import json
from web3 import Web3
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random


class Interact:
    """
    Class for interaction with the contract
    """

    def __init__(self, contract, from_acc):
        self.contract = contract
        self.from_acc = from_acc
        self.adj_matrix = None

    def registerUser(self, user_id, user_name):
        self.contract.functions.registerUser(user_id, user_name).transact({'from':self.from_acc})

    def createAcc(self, user_id_1, user_id_2, total_balance=None, mean_balance=10):
        if total_balance is None:
            total_balance = int(np.random.exponential(scale=mean_balance))
            if total_balance%2 == 1:        # extra (for equal division)
                total_balance += 1
        assert total_balance%2 == 0
        self.contract.functions.createAcc(user_id_1, user_id_2, total_balance).transact({'from':self.from_acc})

    def get_matrix(self):
        self.adj_matrix = self.contract.functions.getEdges().call()

    def sendAmount(self, user_id_1, user_id_2, amount=1, print_error=False):
        # Not calling getEdges() every time, as the simulation
        # does not involve creating/closing accounts after txns start.
        # In the general case, need to get adj_matrix each time.

        assert self.adj_matrix is not None, "adj_matrix is None"

        num_nodes = len(self.adj_matrix)
        index_1 = self.contract.functions.getIndexFromId(user_id_1).call()
        index_2 = self.contract.functions.getIndexFromId(user_id_2).call()

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
                if self.adj_matrix[node][i] >= 0:   # for considering paths having
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
            parents[node] = sorted(parents[node], key=lambda x: -self.adj_matrix[x][node])
            node = list(parents[node])[0]   # heuristic: parent with highest fund
        path.insert(0, index_1)

        # check for sufficient funds along this path
        for i in range(len(path)-1):
            if self.adj_matrix[path[i]][path[i+1]] < amount:
                if print_error:
                    print("transaction failure: insufficient funds along shortest path")
                return

        for i in range(len(path)-1):
            id1 = self.contract.functions.getIdFromIndex(path[i]).call()
            id2 = self.contract.functions.getIdFromIndex(path[i+1]).call()
            try:
                self.contract.functions.sendAmount(id1, id2, amount).transact({'from':self.from_acc})
                # if succeeds, modify the adj_matrix maintained in client
                self.adj_matrix[id1][id2] -= amount
                self.adj_matrix[id2][id1] += amount
            except:
                if print_error:
                    print("transaction failure: contract function raised an exception")
                return False
        
        return True

    def closeAccount(self, user_id_1, user_id_2, from_acc):
        self.contract.functions.closeAccount(user_id_1, user_id_2).transact({'from':from_acc})


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
    deployed_contract_address = '0xd42383151bE5FF14210dEdE8f548Ef0B6b584F86'

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

    interact_obj = Interact(contract=contract, from_acc=w3.eth.accounts[0])

    # register users

    for i in range(num_users):
        interact_obj.registerUser(i, f"user{i}")
    user_ids = list(range(num_users))

    # create connected graph, and joint accounts

    # NOTE: we use networkx module to create a graph
    # according to power-law degree distribution

    graph = nx.powerlaw_cluster_graph(n=100, m=5, p=0.3)
    while not nx.is_connected(graph):
        graph = nx.powerlaw_cluster_graph(n=100, m=5, p=0.3)
    
    for edge in graph.edges:
        interact_obj.createAcc(edge[0], edge[1])   # mean balance: 10
    
    # get matrix
    interact_obj.get_matrix()

    # perform transactions

    successful_in_this_interval = 0
    successful_total = 0

    for i in range(num_txns):
        print(i)
        user_1, user_2 = random.sample(user_ids, k=2)
        if interact_obj.sendAmount(user_1, user_2, amount=1):
            successful_in_this_interval += 1
            successful_total += 1
        if i % ratio_interval == (ratio_interval-1):
            ratios[i+1] = successful_in_this_interval/ratio_interval
            ratios_moving[i+1] = successful_total/(i+1)
            successful_in_this_interval = 0
    
    # plot

    ratios = dict(sorted(ratios.items()))
    ratios_moving = dict(sorted(ratios_moving.items()))
    print(f"{ratios=}")
    print(f"{ratios_moving=}")

    # ratios={100: 0.78, 200: 0.84, 300: 0.83, 400: 0.82, 500: 0.81, 600: 0.8, 700: 0.76, 800: 0.7, 900: 0.73, 1000: 0.74}
    # ratios_moving={100: 0.78, 200: 0.81, 300: 0.8166666666666667, 400: 0.8175, 500: 0.816, 600: 0.8133333333333334, 700: 0.8057142857142857, 800: 0.7925, 900: 0.7855555555555556, 1000: 0.781}
    
    (fig, ax) = plt.subplots()
    ax.plot(ratios.keys(), ratios.values(), marker='o', label='Ratio')
    ax.plot(ratios_moving.keys(), ratios_moving.values(), marker='o', label='Moving Ratio')
    ax.set_ylim(0,1)
    ax.legend()
    fig.savefig("plot_ratios.png", bbox_inches="tight")