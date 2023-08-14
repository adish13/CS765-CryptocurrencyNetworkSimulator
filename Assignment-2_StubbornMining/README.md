# Assignment 2
Created by
1. Adish Shah (200020012)
2. Padakanti Akshay Kiran (200050093)
3. Pinkesh Raghuvanshi (200050106)

## Requirements
The following are the library requirements
1. pydot==1.4.2
2. numpy==1.18.1
3. matplotlib==3.4.1
4. networkx==2.6.2

The code was tested on Python 3.10.9

## Running
To run the code, use the following command
```
python3 main.py [--options]
```
The options are the following

1. -n NODES, --nodes NODES : Number of nodes in network
2. -e ENDTIME, --endtime ENDTIME:  End time of simulation
3. -t INTERARRIVAL, --interarrival INTERARRIVAL : Mean interarrival time (in s) of txns
4. -z FRACSLOW, --fracslow FRACSLOW : Fraction of slow nodes in network
5. -b BLOCK_INTERARRIVAL, --block-interarrival BLOCK_INTERARRIVAL : Interarrival time between blocks
6. -p FRAC_POWERFUL, --frac-powerful FRAC_POWERFUL : Fraction of nodes with high cpu power
7. --high-hash-mean HIGH_HASH_MEAN : Mean of higher hashing power
8. --low-hash-mean LOW_HASH_MEAN : Mean of lower hashing power
9.  -v HBLKV, --hblkv HBLKV : Variance for gaussian distribution of hashing power
10.  --selfish: 0 if adversary is selfish, 1 if stubborn. Defaults to selfish
11.  --zeta: Fraction of honest nodes the adversary is connected to. Defaults to 0.25
12.  --alphascale: Scaling for hashing power of adversary. Defaults to 1
13. --ahp : Parameter for directly setting hashing power of adversary. Others are calculated seperately.
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

6. main.py

This file is the driver program connecting all the parts of code together. It begins with initialising the stuff required throught execution and then goes into a while loop which runs till the end of simulation time. 

7. selfishnode.py

This file contains the SelfishNode class, which inherits the Node class. Some functions have been overridden, so as to handle the private chain broadcasting and receiving mechanisms. 

8. stubbornnode.py

This file contains the StubbornNode class, which inherits the Node class. Some functions have been overridden, so as to handle the private chain broadcasting and receiving mechanisms according to a stubborn miner.

