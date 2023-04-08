import json
from web3 import Web3
import numpy as np

#connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)
#check if ethereum is connected
print(w3.is_connected())

#replace the address with your contract address (!very important)
deployed_contract_address = '0xb35A46Fb54C0216AeC0D3eb0f3Fd44f06be43d7C'

#path of the contract json file. edit it with your contract json file
compiled_contract_path ="build/contracts/Payment.json"
with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']
contract = w3.eth.contract(address = deployed_contract_address, abi = contract_abi)

'''
#Calling a contract function createAcc(uint,uint,uint)
txn_receipt = contract.functions.createAcc(1, 2, 5).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
txn_receipt_json = json.loads(w3.to_json(txn_receipt))
print(txn_receipt_json) # print transaction hash

# print block info that has the transaction)
print(w3.eth.get_transaction(txn_receipt_json)) 

#Call a read only contract function by replacing transact() with call()

'''

def registerUser(user_id, user_name, contract, from_acc):
    contract.functions.registerUser(user_id, user_name).transact({'from':from_acc})

def createAcc(user_id_1, user_id_2, contract, from_acc, total_balance=None, mean_balance=10):
    if total_balance is None:
        total_balance = int(np.random.exponential(scale=mean_balance))
        if total_balance%2 == 1:        # extra (for equal division)
            total_balance += 1
    assert total_balance%2 == 0
    contract.functions.createAcc(user_id_1, user_id_2, total_balance).transact({'from':from_acc})

def sendAmount(user_id_1, user_id_2, contract, from_acc, amount=1):
    edges = contract.functions.getEdges().call()
    num_nodes = len(edges)
    index_1 = contract.functions.getIndexFromId(user_id_1).call()
    index_2 = contract.functions.getIndexFromId(user_id_2).call()

    if index_1>=num_nodes or index_2>=num_nodes:
        print("transaction failure: nodes not present")
        return
    
    visited = [-1 for i in range(num_nodes)]    # works as both `visited` and `distance` arrays
    parents = [set() for i in range(num_nodes)]
    queue = []

    queue.append(index_1)
    visited[index_1] = 0

    # https://stackoverflow.com/questions/20257227/
    while not len(queue) == 0:
        node = queue.pop(0)
        for i in range(num_nodes):
            if edges[node][i] >= amount:        # if only optimal paths to be considered,
                                                # change `amount` to 1
                                                # (anyways, `amount` is always 1 in doc)
                if visited[i] == -1:
                    visited[i] = visited[node]+1
                    parents[i].add(node)
                    queue.append(i)
                else:
                    if visited[i] == visited[node]-1:
                        parents[node].add(i)    # capture ALL shortest paths
        if node == index_2:
            break

    path = []
    node = index_2
    while node != index_1:
        path.insert(0, node)
        if len(parents[node]) == 0:
            print("transaction failure: no path found")
            return
        node = list(parents[node])[0]
    path.insert(0, index_1)

    for i in range(len(path)-1):
        id1 = contract.functions.getIdFromIndex(path[i]).call()
        id2 = contract.functions.getIdFromIndex(path[i+1]).call()
        contract.functions.sendAmount(id1, id2, amount).transact({'from':from_acc})

def closeAccount(user_id_1, user_id_2, contract, from_acc):
    contract.functions.closeAccount(user_id_1, user_id_2).transact({'from':from_acc})

###

# print(list(contract.functions))


# registerUser(1, "user1", contract, w3.eth.accounts[0])    # use register, createAcc operations once
# registerUser(5, "user5", contract, w3.eth.accounts[0])
# registerUser(7, "user7", contract, w3.eth.accounts[0])
# createAcc(1, 5, contract, w3.eth.accounts[0], 20)
# createAcc(5, 7, contract, w3.eth.accounts[0], 10)

# sendAmount(1, 7, contract, w3.eth.accounts[0], 1)

edges = contract.functions.getEdges().call()
print(edges)

# txn_receipt_json = json.loads(w3.to_json(txn_receipt))
# print(txn_receipt) # print transaction hash