import main

class Txn:
    
    curr_txn_id = 0
    txn_size = 8 * (2 ** 10)
    coinbase_fee = 50
    n = main.n
    
    def __init__(self, idx, coinbase = False, idy = -1, C = -1):
        assert(idx >= 0 and idx <= Txn.n)
        self.txn_id = Txn.curr_txn_id
        Txn.curr_txn_id += 1
        self.idx = idx
        self.idy = idy
        self.coinbase = coinbase
        self.C = Txn.coinbase_fee if coinbase else C
