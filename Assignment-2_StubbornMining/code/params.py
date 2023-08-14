from collections import defaultdict
"""
file denoting paramters that are either params or set at the start
of simulation and not changed later on
"""
N = 10 # no of nodes
FRAC_SLOW = 0.3  #fraction of slow nodes (z = 0.3)
MEAN_INTERARRIVAL_TIME = 1
N_EVENTS_PER_NODE = 10000
PARSE_TIME = 1e-7
COINBASE_AMOUNT = 50
MAX_txn_IN_BLOCK = 999 # not 1000 because 1 will be coinbase
BLOCK_INTERARRIVAL_TIME = 10
FRAC_POWERFUL = 0.5
HIGH_HASH_MEAN = 200
LOW_HASH_MEAN = 100
HASH_POWER_VAR = 10
RHO = defaultdict(lambda: defaultdict(lambda: 0))
SELFISH = 0    #1 if selfish, 0 if adversary
NUM_BLOCKS_MAIN_CHAIN = 0
MPU_ADVERSARY = 0
ZETA = 0.25
ALPHA_SCALE = 1
AHP=-1