import json
from web3 import Web3
import numpy as np

#connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)
#check if ethereum is connected
print(w3.is_connected())

#replace the address with your contract address (!very important)
deployed_contract_address = '0xd8d8Fcf5268e19beA74456a38FA4E631bbE1a624'

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

# print(list(contract.functions))

# contract.functions.registerUser(1,"user1").transact({'from':w3.eth.accounts[0]})
# contract.functions.registerUser(5,"user5").transact({'from':w3.eth.accounts[0]})
# contract.functions.registerUser(7,"user7").transact({'from':w3.eth.accounts[0]})

# contract.functions.createAcc(1,5,20).transact({'from':w3.eth.accounts[0]})
# contract.functions.createAcc(5,7,10).transact({'from':w3.eth.accounts[0]})
# contract.functions.sendAmount(1,5,3).transact({'from':w3.eth.accounts[0]})

edges = contract.functions.getEdges().call()
print(edges)

# txn_receipt_json = json.loads(w3.to_json(txn_receipt))
# print(txn_receipt) # print transaction hash

def registerUser(user_id, user_name, contract, from_acc):
    contract.functions.registerUser(user_id, user_name).transact({'from':from_acc})

def createAcc(user_id_1, user_id_2, contract, from_acc, total_balance=None, mean_balance=10):
    if total_balance is None:
        total_balance = int(np.random.exponential(scale=mean_balance))
        if total_balance%2 == 1:
            total_balance += 1
    assert total_balance%2 == 0
    contract.functions.createAcc(user_id_1, user_id_2).transact({'from':from_acc})

def sendAmount(user_id_1, user_id_2, contract, from_acc, amount=1):
    edges = contract.functions.getEdges().call()
    index_1 = contract.functions.getIndexFromId(user_id_1).call()
    index_2 = contract.functions.getIndexFromId(user_id_2).call()
    pass

def closeAccount(user_id_1, user_id_2, contract, from_acc):
    contract.functions.closeAccount(user_id_1, user_id_2).transact({'from':from_acc})