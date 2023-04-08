import json
from web3 import Web3


#connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)
#check if ethereum is connected
print(w3.is_connected())

#replace the address with your contract address (!very important)
deployed_contract_address = '0x2c94dF115E576bEF004E2Fe5780B4905235d17f3'

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

#Add your Code here

print(list(contract.functions))

# # tx_hash = contract.functions.set_balance(1200).transact({'from':w3.eth.accounts[0]})
contract.functions.registerUser(1,"user1").call()
contract.functions.registerUser(5,"user5").call()
contract.functions.registerUser(7,"user7").call()

txn_receipt = contract.functions.getEdges().call()
print(txn_receipt)

# txn_receipt_json = json.loads(w3.to_json(txn_receipt))
# print(txn_receipt) # print transaction hash