'''Import main, Txn, Blk, Event and Simulator'''
import main
from txn import Txn
from block import Blk
from event import Event
from simulator import Simulator

import numpy as np

class Peer:
    '''Peer'''

    # genesis block
    genesis = Blk(None,None,[])
    n = main.n

    # construct peer
    def __init__(self, pid):
        '''constructor'''
        self.pid = pid
        self.slow = False
        self.low = False
        self.curr_balance = []
        self.latest_blk = Peer.genesis
        self.curr_tree = set()
        self.curr_tree.add(Peer.genesis)
        self.alpha = 0
        self.txn_all = set()
        self.txn_exc = set()
        self.txn_sent = {}
        self.blk_all = set()
        self.blk_exc = set()
        self.blk_sent = {}

    # generate txn
    def generate_txn(self, sim:Simulator, eve:Event):
        '''create a txn'''
        idy = np.random.choice(Peer.n)
        invalid = np.random.uniform(0.0,1.0) < 0.1
        if invalid:
            amt = self.curr_balance[self.pid] + np.random.uniform(1e-8,10.0)
        else:
            amt = np.random.uniform(0.0,self.curr_balance[self.pid])
        txn = Txn(self.pid,False,idy,amt)
        self.txn_all.add(txn.txn_id)
        self.txn_exc.add(txn.txn_id)
        self.txn_sent[txn.txn_id] = set()
        fwd_eve = Event(eve.timestamp,2,self,txn,self)
        sim.push(fwd_eve)
        time_txn = np.random.exponential(1.0/sim.Ttx)
        if eve.timestamp + time_txn < sim.T:
            next_eve = Event(eve.timestamp + time_txn,1,self)
            sim.push(next_eve)

    # forward txn
    def forward_txn(self, sim:Simulator, eve:Event):
        '''forward a txn'''
        pass

    # hear txn
    def hear_txn(self, sim:Simulator, eve:Event):
        '''hear a txn'''
        pass

    # generate txn
    def generate_blk(self, sim:Simulator, eve:Event):
        '''create a blk'''
        pass

    # forward txn
    def forward_blk(self, sim:Simulator, eve:Event):
        '''forward a blk'''
        pass

    # hear txn
    def hear_blk(self, sim:Simulator, eve:Event):
        '''hear a blk'''
        pass

    # update tree
    def update_tree(self, sim:Simulator, eve:Event):
        '''update peer tree'''
        pass
