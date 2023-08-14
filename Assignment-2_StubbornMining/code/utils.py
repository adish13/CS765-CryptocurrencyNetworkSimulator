import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from block import Block
import params
import random
from topology import create_random_graph

def sample_exponential(mean):
	return np.random.exponential(mean)


def sample_uniform(low, high):
	return np.random.uniform(low, high)


def sample_randint(low, high, exclude=None):
	"""
	generates a random integer between low and high and ensures that
	the value of the integer is not `exclude`
	"""
	while True:
		x = np.random.randint(low, high+1)
		if not exclude or x != exclude:
			return x


def create_P2P(nodes, adv_index, zeta):
	"""
	creates a random graph for the P2P network
	slightly different from last assignment as this procedure is faster
	"""
	n = len(nodes)
	while True:
		s = []
		mean_deg = np.log(n)

		while len(s) < n:
			nex = int(nx.utils.powerlaw_sequence(1, 2.5)[0])
			if nex >= mean_deg:
				s.append(nex)
		if sum(s)%2 == 0:
			break

	G = nx.configuration_model(s)
	G = nx.Graph(G)                              # remove parallel loops
	G.remove_edges_from(nx.selfloop_edges(G))    # remove self loops

	for edge in G.edges():
		if edge[0] == adv_index or edge[1] == adv_index:
			continue
		nodes[edge[0]].add_peer(nodes[edge[1]])
		nodes[edge[1]].add_peer(nodes[edge[0]])

	G.remove_node(adv_index)
	G.add_node(adv_index)

	adv_connections = int(np.math.floor(zeta*(n-1)))
	adv_edges = random.sample([i for i in range(n) if i != adv_index], adv_connections)
	for i in adv_edges:
		G.add_edge(adv_index, i)
		nodes[adv_index].add_peer(nodes[i])
		nodes[i].add_peer(nodes[adv_index])

	# color map
	color_map = ['darkorange' if node.is_fast else 'lightgray' for node in nodes]
	color_map[n-1] = 'blue'          # this is because adv node will be in last position in G.nodes

	pos = nx.spring_layout(G)
	nx.draw_networkx(G, pos, node_color=color_map)
	plt.savefig('test.pdf')


def set_speed_of_light_delay(nodes):
	"""
	sets the speed of light delay for each link in the network
	"""
	for i in range(len(nodes)):
		for j in range(i+1, len(nodes)):
			# speed of light delay in milliseconds
			params.RHO[i][j] = sample_randint(10, 500) * 0.001
			params.RHO[j][i] = params.RHO[i][j]

def set_t_blk(nodes):
	"""
	sets the interarrival block time ofr each individual node (i.e. t_blk in node model
	and T_k	variable in problem statement
	"""

	if(params.AHP == -1):
		total_hash_power = 0
		for node in nodes:
			if np.random.uniform() <= params.FRAC_POWERFUL:
				hash_power = np.random.normal(params.HIGH_HASH_MEAN, params.HASH_POWER_VAR)
			else:
				hash_power = np.random.normal(params.LOW_HASH_MEAN, params.HASH_POWER_VAR)

			if node.is_selfish:
				hash_power *= params.ALPHA_SCALE
			node.frac_cpu_power = hash_power
			total_hash_power += hash_power

		for node in nodes:
			node.frac_cpu_power /= total_hash_power
			node.t_blk = params.BLOCK_INTERARRIVAL_TIME / node.frac_cpu_power
			if node.is_selfish:
				print(f"main: adversary node hashing power is {node.frac_cpu_power}")

	else:
		total_hash_power = 0
		count = 0
		max_count = int(0.1*params.N)
		for node in nodes:
			if not node.is_selfish:
				if count <= max_count:
					hash_power = 10
					count += 1
				else:
					hash_power = 1

				node.frac_cpu_power = hash_power
				total_hash_power += hash_power

		for node in nodes:
			if not node.is_selfish:
				node.frac_cpu_power = (node.frac_cpu_power*(1-params.AHP))/total_hash_power
			else:
				node.frac_cpu_power = params.AHP
			node.t_blk = params.BLOCK_INTERARRIVAL_TIME / node.frac_cpu_power
			if node.is_selfish:
				print(f"main: adversary node hashing power is {node.frac_cpu_power}")

			

def analyse(nodes, adversary_node_index = -1):
	"""
	dump the analysis data for each node into analysis.txt
	"""
	# flag = 0
	# for node in nodes:
	# 	if node.is_selfish:
	# 		print(node.tree.tree)
	# 	elif not flag:
	# 		print(node.tree.tree)
	# 		flag = 1

	fh = open("analysis.txt", "w")

	# write specification of each node
	for node in nodes:
		fh.write(f"Node {node.nid}, {'fast' if node.is_fast else 'slow'}, block interarrival time : {node.t_blk} ")
		fh.write(f"Frac hashing power: {node.frac_cpu_power:.2f}\n")
	
	fh.write("="*20 + "\n")

	# write ratio of blocks in chain to total number of
	# blocks created for each node
	fh.write("Ratio\n")
	n_txns = [0] * len(nodes)
	for idx, node in enumerate(nodes):
		num_blocks_in_longest_chain = 0
		leaf = node.tree.leaf_bid
		while leaf != -1:
			creator_id = Block.bid_to_obj[leaf].creator_id
			if creator_id == node.nid:
				num_blocks_in_longest_chain += 1
			n_txns[idx] += len(Block.bid_to_obj[leaf].txns)
			leaf = Block.bid_to_obj[leaf].pbid
		if node.num_blocks != 0:
			fh.write(f"Node {node.nid}: {num_blocks_in_longest_chain / node.num_blocks}\n")
		else:
			fh.write(f"Node {node.nid}: 0\n")

		if idx == adversary_node_index:
			params.MPU_ADVERSARY = num_blocks_in_longest_chain / node.num_blocks

	fh.write("="*20 + "\n")
	
	# write number of txns in longest chain of each node
	fh.write("No. of txns in longest chain\n")
	for i in range(len(nodes)):
		fh.write(f"Node {nodes[i].nid}: {n_txns[i]}\n")
	
	fh.write("="*20 + "\n")

	# get branch lengths
	fh.write("Branch Lengths\n")
	for node in nodes:
		lengths = []
		node.tree.dfs(lengths = lengths)
		lengths.sort()
		params.NUM_BLOCKS_MAIN_CHAIN = max(params.NUM_BLOCKS_MAIN_CHAIN, lengths[-1])
		fh.write(f"Node {node.nid}: {lengths}\n")	

	fh.close()

def mpu_overall(nodes):
	num_blocks = 0
	for node in nodes:
		num_blocks += node.num_blocks

	return params.NUM_BLOCKS_MAIN_CHAIN / num_blocks, num_blocks
	
if __name__ == '__main__':
	print(sample_exponential(1))
