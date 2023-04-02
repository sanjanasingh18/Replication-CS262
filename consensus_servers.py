import os
import csv
import pandas as pd
import socket
import math
import time
import uuid
from _thread import *
import threading
from run_client import ClientSocket
from run_server import Server

if __name__ == '__main__':
    hosts = ''
    ports = [8881, 8882, 8883, 8884, 8885]
    alt_ports = [8886, 8887, 8888, 8889, 8890]
    servers = []
    all_server_indices = [0, 1, 2, 3, 4]

    for port in alt_ports:
        new_server = Server(set_host=hosts, set_port=port)
        new_server.initialize_server()
        servers.append(new_server)
    
    leader_index = 0
    leader_server = servers[leader_index]
    leader_server.run_server_program(leader=True)

    # for each program here that isn't a leader, connect to the server
    leader_host = hosts
    leader_port = ports[leader_index]

    non_leaders_indices = [x for x in all_server_indices if x != leader_index]
    for non_leader in non_leaders_indices:
        print("huuijiooh")
        servers[non_leader].connect_to_leader.connect((leader_host, leader_port))


    # servers talk to each other where main leader server receives
    # client actions and then sends those actions to the other servers 
    # then other servers bind to the leader (servers can get information from the leader)
    
    # add in fault detection
    # every server has its won log file of the client actions that have been executed 
    # look at log files to see if there is a fault detected in a file.
    # do this by taking a secure hash of a file and see if the hashes are equal 
    # fault = last line of log file = different (checksum discussion
    # from class)
    # if fault detected on a server 
    # replace the logfile with the consensus file + re parse
    # the server_state using the consensus CSV (aka any csv for a 
    # server that is in the consensus group)
    # now, all are synced and fault has been dealt with
    # if leader has a fault, need to make someone in consensus
    # the leader and make all servers bind to that leader