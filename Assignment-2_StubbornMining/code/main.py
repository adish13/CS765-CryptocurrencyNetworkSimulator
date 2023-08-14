import argparse
import params
import numpy as np
from queue_manager import QueueManager
from node import Node
from selfishnode import SelfishNode
from stubbornnode import StubbornNode
from block import Block
from event import EventAction, EventType
from utils import *

def create_nodes(adversary_node_index):
	"""
	create N nodes keeping the fraction of slow nodes equal to z
	"""
	nodes = []
	perm = np.random.permutation(params.N)
	print(f"main: adversary node is {adversary_node_index}")
	for i in range(params.N):
		if i == adversary_node_index:
			if params.SELFISH == 0:
				nodes.append(SelfishNode())
			else:
				nodes.append(StubbornNode())
		else:
			nodes.append(Node())
	for i in range(int(params.FRAC_SLOW * params.N)):
		if nodes[perm[i]].is_selfish == 0:
			nodes[perm[i]].is_fast = 0
	
	return nodes

def dump(nodes):
	"""
	create a blockchain tree for each node
	called at end of simulation
	"""
	flag = 0
	for node in nodes:
		if node.is_selfish:
			node.tree.dump_txt(node.nid)
			node.tree.dump(node.nid)
		elif flag == 0:
			node.tree.dump_txt(node.nid)
			node.tree.dump(node.nid)
			flag = 1

# parse arguments and other initialising stuff here
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--nodes', type=int, default=10, help='Number of nodes in network')
parser.add_argument('-e', '--endtime', type=int, default=1000, help='End time of simulation')
parser.add_argument('-t', '--interarrival', type=float, default=1, help='Mean interarrival time (in s) of txns')
parser.add_argument('-z', '--fracslow', type=float, default=0.3, help='Fraction of slow nodes in network')
parser.add_argument('-b', '--block-interarrival', type=float, default=5, help='Interarrival time between blocks')
parser.add_argument('-p', '--frac-powerful', type=float, default=0.5, help='Fraction of nodes with high cpu power')
parser.add_argument('--high-hash-mean', type=float, default=1, help='Mean of higher hashing power')
parser.add_argument('--low-hash-mean', type=float, default=0.5, help='Mean of lower hashing power')
parser.add_argument('-v', '--hblkv', type=float, default=0.1, help='Variance for gaussian distribution of hashing power')
parser.add_argument('--selfish', type=int, default=0, help='0 if adversary is selfish, 1 if stubborn')
parser.add_argument('--zeta', type=float, default=0.1, help='Fraction of honest nodes the adversary is connected to')
parser.add_argument('--alphascale', type=int, default=1, help='Scaling for hashing power of adversary')

# parameter for directly setting adversary hashing power, unlike scaling done before
parser.add_argument('--ahp', type=float, default=-1, help='Set adversary hashing power')

args = parser.parse_args()
params.N = args.nodes
params.MEAN_INTERARRIVAL_TIME = args.interarrival
params.FRAC_SLOW = args.fracslow
params.BLOCK_INTERARRIVAL_TIME = args.block_interarrival
params.FRAC_POWERFUL = args.frac_powerful
params.HIGH_HASH_MEAN = args.high_hash_mean
params.LOW_HASH_MEAN = args.low_hash_mean
params.HASH_POWER_VAR = args.hblkv
params.SELFISH = args.selfish
params.ZETA = args.zeta
params.ALPHA_SCALE = args.alphascale
params.AHP = args.ahp

genesis = Block(-1, -1)
adversary_node_index = sample_randint(0, params.N-1)
# setting up network
nodes = create_nodes(adversary_node_index)
create_P2P(nodes, adversary_node_index, params.ZETA)
set_speed_of_light_delay(nodes)
set_t_blk(nodes)


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

## At the end of the simulation, if the adversary has private blocks left over 
## it adds them to its tree
nodes[adversary_node_index].add_private_blocks(len(nodes[adversary_node_index].private_chain) - 1)
# dumps the analysis done for each node into analysis.txt
analyse(nodes, adversary_node_index)
# creates dot file and png file for graphs
dump(nodes)

# print mpu overall
print(f"mpu adversary: {params.MPU_ADVERSARY}")

mpu_overall_val, num_block_overall = mpu_overall(nodes)
print(f"mpu overall: {mpu_overall_val}")


# calculation of R_pool adversary
num_blocks_main_chain = mpu_overall_val * num_block_overall
print(f"R_pool adversary: {params.MPU_ADVERSARY * nodes[adversary_node_index].num_blocks / num_blocks_main_chain}")
