import argparse
import params
import numpy as np
from queue_manager import QueueManager
from node import Node
from block import Block
from event import EventAction, EventType
from utils import *


def create_nodes():
    """
    create N nodes keeping the fraction of slow nodes equal to z
    """
    nodes = []
    high_cpu_powers = [0]*params.N
    perm = np.random.permutation(params.N)
    for i in range(params.N):
        nodes.append(Node())
    for i in range(int(params.FRAC_SLOW * params.N)):
        nodes[perm[i]].is_fast = 0

    perm2 = np.random.permutation(params.N)
    for i in range(int(params.FRAC_POWERFUL*params.N)):
        nodes[perm2[i]].frac_cpu_power = 10
        high_cpu_powers[perm2[i]] = 1
    return nodes,high_cpu_powers

def dump(nodes):
	"""
	create a blockchain tree for each node
	called at end of simulation
	"""
	for node in nodes:
		node.tree.dump_txt(node.nid)
		node.tree.dump(node.nid)

# parse arguments and other initialising stuff here
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--nodes', type=int, default=20, help='Number of nodes in network')
parser.add_argument('-e', '--endtime', type=int, default=400, help='End time of simulation')
parser.add_argument('-t', '--interarrival', type=float, default=0.5, help='Mean interarrival time (in s) of txns')
parser.add_argument('-z0', '--fracslow', type=float, default=0.4, help='Fraction of slow nodes in network')
parser.add_argument('-b', '--block-interarrival', type=float, default=4, help='Interarrival time between blocks')
parser.add_argument('-z1', '--frac-powerful', type=float, default=0.1, help='Fraction of nodes with high cpu power')
args = parser.parse_args()
params.N = args.nodes
params.MEAN_INTERARRIVAL_TIME = args.interarrival
params.FRAC_SLOW = args.fracslow
params.BLOCK_INTERARRIVAL_TIME = args.block_interarrival
params.FRAC_POWERFUL = args.frac_powerful

# setting up network
nodes,high_cpu_powers = create_nodes()
create_P2P(nodes)
set_speed_of_light_delay(nodes)
set_t_blk(nodes)
genesis = Block(-1, -1)

# initialise txns and blocks
for i in range(params.N):
	nodes[i].create_txn()
	nodes[i].create_block(genesis.bid)

#### main loop starts here ####
while QueueManager.event_queue.qsize():
	(event_time, event) = QueueManager.event_queue.get()
	if event_time >= args.endtime:
		break
	if event.type == EventType.txn and event.action == EventAction.SEND:
		# if a node executed send txn, insert another send txn for that
		# node starting from the offset time
		event.node.create_txn(event_time)
	
	if event.type == EventType.txn and event.action == EventAction.RECEIVE:
		# if a node receives a txn, add it to its txn pool
		event.node.receive_txn(event.data, event_time, event.peer)
	
	if event.type == EventType.BLOCK and event.action == EventAction.SEND:
		event.node.broadcast_block(event.data, event_time)

	if event.type == EventType.BLOCK and event.action == EventAction.RECEIVE:
		event.node.receive_block(event.data, event_time, event.peer)

#### main loop ends here ####

# dumps the analysis done for each node into analysis.txt
analyse(nodes,high_cpu_powers)
# creates dot file and png file for graphs
dump(nodes)
print("Number of blocks mined by each node :")
for i in range(len(nodes)):
	print(str(i)+" : " +str(nodes[i].num_blocks))