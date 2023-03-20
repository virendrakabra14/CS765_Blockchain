'''Import Txn and Blk'''
from txn import Txn
from block import Blk

class Event:
    '''Event'''

    # construct event
    def __init__(self, timestamp, typ, peer = None, txn:Txn = None, fro = None,
                 blk:Blk = None):
        '''constructor'''
        self.timestamp = timestamp
        self.type = typ
        self.peer = peer
        self.txn = txn
        self.fro = fro
        self.blk = blk

    def __lt__(self, eve2):
        return self.timestamp<eve2.timestamp
    def __le__(self, eve2):
        return self.timestamp<=eve2.timestamp

    # runner
    def run(self, sim):
        '''event runner'''
        # print(f'Running event {self.type}')
        if self.type == 1:
            self.peer.generate_txn(sim, self)
        elif self.type == 2:
            self.peer.forward_txn(sim, self)
        elif self.type == 3:
            self.peer.hear_txn(sim, self)
        elif self.type == 4:
            print(f'Running event {self.type} (peer {self.peer.pid})')
            self.peer.generate_blk(sim, self)
        elif self.type == 5:
            # print(f'Running event {self.type} (peer {self.peer.pid})')
            self.peer.forward_blk(sim, self)
        elif self.type == 6:
            # print(f'Running event {self.type} (peer {self.peer.pid})')
            self.peer.hear_blk(sim, self)
        elif self.type == 7:
            self.peer.update_tree(sim, self)
