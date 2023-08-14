from utils import *

class txn:
	"""
	class containing model of a txn
	"""
	txn_id_counter = 0

	def __init__(self, sender_id, receiver_id, amount=50, txn_time=0, is_coinbase = 0):
		self.sender_id = sender_id
		self.receiver_id = receiver_id
		self.amount = amount
		self.txn_id = txn.txn_id_counter
		self.is_coinbase = is_coinbase
		txn.txn_id_counter += 1

	def get_msg(self):
		if self.is_coinbase == 0:
			msg = str(self.txn_id) + ": " + str(self.sender_id) + " pays " + str(self.receiver_id)
			msg += " " + str(self.amount) + " coins"
		else:  #Mining Fee txn
			msg = str(self.txn_id) + ": " + str(self.receiver_id) + " mines " + str(self.amount) + " coins"

		return msg
	
	def __repr__(self):
		return self.get_msg()
