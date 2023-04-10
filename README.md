# Replication-CS262
Assignment 3 for CS262

Starting the application
--------------------------
Open three terminals, go into the folder where the `server_agent.py` file is located, and run three instances of the server: 
In the first termainl run 
```
$ python3 server_agent.py 8881 True
```
Then, in the second terminal run 
```
$ python3 server_agent.py 8882 False
```
Then run 
```
$ python3 server_agent.py 8883 False
```` 
in the third terminal

To connect a client to one of the servers, open a new terminal and run the following:
```
$ python3 run_client.py
```
to get a client connected. 

Running the application on different devices
--------------------------
To have clients on different computers as the server, carry out the following steps:

Run the following code in your terminal:

```
$ import socket print(socket.gethostname()) hostName = socket.gethostname()
```

This will give you the host name to connect between computers. Ensure that computers are connected to the same WiFi network.

Update these lines in the code files:

Line 12 on `run_client.py`: `set_host = hostName`

Line 36 on `run_server.py`: `sophia_host = hostName`

Running tests
--------------------------
Go into the `persistence_replication_tests` folder.
In a new terminal, run 
```
python3 persistence_replication_tests.py
```
Other files in this folder are used purely for testing purposes - please do not edit those. 

Common issues:

'Address already in use' issue when you run the files run_server.py or grpc_server.py. Change the set_port variable (line 10, run_server.py OR line 12, grpc_server.py) to be a different value (e.g. 8888) . Then, update the set_port variable ( OR line 12, grpc_client.py) to be that SAME value (e.g. also 8888).

Engineering notebook: https://docs.google.com/document/d/1JPRMwYQ5Q1fQfCrxRsi0h4kE8UZ15pQ1Ze8rgKplbv0/edit?usp=sharing
