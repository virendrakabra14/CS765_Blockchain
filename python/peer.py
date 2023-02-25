'''Import Txn, Blk, Event and Simulator'''
from txn import Txn
from block import Blk
from event import Event
from simulator import Simulator

class Peer:
    '''Peer'''

    # genesis block
    genesis = Blk(None,None,[])

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

    # generate txn
    def generate_txn(self, sim:Simulator, eve:Event):
        '''create a txn'''
        pass

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
