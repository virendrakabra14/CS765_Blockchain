'''Import defaults, main, Txn, Blk, Event and Simulator'''
from copy import copy, deepcopy
import numpy as np
import main
from txn import Txn
from block import Blk
from event import Event
from simulator import Simulator

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
        self.blk_all = {}
        self.blk_exc = set()
        self.blk_trig = set()
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
        for pid in sim.adj[self.pid]:
            if pid != self.pid and pid != eve.fro.pid and pid not in self.txn_sent[eve.txn.txn_id]:
                self.txn_sent[eve.txn.txn_id].add(pid)
            link_speed = sim.sls if self.slow or sim.peers[pid].slow else sim.fls
            queuing_delay = np.random.exponential(link_speed/sim.qdn)
            latency = sim.rho[self.pid][pid] + queuing_delay + eve.txn.txn_size/link_speed
            hear_eve = Event(eve.timestamp + latency,3,sim.peers[pid],eve.txn,self)
            sim.push(hear_eve)

    # hear txn
    def hear_txn(self, sim:Simulator, eve:Event):
        '''hear a txn'''
        tid = eve.txn.txn_id
        if tid not in self.txn_all:
            self.txn_all.add(tid)
            self.txn_exc.add(tid)
            self.txn_sent[tid] = set()
            fwd_eve = Event(eve.timestamp,2,self,eve.txn,eve.fro)
            sim.push(fwd_eve)

    # generate txn
    def generate_blk(self, sim:Simulator, eve:Event):
        '''create a blk'''
        invalid = np.random.uniform(0.0,1.0) < 0.1
        blk_txns = set()
        cb_txn = Txn(self.pid,True,-1,Txn.coinbase_fee)
        self.txn_all.add(cb_txn.txn_id)
        blk_txns.add(cb_txn.txn_id)
        blk_size = cb_txn.txn_size
        self.curr_balance[cb_txn.idx] += cb_txn.amt
        blk = Blk(self,None,blk_txns)
        if invalid:
            for tid in self.txn_exc:
                txn = Txn.txn_i2p[tid]
                if not self.check_bal() or blk_size + txn.txn_size > Blk.max_blk_size:
                    if not self.check_bal():
                        blk.invalid = True
                    blk.update_parent(self.latest_blk)
                    blk.txns = blk_txns
                    break
                blk_size += txn.txn_size
                blk_txns.add(tid)
                if txn.idy == -1:
                    self.curr_balance[txn.idx] += txn.amt
                else:
                    self.curr_balance[txn.idx] -= txn.amt
                    self.curr_balance[txn.idx] += txn.amt
            if blk.parent is None:
                blk.update_parent(self.latest_blk)
                blk.txns = deepcopy(self.txn_exc)
        else:
            invalids = set()
            for tid in self.txn_exc:
                txn = Txn.txn_i2p[tid]
                if blk_size + txn.txn_size > Blk.max_blk_size:
                    blk.update_parent(self.latest_blk)
                    blk.txns = blk_txns
                    break
                blk_size += txn.txn_size
                blk_txns.add(tid)
                if txn.idy == -1:
                    self.curr_balance[txn.idx] += txn.amt
                else:
                    self.curr_balance[txn.idx] -= txn.amt
                    self.curr_balance[txn.idx] += txn.amt
                if not self.check_bal():
                    invalids.add(tid)
                    blk_size -= txn.txn_size
                    blk_txns.remove(tid)
                    if txn.idy == -1:
                        self.curr_balance[txn.idx] -= txn.amt
                    else:
                        self.curr_balance[txn.idx] += txn.amt
                        self.curr_balance[txn.idx] -= txn.amt
            if blk.parent is None:
                blk.update_parent(self.latest_blk)
                for tid in self.txn_exc:
                    if tid not in invalids:
                        blk.txns.add(tid)
        self.latest_blk = blk
        blk.blk_size = blk_size
        self.blk_all[blk.blk_id] = eve.timestamp
        self.blk_sent[blk.blk_id] = set()
        for tid in blk.txns:
            self.txn_exc.remove(tid)
        blk_gen_delay = np.random.exponential(self.alpha/sim.Tblk)
        fwd_eve = Event(eve.timestamp + blk_gen_delay,5,self,None,self,blk)
        sim.push(fwd_eve)
        if eve.timestamp + blk_gen_delay < sim.T:
            mine = Event(eve.timestamp + blk_gen_delay,4,self)
            sim.push(mine)

    # forward txn
    def forward_blk(self, sim:Simulator, eve:Event):
        '''forward a blk'''
        blk = eve.blk
        if (blk.miner.pid == self.pid and blk == self.latest_blk) or blk.parent in self.curr_tree:
            for pid in sim.adj[self.pid]:
                if pid != self.pid and pid != eve.fro.pid and pid not in self.blk_sent[blk.blk_id]:
                    self.blk_sent[blk.blk_id].add(pid)
                    link_speed = sim.sls if self.slow or sim.peers[pid].slow else sim.fls
                    queuing_delay = np.random.exponential(link_speed/sim.qdn)
                    latency = sim.rho[self.pid][pid] + queuing_delay + blk.blk_size/link_speed
                    hear_eve = Event(eve.timestamp + latency,6,sim.peers[pid],None,self,blk)
                    sim.push(hear_eve)

    # hear txn
    def hear_blk(self, sim:Simulator, eve:Event):
        '''hear a blk'''
        blk = eve.blk
        if blk.blk_id not in self.blk_all:
            self.blk_all[blk.blk_id] = eve.timestamp
            self.blk_exc.add(blk.blk_id)
            for tid in blk.txns:
                self.txn_all.add(tid)
                self.txn_exc.add(tid)
            self.blk_sent[blk.blk_id] = set()
            if blk.parent in self.curr_tree:
                tree = Event(eve.timestamp,7,self)
                sim.push(tree)

    # update tree
    def update_tree(self, sim:Simulator, eve:Event):
        '''update peer tree'''
        curr_chain = set()
        bptr = copy(self.latest_blk)
        while bptr is not None:
            curr_chain.add(bptr)
            for tid in bptr.txns:
                self.txn_exc.remove(tid)
            bptr = bptr.parent
        if self.latest_blk not in self.curr_tree:
            for blk in curr_chain:
                self.curr_tree.add(blk)
        for blk in curr_chain:
            for tid in blk.txns:
                txn = Txn.txn_i2p[tid]
                if txn.idy == -1:
                    self.curr_balance[txn.idx] -= txn.amt
                else:
                    self.curr_balance[txn.idx] += txn.amt
                    self.curr_balance[txn.idx] -= txn.amt
                self.txn_exc.add(tid)
        pending = True
        while pending:
            temp_inc = set()
            for bid in self.blk_exc:
                blk = Blk.blk_i2p[bid]
                if not self.check_blk(blk):
                    continue
                if blk.parent is None or blk.parent in self.curr_tree:
                    blk.update_parent(blk.parent)
                    self.curr_tree.add(blk)
                    fwd_eve = Event(eve.timestamp,5,self,None,self,blk)
                    sim.push(fwd_eve)
                    temp_inc.add(bid)
            for bid in temp_inc:
                self.blk_exc.remove(bid)
            pending = False
            temp_inc = set()
            for bid in self.blk_exc:
                blk = Blk.blk_i2p[bid]
                if not self.check_blk(blk):
                    continue
                if blk.parent is None or blk.parent in self.curr_tree:
                    pending = True
                    break
        new_tree = sorted(self.curr_tree, key = lambda x: x.height, reversed = True)
        last = self.latest_blk
        for blk in new_tree:
            if blk.height > self.latest_blk.height:
                bptr = blk
                temp_bal = deepcopy(self.curr_balance)
                while bptr is not None:
                    for tid in bptr.txns:
                        txn = Txn.txn_i2p[tid]
                        if txn.idy == -1:
                            temp_bal[txn.idx] += txn.amt
                        else:
                            temp_bal[txn.idx] -= txn.amt
                            temp_bal[txn.idx] += txn.amt
                    bptr = bptr.parent
                for bal in temp_bal:
                    if bal < 0:
                        break
                else:
                    last = blk
                    break
            else:
                break
        bptr = last
        while bptr is not None:
            for tid in bptr.txns:
                txn = Txn.txn_i2p[tid]
                if txn.idy == -1:
                    temp_bal[txn.idx] += txn.amt
                else:
                    temp_bal[txn.idx] -= txn.amt
                    temp_bal[txn.idx] += txn.amt
                self.txn_exc.remove(tid)
            bptr = bptr.parent
        self.latest_blk = last

    # print txns
    def print_txns(self):
        '''print txns'''
        print(f'Peer {self.pid} txns:')
        for tid in self.txn_all:
            print(tid, end = ' ')
        print()

    # print longest chain
    def print_lc(self):
        '''longest chain'''
        print(f'Peer {self.pid} longest chain:')
        bptr = self.latest_blk
        while bptr is not None:
            print(f'{bptr.blk_id} -> ', end = '')
            bptr = bptr.parent
        print()

    # invalidity of balance
    def check_bal(self):
        '''check balances'''
        for bal in self.curr_balance:
            if bal < 0:
                return False
        return True

    # check blk from genesis
    def check_blk(self, blk):
        '''check validity of block'''
        temp_bal = [0 for _ in range(main.n)]
        while blk is not None:
            for tid in blk.txns:
                txn = Txn.txn_i2p[tid]
                if txn.idy == -1:
                    temp_bal[txn.idx] += txn.amt
                else:
                    temp_bal[txn.idx] -= txn.amt
                    temp_bal[txn.idy] += txn.amt
            blk = blk.parent
        for bal in temp_bal:
            if bal < 0:
                return False
        return True
