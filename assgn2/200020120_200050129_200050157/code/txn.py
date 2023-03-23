class Txn:
    '''Transaction'''

    # shared variables
    curr_txn_id = 0
    txn_size = 8 * (2 ** 10)
    coinbase_fee = 50
    txn_i2p = {}

    # construct txn
    def __init__(self, idx, coinbase = False, idy = -1, amt = -1):
        '''constructor'''
        self.txn_id = Txn.curr_txn_id
        self.idx = idx
        self.idy = idy
        self.coinbase = coinbase
        self.amt = Txn.coinbase_fee if coinbase else amt
        Txn.txn_i2p[self.txn_id] = self # id to txn
        Txn.curr_txn_id += 1 # global counter
