"""
Configuration (BEFORE RUNNING `python3 test_client.py`)
In a separate terminal run `python3 run_server.py` and wait for 'Server is active'.

Now, run `python3 test_client.py` in another terminal. 

"""

import os
import socket
import math
import time
import uuid
import uuid
import unittest
import pandas as pd
from run_client_test import ClientSocket
from server_agent_test import Server

set_port = 8881
set_host = "dhcp-10-250-69-244.harvard.edu"
expected_password = "hi"
msg_content = "abc"

# https://docs.python.org/2/library/unittest.html from section 25.3.1 

# class TestClientMethods(unittest.TestCase):
#     def setUp(self):
#         self.client_socket = ClientSocket()
#         host = set_host
#         port = set_port

#         self.client_socket.client.connect((host, port))

#     def tearDown(self):
#         self.client_socket.client.close()

#     # testing our create account function
#     def test_create_account(self):
#         # test create- see if the username + password are properly updated
#         print("Testing the CREATE function")
#         # creating the test user client account
#         created_username = self.client_socket.create_client_username("create", set_host, expected_password)
#         self.assertEqual(created_username, self.client_socket.getUsername())
#         self.assertEqual(expected_password, self.client_socket.getPassword())

       
#     # testing our login account function
#     def test_login_account(self):
#         print("Testing the LOGIN function")
#         # test will only pass if you enter the correct password- try it out!
#         # want to exit out of the account to see whether that works
#         # creating the test user client account
#         created_username = self.client_socket.create_client_username("create", set_host, expected_password)
#         print("Username is:", created_username)
#         # log out of the account
#         self.client_socket.client.send('exit'.encode())

#         # log into the account
#         self.client_socket.login_client_account("login", set_host, set_port, usrname_input=created_username, pwd_input=expected_password)
#         self.assertEqual(created_username, self.client_socket.getUsername())

#     # testing logging into an account with an incorrect password
#     # def test_incorrect_login_password(self):
#     #     print('Testing the LOGIN function - incorrect password')
#     #     # test will only pass if you enter an incorrect password- try it out!
#     #     # want to exit out of the account to see whether that works
#     #     # creating the test user client account
#     #     created_username = self.client_socket.create_client_username("create", set_host, expected_password)
#     #     print("Username is:", created_username)
#     #     # log out of the account
#     #     self.client_socket.client.send('exit'.encode())

#     #     # fail the log attempt into the account
#     #     self.client_socket.login_client_account("login", set_host, set_port, usrname_input=created_username, pwd_input="h")
#     #     self.assertEqual(login_status, self.client_socket.getUsername())

#     # testing logging into an account with an incorrect username
#     # def test_incorrect_login_username(self):
#     #     print('Testing the LOGIN function - incorrect username')
#     #     # test will only pass if you enter an incorrect password- try it out!
#     #     # want to exit out of the account to s32ee whether that works
#     #     # creating the test user client account
#     #     created_username = self.client_socket.create_client_username("create", set_host, expected_password)
#     #     print("Username is:", created_username)
#     #     # log out of the account
#     #     self.client_socket.client.send('exit'.encode())

#     #     # fail the log attempt into the account
#     #     self.client_socket.send_login_information("login", set_host, set_port, usrname_input="bogus_username", pwd_input=expected_password)
#     #     self.assertEqual(login_status, False)

#     # testing exiting/logging out from your account
#     def test_exit_account(self):
#         print('Testing the EXIT function')
#         # assert that after we have created an account, we can successfully log out/exit.
#         self.client_socket.create_client_username("create", set_host, expected_password)
#         self.assertEqual(self.client_socket.client_exit(set_host), True)

#     # testing deleting your account
#     def test_delete_account(self):
#         print("Testing the DELETE function")
#         # assert that after we have created an account, it is deleted (returns True)
#         # creating the test user client account
#         self.client_socket.create_client_username("create", set_host, expected_password)
#         self.assertEqual(self.client_socket.delete_client_account(host=set_host), True)
    
#     # testing sending messages yourself
#     def test_send_messages_to_self(self):
#         print("Testing the SEND MESSAGE function to yourself. ")
#         # create a new user
#         sender_username = self.client_socket.create_client_username("create", set_host, expected_password)
#         # send message to yourself
#         confirmation_from_server = self.client_socket.send_message(sender_username, set_host, set_port, msg_content=msg_content)
#         # see if the message was delivered as expected
#         expected_confirmation = "Delivered message '" + msg_content + " ...' to " + sender_username + " from " + sender_username
#         self.assertEqual(confirmation_from_server, expected_confirmation)

#     # testing recieving messages from yourself
#     def test_receive_messages_to_self(self):
#         print("Testing the RECEIVE MESSAGE function to yourself.")
        
#         # create a new test user
#         curr_username = self.client_socket.create_client_username("create", set_host, expected_password)
        
#         # send message to yourself
#         self.client_socket.send_message(curr_username, set_host, set_port, msg_content=msg_content)
        
#         # see if the message is received from the server
#         confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
#         expected_confirmation = "we_love_cs262" + curr_username + "abc"
#         self.assertEqual(confirmation_from_server, expected_confirmation)

#     # testing sending messages to another account
#     def test_send_messages_to_others(self):
#         print("Testing the SEND MESSAGE function to another client.")
#         # creating the test user client account
#         sender_username = self.client_socket.create_client_username("create", set_host, expected_password)
#         time.sleep(1)

#         # make other client
#         other_client = ClientSocket()
#         other_client.client.connect((set_host, set_port))
#         other_username = other_client.create_client_username(set_host, set_port, pwd_client=expected_password)
       
#         # comparing the confirmation from the server with expected confirmation
#         confirmation_from_server = self.client_socket.send_message(other_username, set_host, set_port, msg_content=msg_content)
#         expected_confirmation = "Delivered message '" + msg_content + " ...' to " + other_username + " from " + sender_username
#         self.assertEqual(confirmation_from_server, expected_confirmation)
#         # exit other socket
#         other_client.client_exit()

#     # testing receiving messages from another account
#     def test_receive_messages_from_others(self):
#         print("Testing the RECEIVE MESSAGE function to another client.")
#         # creating the test user client recipient
#         recipient_username = self.client_socket.create_client_username("create", set_host, expected_password)
#         time.sleep(1)

#         # make other client
#         other_client = ClientSocket()
#         other_client.client.connect((set_host, set_port))
#         other_username = other_client.create_client_username(set_host, set_port, pwd_client=expected_password)
#         # send message to recipient
#         other_client.send_message(recipient_username, set_host, set_port, msg_content=msg_content)
#         time.sleep(1)

#         # confirmation you expect to receive from the server
#         confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
#         expected_confirmation = "we_love_cs262" + other_username + "abc"
#         self.assertEqual(confirmation_from_server, expected_confirmation)

#         # exit other socket
#         other_client.client_exit()

#     # testing sending messages to an account that does not exist
#     def test_send_messages_to_nonexistent_user(self):
#         print("Testing the SEND MESSAGE function to a nonexistent client username.")
#         # creating the test user client account to send messages from
#         self.client_socket.create_client_username("create", set_host, expected_password)
#         time.sleep(1)

#         # create nonexistent client username
#         nonexistent_username = "nonexistent_client_username"

#         # expected confirmation from the server
#         confirmation_from_server = self.client_socket.send_message(nonexistent_username, set_host, set_port, msg_content=msg_content)
#         expected_confirmation = "User not found."
#         self.assertEqual(confirmation_from_server, expected_confirmation)

#     # testing receiving messages with no available messages
#     def test_receive_empty_messages(self):
#         print("Testing the RECEIVE MESSAGE function with no available messages.")
#         # creating the test user client account to get messages for
#         self.client_socket.create_client_username("create", set_host, expected_password)
#         time.sleep(1)

#         # confirmation you expect to receive 
#         confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
#         expected_confirmation = "No messages available"
#         self.assertEqual(confirmation_from_server, expected_confirmation)

#     # testing the view all accounts function
#     def test_view_account_list(self):
#         print("Testing the VIEW ACCOUNTS function")
#         # creating the test user
#         self.client_socket.create_client_username("create", set_host, expected_password)
        
#         # getting the list of all accounts 
#         list_of_accounts = self.client_socket.list_accounts("listaccts", set_host, set_port)
        
#         # checking if the test user exists in the account list
#         is_in_account_list = self.client_socket.getUsername() in list_of_accounts
#         self.assertEqual(is_in_account_list, True)

#         '''Tried to have two users at the same time for testing, did not work :('''
#         # sender_username = self.client_socket.create_client_username("create", set_host, set_port)
#         # other_object = ClientSocket()
#         # other_username = other_object.create_client_username("create", set_host, set_port)
#         # confirmation_from_server = self.client_socket.send_message(other_username, set_host, set_port)
#         # # here you will be prompted for the message?
#         # expected_confirmation = "Delivered message '" + "abc" + " ...' to " + other_username + " from " + sender_username
#         # self.assertEqual(confirmation_from_server, expected_confirmation)
#         # other_object.client.close()



class TestServerReplication(unittest.TestCase):
    # create only one instance to avoid multiple instantiations and filled ports
    @classmethod
    def setUpClass(self):
        self.server_instance1 = Server(8881, True)
        self.server_instance2 = Server(8882, False)
        self.server_instance3 = Server(8883, False)

        self.server_instance1.initialize_server()

        self.server_instance2.initialize_server()
        self.server_instance3.initialize_server()


    # teardown function for the tests
    def tearDown(self):
        print("Shutting down ...")


    """ Functions to test server persistence """

    # testing if server successfully reads the CSV file into the dataframe
    def test_server_persistence(self):
        # store the parse csv file confirmation message 
        confirmation = "41:40.6"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # get the parse confirmation after server has processed the dataframe
        self.server_instance1.df = test_dataframe
        parse_confirmation = self.server_instance1.parse_csv_file()

        self.assertEqual(parse_confirmation, confirmation)


    # testing if a previous client username is valid after the dataframe has been read 
    def test_server_persistence_client_username_valid(self):
        # create a test username to check for that exists in the CSV file
        test_username = "a9a00d81-1db4-42ac-bcf1-a05c0000447e"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # get the parse confirmation after server has processed the dataframe
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_exists = self.server_instance1.is_username_valid(test_username)

        self.assertEqual(username_exists, True)


    # testing if a nonexistent client username is valid in the server
    # after the dataframe has been read 
    def test_server_persistence_client_username_not_valid(self):
        # create a test username to check for that exists in the CSV file
        test_username = "some-bogus-username-that-doesnt-exist"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # parse the CSV file and populate the dataframe on the server
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_exists = self.server_instance1.is_username_valid(test_username)

        self.assertEqual(username_exists, False)


    # testing if a nonexistent client username exists in the dataframe
    # after the CSV file has been read 
    def test_server_persistence_client_username_in_dataframe(self):
        # create a test username to check for that exists in the CSV file
        test_username = "a9a00d81-1db4-42ac-bcf1-a05c0000447e"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # parse the CSV file and populate the dataframe on the server
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_index = self.server_instance1.df.index[self.server_instance1.df["Username"] == test_username].tolist()[0]

        self.assertEqual(username_index, 1)


    # # testing if the client's password is still in the dataframe after it is read
    def test_server_persistence_client_password_in_dataframe(self):
        # create a test username to check for that exists in the CSV file
        test_username = "38fb6019-8e96-423c-8b90-1eeaefa50173"

        # create a variable to hold the first test messages
        test_password = "heyoo"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # parse the CSV file and populate the dataframe on the server
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_password = self.server_instance1.account_list.get(test_username.strip()).getPassword()

        self.assertEqual(username_password, test_password)


    # testing if client's available messages are in the dataframe after
    # the CSV file has been parsed
    def test_server_persistence_client_messages_in_dataframe(self):
        # create a test username to check for that exists in the CSV file
        test_username = "12d8719c-6e5b-4538-a92f-80bf4215d34d"

        # create a variable to hold the first test messages
        test_message = "'8291d793-0551-48f4-a39d-7a9f3e191094hiohrgiwogh'"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # parse the CSV file and populate the dataframe on the server
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_messages = self.server_instance1.account_list.get(test_username).getMessages()

        self.assertEqual(username_messages[0], test_message)


    # testing if client's empty available messages are in the dataframe after
    # the CSV file has been parsed
    def test_server_persistence_client_empty_messages_in_dataframe(self):
        # create a test username to check for that exists in the CSV file
        test_username = "38fb6019-8e96-423c-8b90-1eeaefa50173"

        # create a variable to hold the first test messages
        test_message = []

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # parse the CSV file and populate the dataframe on the server
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_messages = self.server_instance1.account_list.get(test_username).getMessages()

        self.assertEqual(username_messages, test_message)


    # testing if a previous client username exists in the server list
    # after the CSV file has been read 
    def test_server_persistence_client_username_in_server(self):
        # create a test username to check for that exists in the CSV file
        test_username = "a9a00d81-1db4-42ac-bcf1-a05c0000447e"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # parse the CSV file and populate the dataframe on the server
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_in_server = test_username in self.server_instance1.account_list

        self.assertEqual(username_in_server, True)


    # testing if a nonexistent client username does not exist in the server list
    # after the CSV file has been read 
    def test_server_persistence_client_username_not_in_server(self):
        # create a test username to check for that exists in the CSV file
        test_username = "some-nonexistent-username"

        # get the CSV file we want to restore from
        csv_file_path = "server_test_persistence.csv"

        # read the CSV file into the dataframe
        test_dataframe = pd.read_csv(csv_file_path)

        # parse the CSV file and populate the dataframe on the server
        self.server_instance1.df = test_dataframe
        self.server_instance1.parse_csv_file()

        # check if the username exists in our server after parsing
        username_in_server = test_username in self.server_instance1.account_list

        self.assertEqual(username_in_server, False)


    """ Functions to test server replication """

    # testing the server replication once all servers have been initilized 
    def test_server_replication_initialization(self):

        # get the server hashes of all the server replication files with three users
        server1_file_hash = self.server_instance1.hash_server_file("server_state_1.csv")
        server2_file_hash = self.server_instance2.hash_server_file("server_state_2.csv")
        server3_file_hash = self.server_instance3.hash_server_file("server_state_3.csv")

        # check if each of the hashes for each server is the same
        server_hash_equality = server1_file_hash == server2_file_hash == server3_file_hash
        self.assertEqual(server_hash_equality, True)


    # testing the server replication after three clients have connected and created accounts
    def test_server_replication_populated_csv(self):

        # get the server hashes of all the server replication files 
        # with three users
        server1_file_hash = self.server_instance1.hash_server_file("test_replication1.csv")
        server2_file_hash = self.server_instance2.hash_server_file("test_replication2.csv")
        server3_file_hash = self.server_instance3.hash_server_file("test_replication3.csv")

        # check if each of the hashes for each server is the same
        server_hash_equality = server1_file_hash == server2_file_hash == server3_file_hash
        self.assertEqual(server_hash_equality, True)


    # testing the server replication after three clients have connected and gotten usernames
    # but not yet fully finished setting up their account with password
    def test_server_replication_client_action(self):

        # get the server hashes of all the server replication files 
        # with three users who are mid 'create' action
        server1_file_hash = self.server_instance1.hash_server_file("test_replication_action1.csv")
        server2_file_hash = self.server_instance2.hash_server_file("test_replication_action2.csv")
        server3_file_hash = self.server_instance3.hash_server_file("test_replication_action3.csv")

        # check if each of the hashes for each server is the same
        server_hash_equality = server1_file_hash == server2_file_hash == server3_file_hash
        self.assertEqual(server_hash_equality, True)


    # testing the server replication on empty CSVs files with no data and 
    # no users present
    def test_server_replication_empty_csv(self):

        # get the server hashes of all the server replication files with three users
        server1_file_hash = self.server_instance1.hash_server_file("test_replication_empty1.csv")
        server2_file_hash = self.server_instance2.hash_server_file("test_replication_empty2.csv")
        server3_file_hash = self.server_instance3.hash_server_file("test_replication_empty3.csv")

        # check if each of the hashes for each server is the same
        server_hash_equality = server1_file_hash == server2_file_hash == server3_file_hash
        self.assertEqual(server_hash_equality, True)


    # testing the server replication CSVs files that do not match and checking
    # that it return False for not replicated
    def test_server_replication_different_csv(self):

        # get the server hashes of all the server replication files with three users
        server1_file_hash = self.server_instance1.hash_server_file("test_replication_different1.csv")
        server2_file_hash = self.server_instance2.hash_server_file("test_replication_different2.csv")
        server3_file_hash = self.server_instance3.hash_server_file("test_replication_different3.csv")

        # check if each of the hashes for each server is the same
        server_hash_equality = server1_file_hash == server2_file_hash == server3_file_hash
        self.assertEqual(server_hash_equality, False)


    # testing the hash comparison function we use to ensure all servers are synced with the leader
    def test_server_synced_replication(self):
        # create a list of filepaths for the CSV files
        filepaths = ["test_replication1.csv", "test_replication2.csv", "test_replication3.csv"]

        # check if each of the hashes for each server CSV is the same
        server_hash_consensus = self.server_instance1.compare_server_hash(filepaths)

        # get the correct hash for the leader server 
        correct_hash = self.server_instance1.hash_server_file(filepaths[0])
        self.assertEqual(correct_hash, self.server_instance1.hash_server_file(server_hash_consensus))
        
    
    # testing the replication comparison function when a server is out of sync with the leader
    def test_server_unsynced_replication(self):
        # create a list of filepaths for the CSV files
        filepaths = ["test_replication1.csv", "test_replication2.csv", "test_replication_different3.csv"]

        # check if each of the hashes for each server CSV is the same
        server_hash_consensus = self.server_instance1.hash_server_file(self.server_instance1.compare_server_hash(filepaths))

        # get the correct hash for the leader server 
        correct_hash = self.server_instance1.hash_server_file(filepaths[2])

        # use a variable to store the comparison boolean
        comparison = correct_hash == server_hash_consensus
        self.assertEqual(comparison, False)


if __name__ == '__main__':
    unittest.main()