'''Import Txn and Peer'''
from txn import Txn
from peer import Peer

class Blk:
    '''Block'''

    # shared variables
    curr_blk_id = 0
    max_blk_size = 8 * (2 ** 20)
    blk_i2p = {}

    # construct blk
    def __init__(self, miner:Peer, parent, txns:Txn):
        '''constructor'''
        self.blk_id = Blk.curr_blk_id
        Blk.curr_blk_id += 1
        self.blk_size = 0
        self.miner = miner
        self.txns = txns
        self.invalid = False
        self.update_parent(parent)

    # update parent
    def update_parent(self, parent):
        '''update parent of block'''
        self.parent = parent
        if parent is not None:
            parent.children.add(self)
            self.height = parent.height + 1
        else:
            self.height = 0
            self.children = set()
