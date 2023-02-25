'''Import main'''
import main

class Txn:
    '''Transaction'''

    # shared variables
    curr_txn_id = 0
    txn_size = 8 * (2 ** 10)
    coinbase_fee = 50
    n = main.n

    # construct txn
    def __init__(self, idx, coinbase = False, idy = -1, amt = -1):
        '''constructor'''
        assert(idx >= 0 and idx <= Txn.n)
        self.txn_id = Txn.curr_txn_id
        Txn.curr_txn_id += 1
        self.idx = idx
        self.idy = idy
        self.coinbase = coinbase
        self.amt = Txn.coinbase_fee if coinbase else amt
