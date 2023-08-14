# Assignment 1
Created by Adish Shah (200020012), Akshay Kiran(2000500093), Pinkesh Raghuvanshi (200050106)
## Requirements
The following are the library requirements
1. pydot==1.4.2
2. numpy==1.18.1
3. matplotlib==3.4.1
4. networkx==2.6.2

The code was tested on Python 3.10.9

## Outputs
The sample outputs are stored in the Results folder.

## Running
ALl the code files are in the ```code``` directory.

To run the code, use the following command
```
python3 main.py [--options]
```
The options are the following

1. -n NODES, --nodes NODES : Number of nodes in network
2. -e ENDTIME, --endtime ENDTIME:  End time of simulation
3. -t INTERARRIVAL, --interarrival INTERARRIVAL : Mean interarrival time (in s) of txns
4. -z0 FRACSLOW, --fracslow FRACSLOW : Fraction of slow nodes in network
6. -z1 FRAC_POWERFUL, --frac-powerful FRAC_POWERFUL : Fraction of nodes with high cpu power
6. -b BLOCK_INTERARRIVAL, --block-interarrival BLOCK_INTERARRIVAL : Interarrival time between blocks


None of these options is required as they have default value set. 

## Code flow
Code flow is provided in the design document in the submission directory.

## Code explanation
Code is well commented to and descriptive function, variable names have been used. But a general explanation of major modules is as follows:
1. Node Class

This class contains all the node level properties and methods. So the code to receive a txn, create a txn, mine a block, broadcast block, check validity of block etc. are present here. This is the major class of the program

2. Block Class and txn Class

These contain the various fields and methods to be used by Block and txn objects. They are light classes compared to Node, and do not contain a lot of methods.

3. Queue Manager

The simulator queue has been abstracted out in the class and only the methods of insert/receive txn/block have been provided. This ensures that the entry points of insertion into queue are consistent. 

4. Tree

This contains the blockchain tree for each node. We are able to generate the graphs due to this structure only. We maintain a few variables in it including the leaf node id, timestamps and of course the edge map in form of an adjacency list. The function dump generates all the graphs at the end of simulation

5. utils.py

This file contains the utility functions used throughout the program like random number generators, dumping data into analysis file, creating P2P network etc. All the functions have been documented properly for more details. 

6. topology.py
This file contains the code for creating a random connected graph with minimum 4 and maximum 8 edges between
each node.

7. main.py

This file is the driver program connecting all the parts of code together. It begins with initialising the stuff required throught execution and then goes into a while loop which runs till the end of simulation time. 
