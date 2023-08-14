import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from block import Block
import params
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


def create_P2P(nodes):
    """
    creates a random graph for the P2P network
    """

    G = nx.Graph()
    n = len(nodes)
    graph = create_random_graph(n,4,8)
    for node,peers in graph.items():
        for x in peers:
            if(not G.has_edge(node,x)):
                G.add_edge(node,x)
                nodes[node].add_peer(nodes[x])
                nodes[x].add_peer(nodes[node])             
                # remove parallel loops

    # color map
    color_map = [
        'darkorange' if node.is_fast else 'lightgray' for node in nodes]

    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos, node_color=color_map)
    plt.savefig('test.png')

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
    total_hash_power = 0
    num_nodes = len(nodes)
    num_high_cpu_nodes = int(params.FRAC_POWERFUL*num_nodes)
    total_hash_power = params.HIGH_HASH_POWER*num_high_cpu_nodes + params.LOW_HASH_POWER*(num_nodes-num_high_cpu_nodes)

    for node in nodes:
        node.frac_cpu_power /= total_hash_power
        node.t_blk = params.BLOCK_INTERARRIVAL_TIME / node.frac_cpu_power



def analyse(nodes,high_cpu_powers):
    """
    dump the analysis data for each node into analysis.txt
    """
    fh = open("analysis.txt", "w")

    # write specification of each node
    for node in nodes:
        fh.write(
            f"Node {node.nid}, {'fast' if node.is_fast else 'slow'}, block interarrival time : {node.t_blk} ")
        fh.write(f"Frac hashing power: {node.frac_cpu_power:.2f}\n")

    fh.write("="*20 + "\n")

    # write ratio of blocks in chain to total number of
    # blocks created for each node
    ratio = [0]*params.N

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
            ratio[idx] = num_blocks_in_longest_chain/node.num_blocks 
            fh.write(
                f"Node {node.nid}: {num_blocks_in_longest_chain / node.num_blocks}\n")
        else:
            fh.write(f"Node {node.nid}: 0\n")

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
        node.tree.dfs(lengths=lengths)
        lengths.sort()
        fh.write(f"Node {node.nid}: {lengths}\n")



    # Create a figure and axis object
    fig, ax = plt.subplots()


    # Plot the data
    for i in range(len(high_cpu_powers)):
        if high_cpu_powers[i]:
            ax.plot(i, ratio[i], 'o', color='orange')
        else:
            ax.plot(i, ratio[i], 'o', color='gray')

    plt.plot(range(len(high_cpu_powers)), ratio, color='black')

    # Set axis labels and title
    ax.set_xlabel('Node')
    ax.set_ylabel('Ratio')

    # Set x-axis tick labels
    x_labels = range(len(high_cpu_powers))
    ax.set_xticks(x_labels)
    ax.set_xticklabels(x_labels)

    # Show the plot
    plt.show()

    fh.close()
