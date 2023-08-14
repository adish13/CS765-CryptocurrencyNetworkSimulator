from enum import Enum

class EventType(Enum):
	txn = 1
	BLOCK = 2

class EventAction(Enum):
	SEND = 1
	RECEIVE = 2

class Event:
	def __init__(self, type , action, data, node, peer):
		"""
		type of type EventType
		action of type EventAction
		data contains txn object or block object appropriately
		node contains the node who is sending/receiving message
		"""
		self.data = data
		self.type = type
		self.action = action
		self.node = node
		self.peer = peer

	def __repr__(self):
		return f"{self.node} {EventAction(self.action).name} {EventType(self.type).name} {self.data}"
