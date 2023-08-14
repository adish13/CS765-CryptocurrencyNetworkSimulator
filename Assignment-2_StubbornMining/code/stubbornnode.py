from node import Node
from tree import Tree
from block import Block
import params
from queue_manager import QueueManager
from utils import *
from queue import PriorityQueue

class StubbornNode(Node):
    """
    class containing stubborn ndoe
    will inherit all the properties of node
    and we will modify it here
    """

    def __init__(self):
        Node.__init__(self)
        self.event_queue = PriorityQueue()
        self.is_selfish = 1  #we're using the same flag for both the adversaries
        
        # valid assumption here that the private chain will not have any forks
        # convention: private_chain contains blocks starting from one already in the
        # main chain, or one which is in competition with the honest chain and is publicly known
        self.private_chain = [Block.bid_to_obj[0]]

    def create_block(self, pbid, time_offset = 0):
        """
        given the pbid, creates an event at future time for creation of subsequent block
        before adding the event, the block is checked for valid txns, and only
        valid txns are inserted into the block
        time_offset: simulation time at which this function is called
        """
        self.num_blocks += 1
        block = Block(pbid, self.nid)

        #A Stubborn Miner only includes the coinbase txn to save time
        # balances = self.tree.get_balances(block.pbid)
        # while self.txn_queue and len(block.txns) < params.MAX_txn_IN_BLOCK:
        #     txn = self.txn_queue[0]
        #     self.txn_queue.pop(0)

        #     assert txn.sender_id >= 0 # should not have any txn with -1 sender id over here

        #     # validate txn before inserting in block
        #     if txn.amount <= balances[txn.sender_id]:
        #         block.txns.append(txn)
        #         balances[txn.sender_id] -= txn.amount
            
        broadcast_time = time_offset + sample_exponential(self.t_blk)
        # get mining fee
        coinbase_txn = self.create_coinbase_txn(broadcast_time)
        block.txns.append(coinbase_txn)
        block.is_selfish_mined = 1
        self.event_queue.put((broadcast_time, block, self))


    def broadcast_block(self, block, time):
        self.receive_block(block, time, self)

    def add_private_blocks(self, num):
        # add the private chain to adversary tree
        for i in range(num):
            u = self.private_chain[i].bid
            v = self.private_chain[i+1].bid
            if v not in self.tree.tree[u]:
                self.tree.addEdge(u, v, self.private_chain[i+1].time_of_arrival)

    def receive_block(self, block, time, sender):
        """
        when the selfish node receives a block, it checks its lead
        and takes action accordingly
        """
        id = block.bid
        # already processed and forwarded this blk
        if (-1, id) in self.overall_history or block.bid in self.tree.tree[block.pbid]:
            return
        # when called from broadcast_block, sender is the same node, which is not in history
        self.add_history(sender, (-1, id))
        
        # validate block
        balances = self.tree.get_balances(block.pbid)
        for txn in block.txns:
            if txn.sender_id >= 0 and txn.amount > balances[txn.sender_id]:
                return
            balances[txn.sender_id] -= txn.amount

        # simulate private chain blocks
        while self.event_queue.qsize():
            item = self.event_queue.get()
            if item[0] <= time:
                item[1].time_of_arrival = item[0]
                self.private_chain.append(item[1])
                self.create_block(item[1].bid, item[0])
            else:
                self.event_queue.put(item)
                break

        lead = len(self.private_chain) + (self.private_chain[0].depth - 1) - self.tree.max_depth

        # add the current block into main blockchain tree
        self.tree.addEdge(block.pbid, block.bid, time)

        if block.creator_id != self.nid:
            if lead <= 0:
                # clear event simulator
                while self.event_queue.qsize(): self.event_queue.get()
                self.add_private_blocks(len(self.private_chain)-1)

                # set this as first block for adversary to mine on
                self.private_chain = [block]
                self.create_block(block.bid, time)

            elif lead == 1:
                for _block in self.private_chain[1:]:
                    self.broadcast_block(_block, time)
                self.private_chain = self.private_chain[-1:]
            
            elif lead == 2: #Don't broadcast the entire private chain
                #Broadcast only one block
                for _block in self.private_chain[1:2]:
                    self.broadcast_block(_block, time)
                
                # keep mining on your private chain
                self.private_chain = self.private_chain[1:]
            
            elif lead > 2:
                #Broadcast only one block
                for _block in self.private_chain[1:2]:
                    self.broadcast_block(_block, time)
                
                # keep mining on your private chain
                self.private_chain = self.private_chain[1:]
        
        if block.creator_id == self.nid:
            for peer in self.peers:  #forward to peers after verifying and processing
                if (-1, id) not in self.p2p_history[peer]:
                    peer_recv_time = self.send_msg(block, time, peer, 0)
                    QueueManager.insert_block_receive_event(peer_recv_time, block, peer, self)
