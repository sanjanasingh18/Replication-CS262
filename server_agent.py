import os
import csv
import pandas as pd
import numpy as np
import socket
import math
import time
import uuid
import sys
import io
import hashlib
import datetime
import shutil
import random
import hmac
from _thread import *
from collections import Counter
import threading
from threading import Timer
from run_client import ClientSocket
from action import ClientAction

# create a global variable for our csv backup state file
headers = ["Username", "Logged_in", "Password",
           "Messages", "Timestamp_last_updated"]
ports = [8881, 8882, 8883]

servers = []
all_server_indices = [0, 1, 2]
# set the indices of the servers that can fail (to demo 2-fault tolerant system)
# can alter these to be any 2 values between 0 and 2
failure_indices = [0]
failure_interval = 25.0
failure_detection_time = 7.0
server_comm_message = "server_comm_message"
sophia_host = "dhcp-10-250-69-244.harvard.edu"

class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


class Server:
    # Server object
    def __init__(self, set_port, is_leader=False, set_host=None, sock=None):
        self.port = int(set_port)
        #self.is_leader = is_leader.lower() == "true"

        # create port list for testing purposes
        self.ports = ports

        # set the current leader- when initialized, leader should be the first port
        self.curr_leader = self.ports[0]

        # set host and port attributes
        if set_host is None:
            self.host = sophia_host
        else:
            self.host = set_host

        # keep a count of connected servers to ensure we start sending actions when all servers are connected
        self.connected_servers_count = 0

        # create a variable to store the list of heartbeat actions that we will
        # send to the other servers every heart beat
        self.heartbeat_actions = []

        # create a variable to store the conns of the other servers that connect to this server
        self.other_server_conns = []

        # create a variable to store the sockets to the other servers that this server will connect to
        self.other_server_sockets = []

        # create a variable to store the conns of the clients that connect to this server
        self.client_conns = []

        # create a variable to hold the heart beat actions
        self.heartbeat = None

        # create a variable to store the time interval for the heartbeat actions
        self.heartbeat_interval = 3.0

        # what to send on heartbeat_message if you aren't a leader
        self.heartbeat_message = str(self.port)

        # have a list of failed server ports so the other servers know not to send things to them
        self.failed_server_ports = set()

        # define the other ports that will be used for the other servers
        other_ports = [x for x in self.ports if x != self.port]

        # add a socket to connect to the leader
        if self.port == self.ports[1]:
            self.other_server_sockets.append((socket.socket(
                socket.AF_INET, socket.SOCK_STREAM), self.ports[0]))
        elif self.port == self.ports[2]:
            for port in other_ports:
                self.other_server_sockets.append((socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM), port))
                
        # create an array to store communications from the other servers when they send life updates
        # this array will store communications in the format 
        # [(port1, timestamp), (port2, timestamp), (port3, timestamp)]
        self.server_comms = [(self.ports[0], None),
                             (self.ports[1], None),
                             (self.ports[2], None)]

        # Mutex lock so only one thread can access account_list at a given time
        # Used for multiple clients, also only one thread can modify
        # the dataframe at a given time.
        # Need this to be a Recursive mutex as some subfunctions call on lock on
        # top of a locked function
        self.account_list_lock = threading.RLock()

        # Create a list of accounts for this new server to keep track of clients
        # Format of account_list is [UUID: ClientObject]
        self.account_list = dict()
        self.state_path = "server_state_" + str(self.port - 8880) + ".csv"

        # check if the csv file to store the state as data exists, if not then create the file
        if os.path.isfile(self.state_path):
            self.df = pd.read_csv(self.state_path)
            time_last_updated = self.parse_csv_file()
            print("Server restored from " + time_last_updated + ". :)")

        else:

            # Set up the new file account_list with index username and the columns
            self.df = pd.DataFrame(data=None, columns=headers)

            # make a new row that we will never delete and use to store the time of when this
            # server state was last updated
            self.df.at[0, "Username"] = "last_updated"
            self.df.at[0, "Logged_in"] = False
            self.df.at[0, "Messages"] = []
            self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

            # Save it
            self.df.to_csv(self.state_path, header=True, index=False)
            print("Initializing New Server.")

        if sock is None:
            self.server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock

    # Function to hash our log file to check for server consensus
    def hash_server_file(self, filepath):
        with open(filepath, "rb") as f:
            digest = hashlib.file_digest(f, "sha1")
        return digest.hexdigest()

    # Function to compare the hashes for each server
    def compare_server_hash(self, filepaths):
        hashes = []
        for filepath in filepaths:
            hashes.append(self.hash_server_file(filepath))
        # check if any values are equal to 3+ values for the consensus
        # servers and save that hash in a variable
        data = Counter(hashes)
        correct_hash = data.most_common(1)[0][0]

        return np.where(np.array(hashes) == correct_hash)

    # Function to parse the server data state csv file and add to account_list
    def parse_csv_file(self):
        # Account list is a dictionary [UUID: ClientObject]
        # for row in csv,
        # make client socket object using attributes
        # add to dictionary!

        # lock mutex
        self.account_list_lock.acquire()

        for index, row in self.df.iterrows():
            # create the messages data structure as a list
            messages = []
            processed_messages = row["Messages"].strip('][').split(', ')

            # add each message to the messages list
            if processed_messages != ['']:
                for message in processed_messages:
                    messages.append(message)

            # create a new client socket for each client that needs to be restored
            client_socket = ClientSocket()
            # update the username value in the client socket
            client_socket.setUsername(row["Username"])
            # update the password value for the client socket
            client_socket.setPassword(row["Password"])
            # update the logged in status for the client socket
            client_socket.setLoggedIn(row["Logged_in"])
            # update the messages value for the client socket
            client_socket.setMessages(messages)

            # update messages in Dataframe to be stored correctly
            self.df.at[index, "Messages"] = messages

            self.account_list[row["Username"]] = client_socket

        # create a variable to store the timestamp the CSV file was last updated so we can return it
        csv_timestamp = self.df["Timestamp_last_updated"].values[0]

        # unlock mutex
        self.account_list_lock.release()

        # return the time this server state was last updated so we can print it
        return csv_timestamp

    # Function to parse the server data state csv file when a new server leader is elected
    def update_new_leader_data(self):
        # Account list is a dictionary [UUID: ClientObject]
        # for row in csv,
        # make client socket object using attributes
        # add to dictionary!

        # lock mutex
        self.account_list_lock.acquire()

        for index, row in self.df.iterrows():
            # create the messages data structure as a list
            messages = []
            processed_messages = row["Messages"]
            if isinstance(processed_messages, str):
                processed_messages.strip('][').split(', ')

            # add each message to the messages list
            if processed_messages != ['']:
                for message in processed_messages:
                    messages.append(message)

            # create a new client socket for each client that needs to be restored
            client_socket = ClientSocket()
            # update the username value in the client socket
            client_socket.setUsername(row["Username"])
            # update the password value for the client socket
            client_socket.setPassword(row["Password"])
            # update the logged in status for the client socket
            client_socket.setLoggedIn(row["Logged_in"])
            # update the messages value for the client socket
            client_socket.setMessages(messages)

            # update messages in Dataframe to be stored correctly
            self.df.at[index, "Messages"] = messages

            self.account_list[row["Username"]] = client_socket

        # create a variable to store the timestamp the CSV file was last updated so we can return it
        csv_timestamp = self.df["Timestamp_last_updated"].values[0]

        # unlock mutex
        self.account_list_lock.release()

        # return the time this server state was last updated so we can print it
        return csv_timestamp

    # Returns true if the username exists in the account_list database,
    # false otherwise.

    def is_username_valid(self, recipient_username):
        # lock mutex as we access account_list
        self.account_list_lock.acquire()
        result = recipient_username in self.account_list
        # unlock mutex
        self.account_list_lock.release()
        return result

    # Function to add the message to the recipient's queue

    def add_message_to_queue(self, sender_username, recipient_username, message):
        # queue format is strings of sender_username + "" + message
        message_string = sender_username + message
        # lock mutex
        self.account_list_lock.acquire()

        self.account_list.get(recipient_username).addMessage(message_string)

        # update messages in the dataframe and save it
        username_index = self.df.index[self.df["Username"] == recipient_username].tolist()[
            0]

        # set the current_messages variable to be equal to the messages stored in the client socket
        current_messages = self.account_list.get(
            recipient_username).getMessages()

        # generate a string of current messages to be added to our action object and sent to the other servers
        current_messages_string = current_messages[0]
        for message in current_messages[1:]:
            current_messages_string += "we_like_cs262" + message

        # update the messages value in the username's row in the dataframe
        self.df.at[username_index, "Messages"] = current_messages
        # update the timestamp value in the username's row
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()
        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # create a variable to store the action object that will be used to send this
        # action to the other servers
        client_action = ClientAction(action='sendmsg',
                                     recipient_username=recipient_username,
                                     current_messages=current_messages_string)

        # save the current action object to the list of actions to send out every heart beat
        self.save_client_action(client_action)

        # have to sleep so it saves correctly.
        time.sleep(0.05)
        self.df.to_csv(self.state_path, header=True, index=False)

        # unlock mutex
        self.account_list_lock.release()

    # returns True upon successful message delivery. returns False if it fails.
    def deliver_message(self, sender_username, recipient_username, host, port, conn):
        # If username is invalid, throw error message
        if not self.is_username_valid(recipient_username):
            recipient_not_found = "User not found."
            print(recipient_not_found)
            conn.sendto(recipient_not_found.encode(), (host, port))
            return False

        # query the client for what the message is
        confirmed_found_recipient = "User found. Please enter your message: "
        print(confirmed_found_recipient)
        conn.sendto(confirmed_found_recipient.encode(), (host, port))

        # server will receive what the message the client wants to send is
        message = conn.recv(1024).decode()

        # regardless of client status (logged in or not), add the message to the recipient queue
        self.add_message_to_queue(sender_username, recipient_username, message)

        # print + deliver confirmation
        confirmation_message_sent = "Delivered message '" + \
            message[:50] + " ...' to " + \
            recipient_username + " from " + sender_username
        print(confirmation_message_sent)
        conn.sendto(confirmation_message_sent.encode(), (host, port))
        return True

    # function to create an account/username for a new user
    def create_username(self, host, port, conn):
        # create a variable to store the action object that will be used to send this
        # action to the other servers
        client_action = ClientAction(action='create')

        # save the current action object to the list of actions to send out every heart beat
        self.save_client_action(client_action)

        # server will generate UUID, print UUID, send info to client
        # and then add account information to the dictionary
        username = str(uuid.uuid4())
        print("Unique username generated for client is " + username + ".")
        # set this value in our client action object
        client_action.setClientUsername(username)

        conn.sendto(username.encode(), (host, port))

        # lock mutex
        self.account_list_lock.acquire()

        # add (username: clientSocket object where clientSocket includes log-in status,
        # username, password, and queue of undelivered messages
        self.account_list[username] = ClientSocket()

        # get the username index of the current user that we are looking at
        username_index = len(self.df.index)

        # make a new row where Username = username + append it to dataframe
        self.df.at[username_index, "Username"] = username
        self.df.at[username_index, "Logged_in"] = False
        self.df.at[username_index, "Messages"] = []
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()

        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # save the current action object to the list of actions to send out every heart beat
        self.save_client_action(client_action)

        # save updated CSV with the new username
        self.df.to_csv(self.state_path, header=True, index=False)

        # unlock mutex
        self.account_list_lock.release()

        # client will send back a password + send over confirmation
        client_password = conn.recv(1024).decode()

        # update the password in the object that is being stored in the dictionary
        # lock mutex
        self.account_list_lock.acquire()
        self.account_list.get(username.strip()).setPassword(client_password)

        # update password in the dataframe and save it
        self.df.at[username_index, "Password"] = client_password

        # set this value in our client action object
        client_action.setPassword(client_password)

        # update the logged in variable to be True now that the user is logged in
        self.df.at[username_index, "Logged_in"] = True

        # set the logged in value in the client action object
        client_action.setLoggedIn("true")

        # update the timestamp in the username's row
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()

        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # have to sleep so it saves correctly.
        time.sleep(0.05)

        # save the current action object to the list of actions to send out every heart beat
        self.save_client_action(client_action)

        # save the csv file
        self.df.to_csv(self.state_path, header=True, index=False)

        # unlock mutex
        self.account_list_lock.release()

        # send client confirmation of the password
        message = "Your password is confirmed to be " + client_password
        conn.sendto(message.encode(), (host, port))

        return username

    # send messages to the client that are in the client's message queue
    def send_client_messages(self, client_username, host, port, conn, prefix=''):
        # prefix is appended to the FRONT of messages to be delivered
        # prefix is an optional argument as everything is sent as strings
        # prefix is ONLY used in the login function to send conffirmation

        final_msg = ""
        # note that we hold the mutex in this entire area- if we let go of mutex + reacquire to
        # empty messages we may obtain new messages in that time and then empty messages
        # that have not yet been read

        # lock mutex
        self.account_list_lock.acquire()

        # get available messages
        msgs = self.account_list.get(client_username).getMessages()

        # if there are messages, append them to the final messages
        if msgs:
            str_msgs = ''
            for message in msgs:
                str_msgs += 'we_love_cs262' + message
            final_msg += str_msgs

            # clear all delivered messages as soon as possible to address concurent access
            self.account_list.get(client_username).emptyMessages()

            # empty messages in persistent storage
            # get the index value of the current client username
            username_index = self.df.index[self.df["Username"] == client_username].tolist()[
                0]

            # update the messages value in the username's row
            self.df.at[username_index, "Messages"] = []
            # update the timestamp value in the username's row
            self.df.at[username_index,
                       "Timestamp_last_updated"] = pd.Timestamp.now()

            # update the timestamp value in the global timestamp last saved
            self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

            # create a variable to store the action object that will be used to send this
            # action to the other servers
            client_action = ClientAction(action='msgspls',
                                         client_username=client_username)

            # save the current action object to the list of actions to send out every heart beat
            self.save_client_action(client_action)

            # have to sleep so it saves correctly.
            time.sleep(0.05)
            self.df.to_csv(self.state_path, header=True, index=False)

        else:
            final_msg += "No messages available"
        # unlock mutex
        self.account_list_lock.release()

        # first send over the length of the message
        # SEND prefix + length of final msg- there is only a prefix for login
        len_msg = prefix + str(len(final_msg))
        conn.sendto(len_msg.encode(), (host, port))

        # receive back confirmation from the Client (this is to control info flow)
        conn.recv(1024).decode()

        # then, send over the final message
        conn.sendto(final_msg.encode(), (host, port))

    # function to log in to an account

    def login_account(self, host, port, conn):

        # ask for login and password and then verify if it works
        # receive username from account
        username = conn.recv(1024).decode()

        # send confirmation that username was received
        confirm_received = "Confirming that the username has been received." + username
        conn.sendto(confirm_received.encode(), (host, port))

        password = conn.recv(1024).decode()

        # lock mutex
        self.account_list_lock.acquire()

        # see if username is valid
        if (username.strip() in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()).getPassword():
                # create a variable to hold the username index
                username_index = self.df.index[self.df["Username"] == username.strip()].tolist()[
                    0]

                # updated login value at the username index
                self.df.at[username_index, "Logged_in"] = True

                # when the user attempts a log in, update the timestamp value in the username's row
                self.df.at[username_index,
                           "Timestamp_last_updated"] = pd.Timestamp.now()

                # update the timestamp value in the global timestamp last saved
                self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

                # save updated CSV with the new username
                self.df.to_csv(self.state_path, header=True, index=False)

                # unlock mutex
                self.account_list_lock.release()

                # create a variable to store the action object that will be used to send this
                # action to the other servers
                client_action = ClientAction(
                    action='login', client_username=username.strip(), logged_in='true')

                # save the current action object to the list of actions to send out every heart beat
                self.save_client_action(client_action)

                confirmation = 'You have logged in. Thank you!'
                self.send_client_messages(
                    username.strip(), host, port, conn, confirmation)
                return username.strip()

            else:
                # when the user attempts a log in, update the global timestamp value
                self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

                # save updated CSV with the new username
                self.df.to_csv(self.state_path, header=True, index=False)

                # unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        # see if username is valid- some cases it is concatenated with 'login' before
        elif (username.strip()[5:] in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()[5:]).getPassword():
                # create a variable to hold the username index
                username_index = self.df.index[self.df["Username"] == username.strip()[
                    5:]].tolist()[0]

                # updated login value at the username index
                self.df.at[username_index, "Logged_in"] = True

                # when the user attempts a log in, update the timestamp value in the username's row
                self.df.at[username_index,
                           "Timestamp_last_updated"] = pd.Timestamp.now()

                # update the timestamp value in the global timestamp last saved
                self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

                # save updated CSV with the new username
                self.df.to_csv(self.state_path, header=True, index=False)

                # unlock mutex
                self.account_list_lock.release()

                # create a variable to store the action object that will be used to send this
                # action to the other servers
                client_action = ClientAction(
                    action='login', client_username=username.strip()[5:], logged_in='true')

                # save the current action object to the list of actions to send out every heart beat
                self.save_client_action(client_action)

                confirmation = 'You have logged in. Thank you!'
                self.send_client_messages(
                    username.strip(), host, port, conn, confirmation)
                return username.strip()[5:]
            else:
                # when the user attempts a log in, update the timestamp value in the username's row
                self.df.loc[self.df["Username"] == username.strip(
                )[5:], "Timestamp_last_updated"] = pd.Timestamp.now()

                # update the timestamp value in the global timestamp last saved
                self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

                # save updated CSV with the new username
                self.df.to_csv(self.state_path, header=True, index=False)

                # unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        else:
            # unlock mutex
            self.account_list_lock.release()
            # want to prompt the client to either try again or create account
            print("Account not found.")
            message = 'Error'
            conn.sendto(message.encode(), (host, port))

    # function to delete a client account
    def delete_account(self, username, host, port, conn):
        # You can only delete your account once you are logged in
        # lock mutex
        self.account_list_lock.acquire()
        # check that the username is valid
        if username in self.account_list:
            # delete account and send confirmation
            del self.account_list[username]

            # get the index value of the current client username
            username_index = self.df.index[self.df["Username"] == username].tolist()[
                0]

            # remove the row at the username_index from our dataframe
            self.df.drop(index=username_index, inplace=True)

            # create a variable to store the action object that will be used to send this
            # action to the other servers
            client_action = ClientAction(
                action='delete', client_username=username)

            # save the current action object to the list of actions to send out every heart beat
            self.save_client_action(client_action)

            # Save it
            self.df.to_csv(self.state_path, header=True, index=False)

            print("Successfully deleted client account, remaining accounts: ", self.account_list)
            # unlock mutex
            self.account_list_lock.release()
            message = 'Account successfully deleted.'
            conn.sendto(message.encode(), (host, port))
        else:
            # unlock mutex
            self.account_list_lock.release()
            # want to inform the client that this account doesn't exist so it was already deleted
            message = 'Account already deleted'
            print(message)
            conn.sendto(message.encode(), (host, port))

    # function to list all active (non-deleted) accounts
    # add a return statement so it is easier to Unittest
    def list_accounts(self):
        # lock mutex
        self.account_list_lock.acquire()
        listed_accounts = str(list(self.account_list.keys()))
        # unlock mutex
        self.account_list_lock.release()

        # updated to return the length of the string version of this list
        # as it will be sent over the wire as a string
        return len(listed_accounts), listed_accounts

    # function to handle when a client logs out

    def client_logged_out(self, curr_user):

        print("Updated client log in status")
        # update the logged in value in account lists
        self.account_list[curr_user].setLoggedIn(False)

        # create a variable to hold the username index in our dataframe
        username_index = self.df.index[self.df["Username"] == curr_user.strip()].tolist()[
            0]

        # updated login value at the username index in our dataframe
        self.df.at[username_index, "Logged_in"] = False

        # when the user attempts a log in, update the timestamp value in the username's row
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()

        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # create a variable to store the action object that will be used to send this
        # action to the other servers
        client_action = ClientAction(
            action='logout', client_username=curr_user.strip(), logged_in='false')

        # save the current action object to the list of actions to send out every heart beat
        self.save_client_action(client_action)

        # save updated CSV with the new username
        self.df.to_csv(self.state_path, header=True, index=False)

    # function handle different cases when a client connects to the server versus when
    # another server connects to the server
    def server_reroute(self, host, conn, port):
        # receive information from the connection
        data = conn.recv(1024).decode()
        print("Received from server_reroute function", data)
        # if the connection is a server, the data will be sent in the format
        # `{port} + server`
        if data[4:10] == 'server':
            print("Going to server function")
            # the data is sent in the form `{port} + server + `
            # this information gives us the port address, tells us whether it's a server or a client
            # and tells us if it is a leader or not
            server_port = int(data[:4])
            is_server_leader = data[10:].lower() == "true"

            # check if the current server connection we have is the leader server
            if is_server_leader:
                self.curr_leader = server_port

            # run the server to server handling function
            self.server_to_server(conn, server_port)
        else:
            # run the server to client handling function
            print("Going to client function")
            self.server_to_client(host, conn, port)

    # function to save the current state of the client action to a list of actions to
    # send out every heart beat
    def save_client_action(self, action):
        if self.curr_leader == self.port: #self.is_leader:
            # a hearbeat action will be saved in the format
            self.heartbeat_actions.append(action.exportAction())

    # function to generate an actions string from the current action list
    def generate_server_actions_string(self):
        # create a string to hold all the actions so we can send it
        actions_string = ''

        # if there are actions, add them
        if self.heartbeat_actions:
            # for each action in the action list
            for action in self.heartbeat_actions:
                actions_string += action + "we_love_cs262"
        # otherwise send something so the other servers receive an update 
        # so they get a heartbeat 
        else:
            actions_string = "update_me"

        # return the actions string
        return actions_string

    # function to send the heart beat actions to the other connected servers
    def send_heartbeat_actions(self):
        # get the list of server heart beat actions
        actions = self.generate_server_actions_string()

        print("Am I the LEADER?!", str(self.curr_leader == self.port))

        # if the server is a leader, on each heart beat send out the list of heart beat actions
        # to the other non leader servers

        # detect server failure before you send out heartbeat- only send to live servers
        self.detect_server_failure()

        # there may be a leader function in the above function if leader faults

        if self.curr_leader == self.port:
            print("I am sending my heart beat actions:", actions)

            if self.heartbeat_message == server_comm_message:
                actions = self.heartbeat_message

            # for each of the other non leader servers in the server conns connections
            for other_server_conn, other_server_port in self.other_server_conns:
                # check that each server is not in the list of failed servers
                print("Failed servers are", self.failed_server_ports)
                other_server_conn.sendto(
                    actions.encode(), (self.host, other_server_port))
                print("Sent actions: " + actions +
                    " to " + str(other_server_port))

            # for each of the other non leader servers in the server sockets connections
            for other_server_socket, other_server_port in self.other_server_sockets:
                print("Failed servers are", self.failed_server_ports)
                other_server_socket.sendto(
                    actions.encode(), (self.host, other_server_port))
                print("Sent actions: " + actions +
                    " to " + str(other_server_port))

            # clear the heart beat actions list
            self.heartbeat_actions = []
            
        # non leader servers send out updates to the other servers that have not failed
        else:
            # send out the heartbeat_message of the curent server to update the other servers
            server_update = self.heartbeat_message #str(self.port)
            # send life update to each of the other servers in the conn connections
            for other_server_conn, other_server_port in self.other_server_conns:
                print("Failed servers are", self.failed_server_ports)
                other_server_conn.sendto(
                    server_update.encode(), (self.host, other_server_port))
                print("Sent life update to " + str(other_server_port))

            # send life update to each of the other servers in the server connections
            for other_server_socket, other_server_port in self.other_server_sockets:
                print("Failed servers are", self.failed_server_ports)
                other_server_socket.sendto(
                    server_update.encode(), (self.host, other_server_port))
                print("Sent life update to " + str(other_server_port))

    # function for non leader servers to receive actions from leader and process the actions
    def receive_heartbeat_action(self):
        while True:
            # print("In receive heartbeat")
            # receive for each of the servers in the conns list
            for server_conn, port in self.other_server_conns:
                # decode the message we have received from a server
                server_message = server_conn.recv(2048).decode()
                print("Received", server_message, 'from server')

                # check if server down
                if server_comm_message in server_message:
                    # do not update server_comms
                    print("ServerComm", port)
                    self.failed_server_ports.add(port)

                # if we receive a server reboot update
                elif server_message[:13] == "server_reboot":
                    self.server_comms[self.ports.index(port)] = (port, datetime.datetime.now())
                    #print("post conn update", port, self.server_comms)
                    # remove the rebooted server from the list of failed servers
                    if port in self.failed_server_ports:
                        self.failed_server_ports.remove(port)
                    print("Failed servers after reboot", self.failed_server_ports)
                    print("Server", port, "has been rebooted.")
                # otherwise we received an action item from the server
                elif server_message != "":
                # else 
                    self.server_comms[self.ports.index(port)] = (port, datetime.datetime.now())
                    #print("post conn update", port, self.server_comms)

                    print("Received actions: " +
                        server_message + " from " + str(port))

                    # once we have recieved the list of action from the leader, parse the actions list
                    self.parse_leader_actions(server_message)

            # receive from each of the servers in the server_sockets connection list
            for server_socket, port in self.other_server_sockets:
                # decode the message we have received from a server 
                server_message = server_socket.recv(2048).decode()
                print("Received", server_message, 'from server')
                
                # check if server down
                if server_comm_message in server_message:
                    # do not update server_comms
                    print("ServerComm", port)
                    self.failed_server_ports.add(port)


                # if we receive a server reboot update
                elif server_message[:13] == "server_reboot":
                    self.server_comms[self.ports.index(port)] = (port, datetime.datetime.now())

                    # remove the rebooted server from the list of failed servers
                    if port in self.failed_server_ports:
                        self.failed_server_ports.remove(port)
                    print("Failed servers are", self.failed_server_ports)
                    print("Server", port, "has been rebooted.")
                # otherwise we received an action item from the server
                # else:
                elif server_message != "":
                    # automatically update the time stamp for the leader in server_comms when we receive heart beat actions
                    self.server_comms[self.ports.index(port)] = (port, datetime.datetime.now())
                    
                    print("Received actions: " +
                        server_message + " from " + str(port))
                    

                    # once we have recieved the list of action from the leader, parse the actions list
                    self.parse_leader_actions(server_message)

    # function to handle parsing and saving the client login action
    def save_login_action(self, server_action):
        # get the username of the client that logged in
        username = server_action[1]
        # get the log in status of user
        logged_in = server_action[3].lower() == "true"

        # create a variable to hold the username index
        username_index = self.df.index[self.df["Username"] == username.strip()].tolist()[
            0]

        # updated login value at the username index
        self.df.at[username_index, "Logged_in"] = logged_in

        # when the user attempts a log in, update the timestamp value in the username's row
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()

        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # save updated CSV with the new username
        self.df.to_csv(self.state_path, header=True, index=False)

        print("Succesfully updated login status to logged in")

    # function to handle parsing and saving the create client action
    def save_create_action(self, server_action):
        if server_action[1]:
            # get the username for the new client
            username = server_action[1]
            password = server_action[2]
            logged_in = server_action[3] == "true"

            # if this username has already been added to our dataframe
            if self.df.index[self.df["Username"] == username.strip()].tolist() != []:
                # get the index for the username that exists already
                username_index = self.df.index[self.df["Username"] == username.strip()].tolist()[
                    0]
                self.df.at[username_index, "Password"] = password
                # update the user to be logged in
                self.df.at[username_index, "Logged_in"] = logged_in
                # update the timestamp at that index
                self.df.at[username_index,
                           "Timestamp_last_updated"] = pd.Timestamp.now()

            # if the username has not yet been added to our dataframe
            else:
                # make an index for the new username at the end of the dataframe
                username_index = len(self.df.index)

                # make a new row where Username = username + append it to dataframe
                self.df.at[username_index, "Username"] = username
                self.df.at[username_index, "Password"] = password
                # update the user to be logged in
                self.df.at[username_index, "Logged_in"] = logged_in
                self.df.at[username_index, "Messages"] = []
                # update the timestamp at that index
                self.df.at[username_index,
                           "Timestamp_last_updated"] = pd.Timestamp.now()

        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # save updated CSV with the new username
        self.df.to_csv(self.state_path, header=True, index=False)
        print("it saved? to the CSV file ??")


    # function to handle parsing and saving the logout client action
    def save_logout_action(self, server_action):
        # get the username of the client that logged in
        username = server_action[1]
        # get the log in status of user
        logged_in = server_action[3].lower() == "true"

        # create a variable to hold the username index
        username_index = self.df.index[self.df["Username"] == username.strip()].tolist()[
            0]

        # updated login value at the username index
        self.df.at[username_index, "Logged_in"] = logged_in

        # when the user attempts a log in, update the timestamp value in the username's row
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()

        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # save updated CSV with the new username
        self.df.to_csv(self.state_path, header=True, index=False)

        print("succesfully updated login status to logged out.")

    # function to handle parsing and saving the delete client action
    def save_delete_action(self, server_action):
        # get the username of the client that logged in
        username = server_action[1]

        # get the index value of the current client username
        username_index = self.df.index[self.df["Username"] == username].tolist()[
            0]

        # remove the row at the username_index from our dataframe
        self.df.drop(index=username_index, inplace=True)

        # Save it to dataframe
        self.df.to_csv(self.state_path, header=True, index=False)

        print("successfully deleted client account:", username)

    # function to handle parsing and saving the send message to another user client action
    def save_sendmsg_action(self, server_action):
        # get the username of the recipient
        recipient_username = server_action[4]

        # update messages in the dataframe and save it
        username_index = self.df.index[self.df["Username"] == recipient_username].tolist()[
            0]

        # set the current_messages variable to be equal to the messages stored in the client socket
        current_messages = server_action[5].split("we_like_cs262")

        # update the messages value in the username's row in the dataframe
        self.df.at[username_index, "Messages"] = current_messages
        # update the timestamp value in the username's row
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()
        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # have to sleep so it saves correctly.
        time.sleep(0.05)
        self.df.to_csv(self.state_path, header=True, index=False)

    # function to handle parsing and saving the get messages client action
    def save_msgspls_action(self, server_action):
        # get the username of the client
        client_username = server_action[1]

        # empty messages in persistent storage
        # get the index value of the current client username
        username_index = self.df.index[self.df["Username"] == client_username].tolist()[
            0]

        # update the messages value in the username's row
        self.df.at[username_index, "Messages"] = []
        # update the timestamp value in the username's row
        self.df.at[username_index,
                   "Timestamp_last_updated"] = pd.Timestamp.now()

        # update the timestamp value in the global timestamp last saved
        self.df.at[0, "Timestamp_last_updated"] = pd.Timestamp.now()

        # have to sleep so it saves correctly.
        time.sleep(0.05)
        self.df.to_csv(self.state_path, header=True, index=False)

    # function to parse the list of actions we receive from the leader server
    def parse_leader_actions(self, actions):
        action_log = actions.split("we_love_cs262")
        # [[create], [create, username], [create, username, password], [exit]]
        for action in action_log:
            # server action will be in the format
            # ["action", "client_username", "password", "recipient_username", "message", "available_messages"]
            server_action = action.split("we_hate_cs262")

            # if the action that the client took was "login"
            if server_action[0] == "login":
                self.save_login_action(server_action)

            # if the action that the client took was "create"
            elif server_action[0] == "create":
                self.save_create_action(server_action)

            # if the action that the client took was "delete"
            elif server_action[0] == "delete":
                self.save_delete_action(server_action)

            # if the action that the client took was "send message"
            elif server_action[0] == "sendmsg":
                self.save_sendmsg_action(server_action)

            # if the action that the client took was "get messages"
            elif server_action[0] == "msgspls":
                self.save_msgspls_action(server_action)

            # if the action that the client took was "logout"
            elif server_action[0] == "logout":
                self.save_logout_action(server_action)

    # function to handle server to server communications 
    def server_to_server(self, conn, other_server_port):
        self.other_server_conns.append((conn, other_server_port))
        self.ports.index(other_server_port)
        print("Server" + str(other_server_port) + "connected (wowww!)")

    # function that does the heavy lifting of server, client communication
    def server_to_client(self, host, conn, port):
        
        self.client_conns.append((conn, port))

        print("Client connected, sending leader info rn...")

        # send to client who the curr_leader is 
        curr_leader_str = "CurrLeader" + str(self.curr_leader)
        conn.sendto(curr_leader_str.encode(), (host, port))

        print("Sent to client!")

        # keep track of the current client on this thread
        curr_user = ''

        # while statement only breaks when client deletes their account
        # or if client exits on their side (closes connection)
        while True:
            # receive from client
            data = conn.recv(1024).decode()

            # check if connection closed- if so, close thread
            if not data:
                # close thread
                return

            print('Message from client: ' + data)

            # check if data equals 'login'- take substring as we send login + username to server
            if data.lower().strip()[:5] == 'login':
                curr_user = self.login_account(host, port, conn)

            # check if data equals 'create'
            elif data.lower().strip()[:6] == 'create':
                curr_user = self.create_username(host, port, conn)

            # check if data equals 'delete'- take substring as we send delete + username to server
            elif data.lower().strip()[:6] == 'delete':
                # data parsing works correctly
                # print(data, data.lower().strip(), data.lower().strip()[6:])
                # client username, host, port, conn
                self.delete_account(data.lower()[6:], host, port, conn)
                return

            # check if client request to send a message
            elif data.lower().strip()[:7] == 'sendmsg':
                # data parsing works correctly
                # client username, recipient username, host, port, conn
                self.deliver_message(data.lower().strip()[7:43], data.lower()[
                                     44:], host, port, conn)

            # check if client request is to list all accounts
            elif data.lower().strip()[:9] == 'listaccts':
                len_list, list_of_accounts = self.list_accounts()
                # send length of the list accounts function to be sent
                conn.sendto(str(len_list).encode(), (host, port))
                # receive confirmation from the Client it is ready for the
                # list of accts
                conn.recv(1024).decode()
                # send the list of accounts
                conn.sendto(list_of_accounts.encode(), (host, port))

            # check if client request is to get available messages
            elif data[:8] == "msgspls!":
                self.send_client_messages(curr_user, host, port, conn)

            # check if the client is logging out with our secret log out code
            elif data == "~\|/~<3exit":
                self.client_logged_out(curr_user)

    # function to establish connections between the servers

    def connect_to_other_servers(self):
        # construct the message to send to the other servers to indicate that we are a server connection
        message = str(self.port) + "server" + str(self.curr_leader == self.port)
        if self.port == self.ports[1]:
            self.other_server_sockets[0][0].connect((self.host, self.ports[0]))
            self.other_server_sockets[0][0].sendto(
                message.encode(), (self.host, self.ports[0]))

        elif self.port == self.ports[2]:
            self.other_server_sockets[0][0].connect((self.host, self.ports[0]))
            self.other_server_sockets[0][0].sendto(
                message.encode(), (self.host, self.ports[0]))

            self.other_server_sockets[1][0].connect((self.host, self.ports[1]))
            self.other_server_sockets[1][0].sendto(
                message.encode(), (self.host, self.ports[1]))


    # function to detect server failure based on timestamps
    def detect_server_failure(self):
        # first check if the leader has failed, then update failure list
        if self.curr_leader in self.failed_server_ports:
            print("Electing a new leader...")
            self.elect_new_server_leader()

        cur_time = datetime.datetime.now()
        print("self.server_comms:", self.server_comms)
        for port_val, most_recent_heartbeat_time in self.server_comms:
            if most_recent_heartbeat_time:
                failure_bound = most_recent_heartbeat_time + datetime.timedelta(seconds=failure_detection_time)
                print('failure time, cur time, is cur time>fail time?', failure_bound, cur_time, cur_time > failure_bound)
                if cur_time > failure_bound:
                    # then server has failed:
                    self.failed_server_ports.add(port_val)
                    print("Server with port #", port_val, "has failed")

                    # check if it is the leader server who failed- if so, carry
                    # out a leader election
                    if port_val == self.curr_leader:
                        print("Electing a new leader...")
                        self.elect_new_server_leader()


    # function to elect a new server leader
    def elect_new_server_leader(self):
        # if our current leader server has failed, want to carry out election
        past_leader = self.curr_leader
        if self.curr_leader in self.failed_server_ports:
            # elect a new leader server- do it by the lowest port # 
            # possible- smallest port not failed
            if self.ports[0] not in self.failed_server_ports:
                self.curr_leader = self.ports[0]
            elif self.ports[1] not in self.failed_server_ports:
                self.curr_leader = self.ports[1]
            # conclude that the third server must be functioning- a 2F tolerant system
            else: 
                self.curr_leader = self.ports[2]

        # if you are the new leader, parse the csv file so you are up to date
        if past_leader != self.curr_leader:
            if self.curr_leader == self.port:
                # parse the csv file
                self.update_new_leader_data()
                time.sleep(0.2)
            
                # if you there is a new server leader, inform all clients!
                message = "nEwLeAdEr" + str(self.curr_leader)
                for client_conn, client_port in self.client_conns:
                    client_conn.sendto(
                        message.encode(), (self.host, client_port))
                
        print("!! Introducing the new server...", self.curr_leader)


    # function to mimic server failure
    # makes the server sleep for a certain amount of time
    def start_server_failure(self):

        self.heartbeat_message = server_comm_message
        self.failed_server_ports.add(self.port)

        # make the server sleep for five seconds to simulate server failure
        begin_time = datetime.datetime.now()
        print("This server has failed at", begin_time)
        time.sleep(20)

        # once the sleep time has stopped, we can reboot the server
        self.reboot_server()


    # function to reset the server communication list
    def reset_server_comms(self):
        # when the server communicatons are reset, set each server's time to be None
        for ind, (port, _) in enumerate(self.server_comms):
            self.server_comms[ind] = (port, None)

    
    # function to reboot the server
    def reboot_server(self):
        # reboot the server to start sending heartbeat actions again
        self.send_server_reboot_message()

        # set the rebooted server's heartbeat message to be its port
        self.heartbeat_message = str(self.port)

        # remove the rebooted server from the list of failed server
        self.failed_server_ports.remove(self.port)

        # reset the timestamp communications on the rebooted server
        self.reset_server_comms()

        # copy over the leader server's file cotents to the rebooted server
        self.copy_leader_server_csv()

        print("Successfully rebooted this server...")


    # function to make a copy of the leader's CSV file when a failed server is rebooted
    def copy_leader_server_csv(self):
        # use shutil to make a copy of the CSV file
        shutil.copyfile("server_state_" + str(self.curr_leader - 8880) + ".csv", "server_state_" + str(self.port - 8880) + ".csv")


    # function to tell the other servers that this server has been rebooted
    def send_server_reboot_message(self):
        # variable to store the reboot message in the format "server_reboot" + "{port_number}"
        reboot_message = "server_reboot" + str(self.port)

        # send life update to each of the other servers in the conn connections
        for other_server_conn, other_server_port in self.other_server_conns:
            # check that each server is not in the list of failed servers
            # if other_server_port not in self.failed_server_ports:
            # send over a life update
            other_server_conn.sendto(
                reboot_message.encode(), (self.host, other_server_port))
            print("Sent server reboot update to " + str(other_server_port))

        # send life update to each of the other servers in the server connections
        for other_server_socket, other_server_port in self.other_server_sockets:
            # check that each server is not in the list of failed servers
            # if other_server_port not in self.failed_server_ports:
            # send over a life update
            other_server_socket.sendto(
                reboot_message.encode(), (self.host, other_server_port))
            print("Sent server reboot update to " + str(other_server_port))

    def start_heartbeat(self):
        # set up the send heartbeat function if you are a leader and sufficient servers have connected
        self.heartbeat = RepeatingTimer(self.heartbeat_interval, self.send_heartbeat_actions)
        self.heartbeat.start()


    # this program sets up the server + creates new threads for clients
    def initialize_server(self):
        host = self.host
        port = self.port
        self.server.bind((host, port))
        self.server.listen()
        print('Server is active')
        # connect to the other servers
        self.connect_to_other_servers()
        print('Server is connected to other servers')


    def run_server_program(self):
        host = self.host
        port = self.port

        # set up the send heartbeat function if you are a leader and sufficient servers have connected
        self.start_heartbeat()


        # set up the receive heartbeat function if you are a follower
        receive_heartbeat = threading.Thread(target=self.receive_heartbeat_action)

        # start the thread
        receive_heartbeat.start()

        # if this server has an index which is 'allowed to fail' (system is 2 fault-tolerant
        # so we have at most 2 servers failing), then have it fail.
        index_of_self = self.ports.index(self.port)
        if index_of_self in failure_indices:
            # failure_interval = self.heartbeat_interval * random.uniform(1.0, 15.0)
            print("This Server will fail in " + str(failure_interval) + " seconds.")

            # set up the failure function to make the server stop responding to mimic failure
            # one time timer (not repeated) as you will run 'run_server_program' to reboot server.
            server_failure = Timer(failure_interval, self.start_server_failure)
            server_failure.start()

        # while True, listen!
        while True:

            conn, addr = self.server.accept()

            self.connected_servers_count += 1

            print(f'{addr} connected to server.')

            # Start a new thread with this client
            curr_thread = threading.Thread(target=self.server_reroute, args=(host, conn, port))
            
            curr_thread.start()


# create a server object and run the server program!
if __name__ == '__main__':
    # to create a leader server, enter something as a command line arg
    # first command line input = port #, second command line input = is_leader
    # default is_leader value = False; only need second arg if is_leader = True
    server = Server(set_port=sys.argv[1], is_leader=sys.argv[2])
    server.initialize_server()
    server.run_server_program()
