import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from block import Block
import params
import os

class Tree:
    def __init__(self):
        """
        tree: stores the directed graph in adjacency list format
        max_depth: stores the maximum depth of blockchain
        new_Longest_chain: boolean which is set to 1 if new longest chain is being formed
        leaf_bid: current endpoint of blockchain
        time: map of int -> int denoting blkid -> time of arrival of block
        """
        self.tree = defaultdict(list)
        self.max_depth = 1
        self.new_longest_chain = 0
        self.leaf_bid = 0 # block id of block at end of longest chain
        self.time = defaultdict(lambda: 0)
  
    # function to add an edge to graph
    def addEdge(self, u, v, time):
        """
        denotes that block with block id v is next to block with block id u
        in blockchain
        time denotes the time of appending of block
        """
        self.tree[u].append(v)
        self.time[v] = time
        if Block.bid_to_obj[v].depth > self.max_depth:
            self.max_depth = Block.bid_to_obj[v].depth
            self.new_longest_chain = 1
            self.leaf_bid = v
        else:
            self.new_longest_chain = 0
    
    def get_balances(self, bid):
        """
        returns a dict containing balances of nodes till the block
        """
        balances = defaultdict(lambda: 0)
        while bid != -1:
            for txn in Block.bid_to_obj[bid].txns:
                balances[txn.sender_id] -= txn.amount
                balances[txn.receiver_id] += txn.amount
            bid = Block.bid_to_obj[bid].pbid

        return balances
    
    def dfs(self, start = 0, lengths = [], level = 1):
        """
        perform dfs and return a list containing length of branches in the tree
        """
        if len(self.tree[start]) == 0:
            lengths.append(level)
            return
        for i in self.tree[start]:
            self.dfs(start = i, lengths = lengths, level = level + 1)
        
    def dump_txt(self, nid):
        """
        dumps tree file as txt file
        """
        if not os.path.isdir("treefiles"):
            os.mkdir("treefiles")
        blocks = [val for k,v in self.tree.items() for val in v]
        blocks = blocks + [k for k,v in self.tree.items()]
        blocks = list(set(blocks))
        blocks.sort(key = lambda blk: Block.bid_to_obj[blk].depth)
        with open(f"treefiles/node_{nid}.txt", "w") as fh:
            for block in blocks:
                # -1 in depth because we have started depth counter from 0 in Block model
                fh.write(f"blockHash: {block}\nblockNum: {Block.bid_to_obj[block].depth - 1}\n")
                fh.write(f"TimeOfArrival: {self.time[block]}\nparentBlockHash: {Block.bid_to_obj[block].pbid}\n")
                fh.write("="*20 + "\n")
    
    def dump(self, nid):
        """
        create a graphical representation for the tree for each node
        """
        detailed_graphs_dir = "detailed_graphs"
        graphs_dir = "graphs"
        # create directory for storing graphs
        if not os.path.isdir(detailed_graphs_dir):
            os.mkdir(detailed_graphs_dir)
        if not os.path.isdir(graphs_dir):
            os.mkdir(graphs_dir)

        # create a directed graph
        G = nx.DiGraph()
        G.add_node(0)
        queue = [0]
        while len(queue):
            top = queue[0]
            queue.pop(0)
            for node in self.tree[top]:
                G.add_edge(top, node)
                queue.append(node)

        # find the nodes in longest chain
        longest_chain = []
        leaf = self.leaf_bid
        while leaf >= 0:
            longest_chain.append(leaf)
            leaf = Block.bid_to_obj[leaf].pbid

        # set node colors
        nodes = G.nodes()
        node_colors = ['lightgray'] * len(nodes)
        for idx, node in enumerate(nodes):
            if node in longest_chain:
                node_colors[idx] = 'darkorange'
            if Block.bid_to_obj[node].is_selfish_mined:
                node_colors[idx] = 'red'

        # create and save graph as png
        plt.clf()
        nx.draw_spring(G, with_labels=True, node_color=node_colors)
        plt.savefig(f"{detailed_graphs_dir}/node_{nid}.png", dpi=500)
        
        # save detailed graph in a dot file
        new_labels = dict()
        for idx, node in enumerate(G.nodes):
            G.nodes[node]['shape'] = 'square'
            G.nodes[node]['color'] = node_colors[idx]
            new_labels[node] = f"{node}\n{self.time[node]:.2f}"

            # add txns in labels
            for txn in Block.bid_to_obj[node].txns:
                # replace : to - because graph does not accept ':' in its node label
                new_labels[node] += f"\n{txn.get_msg().replace(':', ' -')}"
            
            # add balances in label
            balances = self.get_balances(node)
            new_labels[node] += f"\nBalances"
            for i in range(params.N):
                new_labels[node] += f"\n{i} - {balances[i]}"

        # relabel nodes to add balances and txns
        G_detailed = nx.relabel_nodes(G, new_labels)
        nx.drawing.nx_pydot.write_dot(G_detailed, f"{detailed_graphs_dir}/graph_{nid}.dot")

        # create graph in format specified
        new_labels = dict()
        for idx, node in enumerate(G.nodes):
            new_labels[node] = f"blockHash - {Block.bid_to_obj[node].bid}\n"
            new_labels[node] += f"blockNum - {Block.bid_to_obj[node].depth - 1}\n"
            new_labels[node] += f"TimeOfArrival - {self.time[node]:.2f}\n"
            new_labels[node] += f"N txns - {len(Block.bid_to_obj[node].txns)}\n"
            new_labels[node] += f"parentBlockHash - {Block.bid_to_obj[node].pbid}"
        G_compact = nx.relabel_nodes(G, new_labels)
        nx.drawing.nx_pydot.write_dot(G_compact, f"{graphs_dir}/graph_{nid}.dot")
