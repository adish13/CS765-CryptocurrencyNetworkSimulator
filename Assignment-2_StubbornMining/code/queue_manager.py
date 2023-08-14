from queue import PriorityQueue
from event import Event, EventAction, EventType
class QueueManager:
    """
    wrapper class for the simulator event queue handling various operations
    like insertion of txn/block and receiving of txn/block
    this queue just creates an event in the priority queue
    the corresponding action is taken in main.py
    """
    event_queue = PriorityQueue()

    @staticmethod
    def insert_txn_create_event(txn_time, txn_obj, node):
        event_obj = Event(EventType.txn, EventAction.SEND, txn_obj, node, None)
        QueueManager.event_queue.put((txn_time, event_obj))
        for peer in node.peers:
            recv_time = node.send_msg(txn_obj, txn_time, peer, 1)
            QueueManager.insert_txn_receive_event(recv_time, txn_obj, peer, node)
    
    @staticmethod
    def insert_txn_receive_event(recv_time, txn_obj, node, sender):
        event_obj = Event(EventType.txn, EventAction.RECEIVE, txn_obj, node, sender)
        QueueManager.event_queue.put((recv_time, event_obj))
    
    @staticmethod
    def insert_block_create_event(broadcast_time, block_obj, node):
        event_obj = Event(EventType.BLOCK, EventAction.SEND, block_obj, node, None)
        QueueManager.event_queue.put((broadcast_time, event_obj))
    
    @staticmethod
    def insert_block_receive_event(recv_time, block_obj, node, sender):
        event_obj = Event(EventType.BLOCK, EventAction.RECEIVE, block_obj, node, sender)
        QueueManager.event_queue.put((recv_time, event_obj))
