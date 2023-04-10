import os
import socket
import math
import time
import uuid
from _thread import *
from collections import Counter
import threading
from threading import Timer

set_port = 8881
set_host = "dhcp-10-250-69-244.harvard.edu"
# set_host = 'dhcp-10-250-7-238.harvard.edu'
#[uuid: account info ]


class ClientSocket:

  def __init__(self, ports=[8881, 8882, 8883], client=None):
    # We store if the client is currently logged in (to see if they have permission to
    # send/receive messages), their username, password, and 
    # queue of messages that they have received.

    # All of these objects are stored in a dictionary on the server of [username : ClientSocket object]

    self.logged_in = False
    self.username = ''
    self.password = ''
    self.messages = []

    # create three sockets to connec to each of the servers
    self.client_sockets = []
    self.ports = ports

    if client is None:
      for _ in self.ports:
        self.client_sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    # set the port for the leader server socket
    self.leader_server_port = self.ports[0]
    self.port_index = self.ports.index(self.leader_server_port)
    self.client = self.client_sockets[self.port_index]

    # create a variable to store the initial leader consensus
    self.leader_consensus = []

  # basic get/set functions to allow for the server to update these values

  def updateLeaderServer(self, port):
    # set the port connection for the leader server socket
    self.leader_server_port = port
    self.port_index = self.ports.index(self.leader_server_port)
    self.client = self.client_sockets[self.port_index]

  def getStatus(self):
    return self.logged_in

  def setLoggedIn(self, logged_in):
    self.logged_in = logged_in

  def getLoggedIn(self):
    return self.logged_in
  
  def setUsername(self, username):
    self.username = username

  def getUsername(self):
    return self.username

  def getPassword(self):
    return self.password

  def setPassword(self, password):
    self.password = password

  def getMessages(self):
    return self.messages

  def emptyMessages(self):
    self.messages = []

  def addMessage(self, message_string):
    self.messages.append(message_string)

  def setMessages(self, messages):
    self.messages = messages

  # TODO give server acces to client's login
  # state when we do transfer power between servers


  # Function to create a new account
  def create_client_username(self, client_message, host, pwd_client=""):
    # message contains 'create'- send this to the server
    # so the server runs the create function

    self.client.sendto(client_message.encode(), (host, self.leader_server_port))

    # server will send back a username (UUID)
    data = self.client.recv(1024).decode()

    # check if the leader server has changed
    if self.check_server_leader(data):
      print("Internal error. You will be given new login credentials.")
      # run the function again
      self.create_client_username(client_message, host)
      return

    # Update ClientSocket object username and log in fields
    self.username = data
    self.logged_in = True
    print('Your unique username is '  + data)

    if pwd_client == "":
      # Add a password input
      pwd_client = input('Enter password: ')

      # What if the users do not enter a password? or one that is too long?
      while len(pwd_client) < 1 or len(pwd_client) > 950:
        print("Error: password is required to be between 1 and 950 characters")
        pwd_client = input('Enter password: ')

    # Update the password in the client side
    self.password = pwd_client

    # Inform the server of the password
    self.client.sendto((pwd_client).encode(), (host, self.leader_server_port))

    # The server will confirm the password
    confirmation_from_server = self.client.recv(1024).decode()

    # check if the leader server has changed
    if self.check_server_leader(confirmation_from_server):
      print("Internal error. You will be given new login credentials.")
      # run the function again
      self.create_client_username(client_message, host)
      return

    print(confirmation_from_server)
    return self.getUsername()

  
  # helper function to parse messages as everything is sent as strings
  def parse_live_message(self, message):
    # message format is senderUUID+message
    # UUID is 36 characters total (fixed length)
    # return is of the format (sender UUID, message)
    return (message[:36], message[36:])

  # function to print all available messages
  def deliver_available_msgs(self, available_msgs):
    # want to receive all undelivered messages
    for received_msg in available_msgs:
      # get Messages() has 
      sender_username, msg = self.parse_live_message(received_msg)
      print("Message from " + sender_username + ": " + msg)


  # Function to login to a client account
  def login_client_account(self, client_message, host, usrname_input="", pwd_input=""):

    # ensure that the server knows that it is the login function
    # message says 'login'
    self.client.sendto(client_message.encode(), (host, self.leader_server_port))

    # ensure nonempty username
    while len(usrname_input) < 1:
      # client will enter a username
      usrname_input = input("""
      Please enter your username to log in: 
      """)

    # send over the username to the server
    self.client.sendto(usrname_input.encode(), (host, self.leader_server_port))

    # will receive back confirmation that username was sent successfully
    data = self.client.recv(1024).decode()
    print("FROM SEREVR", data)

    # check if the leader server has changed
    if self.check_server_leader(data):
      print("Internal error. Please input your username again.")
      # run the function again
      self.login_client_account(client_message, host, usrname_input="", pwd_input="")
      return

    # ensure nonempty password
    while len(pwd_input) < 1:
      # client will enter a password
      pwd_input = input("""
      Please enter your password to log in: 
      """)

    # in the loop, send the password to the server
    self.client.sendto(pwd_input.encode(), (host, self.leader_server_port))

    # server will send back feedback on whether this was a valid login or not
    data = self.client.recv(1024).decode()

    # check if the leader server has changed
    if self.check_server_leader(data):
      print("Internal error. You will be reprompted to log in.")
      # run the function again
      self.login_client_account(client_message, host, usrname_input="", pwd_input="")

    # stay in for loop until you 
    while data[:30] != 'You have logged in. Thank you!':
      
      # allow them to create an account, exit, or try to log in again
      message = input("""We were unable to find an account associated with that username and password combination.
      Please type either 'create' to create a new account,
      'exit' to close the server connection/log out, 
      or type 'login' to attempt to log in again. If you do not 
      enter any of these options, you will be instructed to log in.
      """)

      # exit- close the connection
      if message.lower().strip() == 'exit':
        # send a message to server to indicate this user is logging out
        self.client.sendto("~\|/~<3exit".encode(), (host, self.leader_server_port))

        print(f'Connection closed.')
        self.logged_in = False
        self.client.close()
        break

      # create new account- reroute to that function
      elif message.lower().strip() == 'create':
        self.create_client_username(message, host)
        break

      else: 
        # requery the client to restart login process
        inform_status = 'login'
        self.client.sendto(inform_status.encode(), (host, self.leader_server_port))

        usrname_input = input("""
        Please enter your username to log in: 
        """)

        # ensure nonempty username
        while len(usrname_input ) < 1:
          usrname_input = input("""
          Please enter your username to log in: 
          """)

        # send over the username to the server
        self.client.sendto(usrname_input.encode(), (host, self.leader_server_port))

        # will receive back confirmation that username was sent successfully
        data = self.client.recv(1024).decode()

        # check if the leader server has changed
        if self.check_server_leader(data):
          print("Internal error. Please input your username again.")
          # run the function again
          self.login_client_account(client_message, host, usrname_input="", pwd_input="")
          return

        pwd_input = input("""
        Please enter your password to log in: 
        """)

        while len(pwd_input) < 1:
          # client will enter a password
          pwd_input = input("""
          Please enter your password to log in: 
          """)
          
        # in the loop, send the password to the server
        self.client.sendto(pwd_input.encode(), (host, self.leader_server_port))

        # server will send back feedback on whether this was a valid login or not
        data = self.client.recv(1024).decode()

        # check if the leader server has changed
        if self.check_server_leader(data):
          print("Internal error. You will be reprompted to log in.")
          # run the function again
          self.login_client_account(client_message, host, usrname_input="", pwd_input="")
          return
    
    # NOW THIS WILL INSTEAD BE the confirmation + str length
    # can exit while loop on success (logged in) or if the loop breaks (with create/exit)
    if data[:30] == 'You have logged in. Thank you!':
      # only if logged in, update the variables
      len_msgs = int(data[30:])

      confirmation_msg = "ok"
      self.client.sendto(confirmation_msg.encode(), (host, self.leader_server_port))

      # retrieve all messages (of the length necessary)

      data = self.client.recv(len_msgs).decode()

      # check if the leader server has changed
      if self.check_server_leader(data):
        # run the function again
        self.get_client_messages(host)
        return

      print("Successfully logged in.")
      self.logged_in = True
      self.username = usrname_input

      if data != 'No messages available':
          available_msgs = data.split('we_love_cs262')[1:]
          self.deliver_available_msgs(available_msgs)
      
    return self.getUsername()
  
  # function to have a client exit
  def client_exit(self, host):
    # send a message to server to indicate this user is logging out
    self.client.sendto("~\|/~<3exit".encode(), (host, self.leader_server_port))

    print(f'Connection closed.')
    self.client.close()
    self.logged_in = False
    return True

  # function to delete the client account
  def delete_client_account(self, host):

    # send a message that is 'delete' followed by the username to be parsed by the other side
    # we do not have a confirmation to delete as it takes effort to type 'delete' so it is difficult
    # to happen by accident

    message = "delete" + str(self.username)
    self.client.sendto(message.encode(), (host, self.leader_server_port))
    
    # server sends back status of whether account was successfully deleted
    data = self.client.recv(1024).decode()

    # check if the leader server has changed
    if self.check_server_leader(data):
      self.delete_client_account(host)
      return

    if data == 'Account successfully deleted.':
      self.logged_in = False
      print("Successfully deleted account.")
    else:
      self.logged_in = False
      print("Account already deleted")

    return True


  def check_server_leader(self, message):
    # check if the server is telling us that we have a new leader
    if message[:9] == "nEwLeAdEr":
      # get the port and port index of the new leader and
      # set the client to communicate to the new server
      print("Updating the leader...")
      proposed_leader_port = int(message[9:])
      if self.leader_server_port != proposed_leader_port:
        self.updateLeaderServer(proposed_leader_port)

        # decode the data that is sent back from the server
        self.client.recv(1024).decode()
        # have the function return true
        return True
    
    # return False otherwise
    return False


  # functon to get client messages from the server at any time
  def get_client_messages(self, host):
    # check remaining msgs
    message = 'msgspls!'

    # inform server that you want to get new messages
    self.client.sendto(message.encode(), (host, self.leader_server_port))

    # server will send back the length of messages
    len_msgs = self.client.recv(1024).decode()

    # check if the leader server has changed
    if self.check_server_leader(len_msgs):
      # inform server that you want to get new messages again
      self.get_client_messages(host)
      return

    # send message to control info flow (ensure you are ready to decode msg)
    message = 'ok'
    self.client.sendto(message.encode(), (host, self.leader_server_port))

    # server will send back messages of proper length
    if len_msgs == "":
      len_msgs = 1024
    data = self.client.recv(int(len_msgs)).decode()

    # check if the leader server has changed
    if self.check_server_leader(data):
      self.get_client_messages(host)
      return
    
    if data != 'No messages available':
      available_msgs = data.split('we_love_cs262')[1:]
      self.deliver_available_msgs(available_msgs)


  # function to list all accounts on the server
  def list_server_accounts(self, client_message, host):
    # tell the server we want to list accounts
    self.client.sendto(client_message.encode(), (host, self.leader_server_port))
    # will receive from server the length of the account_list
    len_list = self.client.recv(1024).decode()

    # check if the leader server has changed
    if self.check_server_leader(len_list):
      self.list_server_accounts(client_message, host)
      return

    # send confirmation to control input flow
    message = 'Ok'
    self.client.sendto(message.encode(), (host, self.leader_server_port))

    # Receive the message data- decode the correct length
    data = self.client.recv(int(len_list)).decode()

    # check if the leader server has changed
    if self.check_server_leader(data):
      self.list_server_accounts(client_message, host)
      return
    
    print('Usernames: ' + data)

  # function to send a message to another client
  def send_message(self, client_message, host):
    # tell the server we want to send a message to a recipient
    self.client.sendto(('sendmsg' + self.getUsername() + "_" + client_message).encode(), (host, self.leader_server_port))
    data = self.client.recv(1024).decode()

    # check if the leader server has changed
    if self.check_server_leader(data):
      self.send_message(client_message, host)
      return

    # if username is found, server will return 'User found. What is your message: '
    if data == "User found. Please enter your message: ":
      message = input(data)
      while message == "":
        message = input("Please enter a non-empty message to send: ")
      self.client.sendto(message.encode(), (host, self.leader_server_port))
      # receive confirmation from the server that it was delivered
      data = self.client.recv(1024).decode()

      # check if the leader server has changed
      if self.check_server_leader(data):
        print("Internal error. Please re-enter your message.")
        self.send_message(client_message, host)
        return
      
    # print output of the server- either that it was successfully sent or that the user was not found.
    print('Message from server: ' + data)


  # this is the main client program that we run- it calls on all subfunctions
  def client_program(self):
    host = set_host

    for ind, port in enumerate(self.ports):
      # connect to each of the three servers
      print("Currently connecting to server port:", port)
      self.client_sockets[ind].connect((host, port))
      # tell all the servers that we are a client
      self.client_sockets[ind].sendto("client".encode(), (host, port))
      # will receive back who the curr leader is
      curr_leader_str = self.client_sockets[ind].recv(1024).decode()
      self.leader_consensus.append(int(curr_leader_str[10:]))

    leader_server_consensus = Counter(self.leader_consensus).most_common(1)[0][0]
    self.updateLeaderServer(leader_server_consensus)
    
    # for ind, port in enumerate(self.ports):
    #   if ind>0:
    #     # set up threads for other files
    #     new_thread = threading.Thread(target=client_logic, args=(port))

    self.client_logic(self.leader_server_port)

    # handle initial information flow- either will login or create a new account
    # You need to either log in or create an account first

  def client_logic(self, port):
    host = set_host
    while not self.logged_in:
      # handle initial information flow- either will login or create a new account
      message = input("""
      Welcome!
      Type 'login' to log into your account.
      Type 'create' to create a new account.
      Type 'exit' to disconnect from server/log out.
      """)

      # login function
      if message.lower().strip()[:5] == 'login':
        self.login_client_account(message, host)
        break

      # create function
      elif message.lower().strip() == 'create':
        self.create_client_username(message, host)
    
      # exit function- may want to exit early
      elif message.lower().strip() == 'exit':
        # send a message to server to indicate this user is logging out
        self.client.sendto("~\|/~<3exit".encode(), (host, self.leader_server_port))

        print(f'Connection closed.')
        self.client.close()
        self.logged_in = False
        break
      
      # if it is none of these key words, it will re query until you enter 'login' or 'create' or 'exit'

    # can only enter loop if you are logged in
    if self.logged_in:

      message = input("""
      To send a message, enter the recipient username, 
      'listaccts' to list all active usernames, 
      'exit' to leave program, or 
      'delete' to delete your account: 
      """)
      
      # continue until client asks to exit
      while message.strip() != 'exit':
        
        # delete account function
        if message.lower().strip() == 'delete':
          # get the client messages
          self.get_client_messages(host)

          # delete the client
          self.delete_client_account(host)
          break

        # if they ask to create or delete given that you are currently logged in, throw an error
        elif message.lower().strip() == 'create':
          print("Error: you must log out before creating a new account. Type 'exit' to log out.")

        # if they ask to create or delete given that you are currently logged in, throw an error
        elif message.lower().strip() == 'login':
          print("Error: you are currently logged in to an account. Type 'exit' to log out and then log into another account.")

        # list all account usernames
        elif message.lower().strip() == 'listaccts':
          self.list_server_accounts(message.lower().strip(), host)

        # send message otherwise
        else:
          self.send_message(message.lower().strip(), host)


        # get all messages that have been delivered to this client
        self.get_client_messages(host)

        # re query for new client actions
        message = input("""
        To send a message, enter the recipient username, 
        'listaccts' to list all active usernames, 
        'exit' to leave program, 
        'delete' to delete your account,
        or press enter to continue: 
        """)

      # will only exit while loops on 'exit' or 'delete'
      # read undelivered messages for exit
      if message.strip() == 'exit':
        # retrieve messages before exiting
        self.get_client_messages(host)

      # send a message to server to indicate this user is logging out
      self.client.sendto("~\|/~<3exit".encode(), (host, self.leader_server_port))

      print(f'Connection closed.')
      self.client.close()

# program creates a ClientSocket object and runs client_program which
# handles input and directs it to the appropriate function
if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()