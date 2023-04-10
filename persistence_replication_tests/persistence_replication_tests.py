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