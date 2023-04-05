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
import hmac
from _thread import *
from collections import Counter
import threading
from threading import Timer
from run_client import ClientSocket
from action import Action

# create a global variable for our csv backup state file
headers = ["Username", "Logged_in", "Password",
           "Messages", "Timestamp_last_updated"]
ports = [8881, 8882, 8883]
alt_ports = [8887, 8888, 8889]
servers = []
all_server_indices = [0, 1, 2, 3, 4]


class Server:
    # Server object
    def __init__(self, set_port, is_leader=False, set_host=None, sock=None):
        self.port = int(set_port)
        self.is_leader = is_leader

        # create port list for testing purposes
        self.ports = ports

        # set the current leader- when initialized, leader should be the first port
        self.curr_leader = self.ports[0]      

        # set host and port attributes
        if set_host is None:
            self.host = ''
        else:
            self.host = set_host

        # create a variable to store the list of heartbeat actions that we will
        # send to the other servers every heart beat
        self.heartbeat_actions = []

        # create a variable to store the conns of the other servers that connect to this server
        self.other_server_sockets = []

        # define the other ports that will be used for the other servers
        other_ports = [x for x in ports if x != self.port]

        # add a socket to connect to the leader
        if self.port == self.ports[1]:
            self.sockets = []
            self.sockets.append(socket.socket(
                socket.AF_INET, socket.SOCK_STREAM))
        elif self.port == self.ports[2]:
            self.sockets = []
            for _ in other_ports:
                self.sockets.append(socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM))

        # this commented line was to check that you are able to print account_list usernames
        # of different lengths
        # self.account_list['veryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrvvvvvvveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkr'] = ClientSocket()
        # Mutex lock so only one thread can access account_list at a given time
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
        # current_messages = self.df["Messages"].values[username_index]
        current_messages = self.account_list.get(
            recipient_username).getMessages()

        # current_messages.append(message_string)

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
        client_action = Action(action='create')

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
        confirm_received = "Confirming that the username has been received."
        conn.sendto(confirm_received.encode(), (host, port))

        password = conn.recv(1024).decode()

        # TODO login account; add is logged_in support if you log in successfully
        # if server is shut down, are logged in users still logged in or do they get
        # logged out
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
                confirmation = 'You have logged in. Thank you!'
                self.send_client_messages(
                    username.strip(), host, port, conn, confirmation)
                return username.strip()

            else:
                # when the user attempts a log in, update the timestamp value in the username's row
                # create a variable to hold the username index
                username_index = self.df.index[self.df["Username"] == username.strip()].tolist()[
                    0]

                # update the timestamp value in the global timestamp last saved
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

            # Save it
            self.df.to_csv(self.state_path, header=True, index=False)

            print(
                "Successfully deleted client account, remaining accounts: ", self.account_list)
            # unlock mutex
            self.account_list_lock.release()
            message = 'Account successfully deleted.'
            conn.sendto(message.encode(), (host, port))
        else:
            # unlock mutex
            self.account_list_lock.release()
            # want to inform the client that it was unable to delete account
            message = 'Error deleting account'
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


    # function handle different cases when a client connects to the server versus when 
    # another server connects to the server
    def server_reroute(self, host, conn, port):
        # receive information from the connection
        data = conn.recv(1024).decode()

        # if the connection is a server, the data will be sent in the format 
        # `{port} + server`
        if data[4:10] == 'server':
            # the data is sent in the form `{port} + server + `
            # this information gives us the port address, tells us whether it's a server or a client
            # and tells us if it is a leader or not
            server_port = int(data[:4])
            is_server_leader = bool(data[10:])

            # check if the current server connection we have is the leader server
            if is_server_leader: 
                self.curr_leader = server_port

            # run the server to server handling function
            self.server_to_server(host, conn, server_port)
        else:
            # run the server to client handling function
            self.server_to_client(host, conn, port)


    # function to save the current state of the client action to a list of actions to
    # send out every heart beat
    def save_client_action(self, action):
        if self.is_leader:
            # a hearbeat action will be saved in the format
            self.heartbeat_actions.append(action.exportAction())


    # function to send the heart beat actions to the other connected servers
    def send_heartbeat_actions(self):
        # if the server is a leader, on each heart beat send out the list of heart beat actions
        # to the other non leader servers
        if self.is_leader:
            # for each of the other non leader servers
            for other_server_conn, other_server_port in self.other_server_sockets:
                # send every action that has occured in between heartbeats to each other server
                for action in self.heartbeat_actions:
                    other_server_conn.sendto(
                        action.encode(), (self.host, other_server_port))


    # function for non leader servers to receive actions from leader and process the actions
    def receive_heartbeat_action(self):
        # if server is not a leader, it recieves actions from the leader
        if not self.is_leader:
            # get the index of the leader server
            leader_index = self.ports.index(self.curr_leader)
            actions = self.sockets[leader_index].recv(1024).decode()

            # for each servers, only receive actions from the leader server 
            # if self.port == self.ports[0]:
            #     actions = self.sockets[leader_index].recv(1024).decode()
            # elif self.port == self.ports[1]:
            #     actions = self.sockets[leader_index].recv(1024).decode()
            # elif self.port == self.ports[2]:
            #     actions = self.sockets[leader_index].recv(1024).decode()
        
        self.parse_leader_actions(actions)

    def parse_leader_actions(self, actions):
        print("wooo")


    def server_to_server(self, host, conn, other_server_port):
        self.other_server_sockets.append((conn, other_server_port))
        print("a server" + str(other_server_port) + "connected wowwww")

    # function that does the heavy lifting of server, client communication

    def server_to_client(self, host, conn, port):

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

            # check if data equals 'delete'- take substring as we send  delete + username to server
            elif data.lower().strip()[:6] == 'delete':
                # data parsing works correctly
                # print(data, data.lower().strip(), data.lower().strip()[6:])
                # client username, host, port, conn
                self.delete_account(data.lower()[6:], host, port, conn)
                return

            # check if client request to send a message
            elif data.lower().strip()[:7] == 'sendmsg':
                # data parsing works correctly
                # print(data, data.lower().strip()[7:43], data.lower()[44:])
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
                recieved = conn.recv(1024).decode()
                # send the list of accounts
                conn.sendto(list_of_accounts.encode(), (host, port))

            # check if client request is to get available messages
            elif data[:8] == "msgspls!":
                self.send_client_messages(curr_user, host, port, conn)

    # function to establish connections between the servers
    def connect_to_other_servers(self):
        message = str(self.port) + "server" + str(self.is_leader)
        if self.port == self.ports[1]:
            self.sockets[0].connect((self.host, self.ports[0]))
            self.sockets[0].sendto(
                message.encode(), (self.host, self.ports[0]))
            self.other_server_sockets.append(("client_conn", self.ports[0]))
        elif self.port == self.ports[2]:
            self.other_server_sockets.append(("client_conn", self.port))
            self.sockets[0].connect((self.host, self.ports[0]))
            self.sockets[0].sendto(
                message.encode(), (self.host, self.ports[0]))
            self.other_server_sockets.append(("client_conn", self.ports[0]))

            self.sockets[1].connect((self.host, self.ports[1]))
            self.sockets[1].sendto(
                message.encode(), (self.host, self.ports[1]))
            self.other_server_sockets.append(("client_conn", self.ports[1]))

    # this program sets up the server + creates new threads for clients
    def initialize_server(self):
        host = self.host
        port = self.port
        self.server.bind((host, port))
        self.server.listen()
        print('Server is active')

    def run_server_program(self):
        host = self.host
        port = self.port

        self.connect_to_other_servers()
        
        # set up the send heartbeat function if you are a leader
        if self.is_leader:
            t = Timer(30.0, self.send_heartbeat_actions)
            t.start() # after 30 seconds, "hello, world" will be printed
            t.cancel() # cancels execution, this only works before the 30 seconds is elapsed
        
        # set up the receive heartbeat function if you are a follower

        # while True, listen!
        while True:
            conn, addr = self.server.accept()

            print(f'{addr} connected to server.')

            # Start a new thread with this client
            curr_thread = threading.Thread(
                target=self.server_reroute, args=(host, conn, port))

            # curr_thread = threading.Thread(target=self.server_to_client, args=(host, conn, port,))
            curr_thread.start()


# create a server object and run the server program!
if __name__ == '__main__':
    # to create a leader server, enter something as a command line arg
    # first command line input = port #, second command line input = is_leader
    # default is_leader value = False; only need second arg if is_leader = True
    server = Server(set_port=sys.argv[1], is_leader=sys.argv[2])
    server.initialize_server()
    server.run_server_program()
