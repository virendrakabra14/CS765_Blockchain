class Blk:
    
    curr_blk_id = 0
    max_blk_size = 8 * (2 ** 20)
    blk_i2p = {}
    
    def __init__(self, miner, parent, txns):
        self.blk_id = Blk.curr_blk_id
        Blk.curr_blk_id += 1
        self.blk_size = 0
        self.miner = miner
        self.txns = txns
        self.invalid = False
        self.update_parent(parent)
    
    def update_parent(self, parent):
        self.parent = parent
        if (parent is not None):
            parent.children.add(self)
            self.height = parent.height + 1
        else:
            self.height = 0
            self.children = set()