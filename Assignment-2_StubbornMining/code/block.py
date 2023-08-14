class Block:
	"""
	class containing model of a block
	contains some extra fields for a better code flow
	"""
	bid_counter = 0
	bid_to_obj = dict()

	def __init__(self, pbid, creator_id):
		self.pbid = pbid
		self.depth = 1
		if pbid != -1:
			self.depth = Block.bid_to_obj[pbid].depth + 1
		self.bid = Block.bid_counter
		self.txns = []
		self.creator_id = creator_id # id of the node that created this block
		# for ease of visualisation
		self.is_selfish_mined = 0
		# needed for private blocks
		self.time_of_arrival = 0
		Block.bid_to_obj[Block.bid_counter] = self
		Block.bid_counter += 1

	def add_txn(self, txn):
		self.txns.append(txn)

	def get_msg(self):
		pass  #return str representation of blk

	def size(self):
		"""
		returns block size in KB
		"""
		return min(1, len(self.txns))

	def __str__(self) -> str:
		return f"Block ID {self.bid} mined by {self.creator_id} and has {len(self.txns)} txns"
