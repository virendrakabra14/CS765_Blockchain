import json
from web3 import Web3
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random

"""
Functions interacting with the contract
"""

def registerUser(user_id, user_name, contract, from_acc):
    contract.functions.registerUser(user_id, user_name).transact({'from':from_acc})

def createAcc(user_id_1, user_id_2, contract, from_acc, total_balance=None, mean_balance=10):
    if total_balance is None:
        total_balance = int(np.random.exponential(scale=mean_balance))
        if total_balance%2 == 1:        # extra (for equal division)
            total_balance += 1
    assert total_balance%2 == 0
    contract.functions.createAcc(user_id_1, user_id_2, total_balance).transact({'from':from_acc})

def sendAmount(user_id_1, user_id_2, contract, from_acc, amount=1, print_error=False):
    edges = contract.functions.getEdges().call()
    num_nodes = len(edges)
    index_1 = contract.functions.getIndexFromId(user_id_1).call()
    index_2 = contract.functions.getIndexFromId(user_id_2).call()

    if index_1>=num_nodes or index_2>=num_nodes:
        if print_error:
            print("transaction failure: nodes not present")
        return False
    
    visited = [-1 for i in range(num_nodes)]    # works as both `visited` and `distance` arrays
    parents = [set() for i in range(num_nodes)]
    queue = []

    queue.append(index_1)
    visited[index_1] = 0

    # https://stackoverflow.com/questions/20257227/
    while not len(queue) == 0:
        node = queue.pop(0)
        for i in range(num_nodes):
            if edges[node][i] >= 0:             # for considering paths having
                                                # sufficient funds, use `>= amount`
                if visited[i] == -1:
                    visited[i] = visited[node]+1
                    parents[i].add(node)
                    queue.append(i)
                else:
                    if visited[i] == visited[node]-1:
                        parents[node].add(i)    # capture ALL shortest paths
        if node == index_2:
            break

    # get a shortest path
    path = []
    node = index_2
    while node != index_1:
        path.insert(0, node)
        if len(parents[node]) == 0:
            if print_error:
                print("transaction failure: no path found")
            return False
        parents[node] = sorted(parents[node], key=lambda x: -edges[x][node])
        node = list(parents[node])[0]   # heuristic: parent with highest fund
    path.insert(0, index_1)

    # check for sufficient funds along this path
    for i in range(len(path)-1):
        if edges[path[i]][path[i+1]] < amount:
            if print_error:
                print("transaction failure: insufficient funds along shortest path")
            return

    for i in range(len(path)-1):
        id1 = contract.functions.getIdFromIndex(path[i]).call()
        id2 = contract.functions.getIdFromIndex(path[i+1]).call()
        try:
            contract.functions.sendAmount(id1, id2, amount).transact({'from':from_acc})
        except:
            if print_error:
                print("transaction failure: contract function raised an exception")
            return False
    
    return True

def closeAccount(user_id_1, user_id_2, contract, from_acc):
    contract.functions.closeAccount(user_id_1, user_id_2).transact({'from':from_acc})


if __name__=="__main__":

    """
    Initial connection setup
    """

    # connect to the local ethereum blockchain
    provider = Web3.HTTPProvider('http://127.0.0.1:8545', request_kwargs={'timeout': 600})
    w3 = Web3(provider)
    # check if ethereum is connected
    assert w3.is_connected() == True

    # contract address
    deployed_contract_address = '0x11f8e63aD45d88097d55e24047A1c092866B667A'

    # path to contract json file
    compiled_contract_path ="build/contracts/Payment.json"
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']
    contract = w3.eth.contract(address = deployed_contract_address, abi = contract_abi)


    """
    Simulation
    """

    num_users = 100
    num_txns = 1000
    ratio_interval = 100
    ratios = {}
    ratios_moving = {}

    # register users

    for i in range(num_users):
        registerUser(i, f"user{i}", contract, w3.eth.accounts[0])
    user_ids = list(range(num_users))

    # create connected graph, and joint accounts

    graph = nx.powerlaw_cluster_graph(n=100, m=5, p=0.3)
    while not nx.is_connected(graph):
        graph = nx.powerlaw_cluster_graph(n=100, m=5, p=0.3)
    
    for edge in graph.edges:
        createAcc(edge[0], edge[1], contract, w3.eth.accounts[0])   # mean balance: 10
    
    # perform transactions

    successful_in_this_interval = 0
    successful_total = 0

    for i in range(num_txns):
        user_1, user_2 = random.sample(user_ids, k=2)
        if sendAmount(user_1, user_2, contract, w3.eth.accounts[0], amount=1):
            successful_in_this_interval += 1
            successful_total += 1
        if i % ratio_interval == (ratio_interval-1):
            print(i)
            ratios[i+1] = successful_in_this_interval/ratio_interval
            ratios_moving[i+1] = successful_total/(i+1)
            successful_in_this_interval = 0
    
    # plot

    ratios = dict(sorted(ratios.items()))
    ratios_moving = dict(sorted(ratios_moving.items()))
    print(f"{ratios=}")
    print(f"{ratios_moving=}")
    
    (fig, ax) = plt.subplots()
    ax.scatter(ratios.keys(), ratios.values(), label='Ratio')
    ax.scatter(ratios_moving.keys(), ratios_moving.values(), label='Moving Ratio')
    fig.savefig("plot_ratios.png", bbox_inches="tight")