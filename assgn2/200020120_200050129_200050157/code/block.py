'''Import Txn'''
from __future__ import annotations
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
        Blk.blk_i2p[self.blk_id] = self # id to blk
        Blk.curr_blk_id += 1 # global counter

    # update parent
    def update_parent(self, parent):
        '''update parent of block'''
        if parent is not None:
            self.pid = parent.blk_id
            parent.children.add(self) # build tree
            self.height = parent.height + 1
        else:
            self.pid = -1
            self.height = 0 # genesis
            self.children = set()
