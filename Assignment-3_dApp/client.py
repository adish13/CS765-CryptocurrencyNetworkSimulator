import json
from web3 import Web3
import random
import matplotlib.pyplot as plt
from networkx import barabasi_albert_graph, to_dict_of_lists

#connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)

#check if ethereum is connected
print(w3.is_connected())

#replace the address with your contract address (!very important)
deployed_contract_address = '0xbbc38c9f5890e0ea509f7c63dc0ab781f5357034'

#path of the contract json file. edit it with your contract json file
compiled_contract_path ="build/contracts/Payment.json"
with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address = Web3.to_checksum_address(deployed_contract_address), abi = contract_abi)

# number of users to register
num_users = 100

# register users
for i in range(num_users):
    contract.functions.registerUser(i, f"user_{i}").transact({'from': w3.eth.accounts[0]})

# # adjacency list
# graph = {}

# # create joint accounts with power-law degree distribution
# degrees = []
# for i in range(1, num_users + 1):
#     # determine degree according to power-law distribution
#     degree = int(random.paretovariate(2.5) * 10)
#     # make sure degree is not greater than remaining number of users
#     degree = min(degree, num_users - i)
#     degrees.append(degree)
#     # select random users to create joint account with
#     joint_users = random.sample(range(i + 1, num_users + 1), degree)
#     # determine initial balance for joint account from exponential distribution
#     balance = int(random.expovariate(1/10)/2)
#     for user in joint_users:
#         contract.functions.createAcc(i-1, user-1, balance).transact({'from': w3.eth.accounts[0]})
#         # add edge to graph
#         if i-1 not in graph:
#             graph[i-1] = [user-1]
#         else:
#             graph[i-1].append(user-1)
#         if user-1 not in graph:
#             graph[user-1] = [i-1]
#         else:
#             graph[user-1].append(i-1)

# create graph using networkX
G = barabasi_albert_graph(100,10)
graph = to_dict_of_lists(G)

for i in range(0, num_users):
    # determine initial balance for joint account from exponential distribution
    balance = int(random.expovariate(1/10)/2)
    # create an account for each pair of neighbours in graph
    for user in graph[i]:
        if (user > i) : # to avoid repititions
            contract.functions.createAcc(i, user, balance).transact({'from': w3.eth.accounts[0]})

# function to return path
def shortest_path_bfs(start, end):
    visited = set() # set to keep track of visited nodes
    queue = [[start]] # queue to keep track of the current path
    if start == end:
        return [start] # return the path if the start and end nodes are the same
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node not in visited:
            neighbors = graph[node] # get the neighbors of the current node
            for neighbor in neighbors:
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
                if neighbor == end:
                    return new_path # return the path if the target node is found
            visited.add(node)
    return None # return None if no path is found

# function to check whether path is feasible
def checkPath(path):
    if path is None:
        return False
    for i in range(len(path)-1):
        balance = contract.functions.balances(path[i], path[i+1]).call()
        if balance <= 0:
            return False
    return True


# fire transactions
success_rates = []
n_transactions = 1000
batch_size = 100
n_batches = n_transactions // batch_size
for i in range(n_batches):
    n_success = 0
    for j in range(batch_size):
        # select two random users to send amount between
        user1 = random.randint(0, num_users-1)
        user2 = random.randint(0, num_users-1)
        # skip if same user is selected
        if user1 == user2:
            continue
        # try to send amount between users
        path = shortest_path_bfs(user1, user2)
        # check path
        if (checkPath(path)) :
            # send amount along path (one edge at a time)
            for k in range(len(path)-1):
                contract.functions.sendAmount(path[k], path[k+1]).transact({'from': w3.eth.accounts[0]})
            n_success += 1

    # record success rate for current batch
    success_rate = n_success / batch_size
    success_rates.append(success_rate)
    print(f"Batch {i+1}/{n_batches}: Success rate = {success_rate}")

# plot success rates over time
plt.plot(range(1, n_batches+1), success_rates)
plt.xlabel("Batch")
plt.ylabel("Success rate")
plt.title(f"Success rates for {n_transactions} transactions")
plt.savefig("result.png")
plt.show()

# close joint accounts
for i in range(num_users):
    for j in graph[i]:
        if (j > i):
            contract.functions.closeAccount(i, j).transact({'from': w3.eth.accounts[0]})