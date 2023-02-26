'''Import Txn'''
from txn import Txn

class Blk:
    '''Block'''

    # shared variables
    curr_blk_id = 0
    max_blk_size = 8 * (2 ** 20)
    blk_i2p = {}

    # construct blk
    def __init__(self, miner, parent, txns:list[Txn]):
        '''constructor'''
        self.blk_id = Blk.curr_blk_id
        self.blk_size = 0
        self.miner = miner
        self.txns = txns
        self.invalid = False
        self.update_parent(parent)
        Blk.blk_i2p[self.blk_id] = self
        Blk.curr_blk_id += 1

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
