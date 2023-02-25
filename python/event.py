'''Import Txn, Blk, Peer and Simulator'''
from txn import Txn
from block import Blk
from peer import Peer
from simulator import Simulator

class Event:
    '''Event'''

    # construct event
    def __init__(self, timestamp, typ, peer:Peer, txn:Txn, fro:Peer, blk:Blk):
        '''constructor'''
        self.timestamp = timestamp
        self.type = typ
        self.peer = peer
        self.txn = txn
        self.fro = fro
        self.blk = blk

    # runner
    def run(self, sim:Simulator):
        '''event runner'''
        if self.type == 1:
            self.peer.generate_txn(sim, self)
        elif self.type == 2:
            self.peer.forward_txn(sim, self)
        elif self.type == 3:
            self.peer.hear_txn(sim, self)
        elif self.type == 4:
            self.peer.generate_blk(sim, self)
        elif self.type == 5:
            self.peer.forward_blk(sim, self)
        elif self.type == 6:
            self.peer.hear_blk(sim, self)
        elif self.type == 7:
            self.peer.update_tree(sim, self)
