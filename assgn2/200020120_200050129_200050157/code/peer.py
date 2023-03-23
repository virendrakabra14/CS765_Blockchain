'''Import defaults, Txn, Blk and Event'''
from io import TextIOWrapper
from copy import copy, deepcopy
import numpy as np
from txn import Txn
from block import Blk
from event import Event

class Peer:
    '''Peer'''

    # genesis block
    genesis = Blk(None,None,[])
    n = 0
    adv_blks = 0        # number of blocks created by adversary

    # construct peer
    def __init__(self, n, pid):
        '''constructor'''
        self.n = n
        self.pid = pid
        self.adv = False
        self.slow = False
        self.low = False
        self.curr_balance = [0 for _ in range(n)]
        self.latest_blk = Peer.genesis
        self.own_chain = []
        self.curr_tree = set()
        self.curr_tree.add(Peer.genesis.blk_id)
        self.alpha = 0
        self.txn_all = set()
        self.txn_exc = set()
        self.txn_sent = {}
        self.blk_all = {0:0}
        self.blk_exc = set()        # blocks excluded from the tree
        self.blk_trig = set()       # trigger set
        self.blk_sent = {}

    # generate txn
    def generate_txn(self, sim, eve:Event):
        '''create a txn'''
        idy = np.random.choice(self.n)
        invalid = np.random.uniform(0.0,1.0) < 0.1
        if invalid:
            amt = self.curr_balance[self.pid] + np.random.uniform(1e-8,10.0)
        else:
            amt = np.random.uniform(0.0,self.curr_balance[self.pid])
        txn = Txn(self.pid,False,idy,amt)
        self.txn_all.add(txn.txn_id)
        self.txn_exc.add(txn.txn_id)
        self.txn_sent.setdefault(txn.txn_id,set())
        # create forwarding event
        fwd_eve = Event(eve.timestamp,2,self,txn,self)
        sim.push(fwd_eve)
        time_txn = np.random.exponential(sim.Ttx)
        # set next generation
        if eve.timestamp + time_txn < sim.T:
            next_eve = Event(eve.timestamp + time_txn,1,self)
            sim.push(next_eve)

    # forward txn
    def forward_txn(self, sim, eve:Event):
        '''forward a txn'''
        for pid in sim.adj[self.pid]:
            # check whom to forward
            if pid != self.pid and pid != eve.fro.pid and pid not in self.txn_sent[eve.txn.txn_id]:
                self.txn_sent.setdefault(eve.txn.txn_id,set())
                self.txn_sent[eve.txn.txn_id].add(pid)
            # calculate delay
            link_speed = sim.sls if self.slow or sim.peers[pid].slow else sim.fls
            queuing_delay = np.random.exponential(sim.qdn/link_speed)
            latency = sim.rho[self.pid][pid] + queuing_delay + eve.txn.txn_size/link_speed
            # set hear event
            hear_eve = Event(eve.timestamp + latency,3,sim.peers[pid],eve.txn,self)
            sim.push(hear_eve)

    # hear txn
    def hear_txn(self, sim, eve:Event):
        '''hear a txn'''
        tid = eve.txn.txn_id
        if tid not in self.txn_all:
            self.txn_all.add(tid)
            self.txn_exc.add(tid)
            self.txn_sent.setdefault(tid,set())
            # set forward event
            fwd_eve = Event(eve.timestamp,2,self,eve.txn,eve.fro)
            sim.push(fwd_eve)

    # generate blk
    def generate_blk(self, sim, eve:Event):
        '''create a blk'''
        invalid = np.random.uniform(0.0,1.0) < 0.1
        blk_txns = set()
        # coinbase for miner
        cb_txn = Txn(self.pid,True,-1,Txn.coinbase_fee)
        self.txn_all.add(cb_txn.txn_id)
        self.txn_exc.add(cb_txn.txn_id)
        blk_txns.add(cb_txn.txn_id)
        blk_size = cb_txn.txn_size
        temp_bal = [0 for _ in range(self.n)]
        temp_bal[cb_txn.idx] += cb_txn.amt
        blk = Blk(self,None,blk_txns)
        if invalid:
            # generate invalid block
            blk.invalid = True
            for tid in self.txn_exc:
                txn = Txn.txn_i2p[tid]
                # still check for block size
                if not self.check_bal(temp_bal) or blk_size + txn.txn_size > Blk.max_blk_size:
                    if not self.check_bal(temp_bal):
                        blk.invalid = True
                    blk.update_parent(self.latest_blk)
                    blk.txns = blk_txns
                    break
                blk_size += txn.txn_size
                blk_txns.add(tid)
                if txn.idy == -1:
                    temp_bal[txn.idx] += txn.amt
                else:
                    temp_bal[txn.idx] -= txn.amt
                    temp_bal[txn.idy] += txn.amt
            # attach block to genesis
            if blk.pid == -1:
                blk.update_parent(self.latest_blk)
                blk.txns = deepcopy(self.txn_exc)
        else:
            # create valid block
            invalids = set()
            for tid in self.txn_exc:
                txn = Txn.txn_i2p[tid]
                # check block size
                if blk_size + txn.txn_size > Blk.max_blk_size:
                    blk.update_parent(self.latest_blk)
                    blk.txns = blk_txns
                    break
                blk_size += txn.txn_size
                blk_txns.add(tid)
                if txn.idy == -1:
                    temp_bal[txn.idx] += txn.amt
                else:
                    temp_bal[txn.idx] -= txn.amt
                    temp_bal[txn.idy] += txn.amt
                # invalid so remove txn
                if not self.check_bal(temp_bal):
                    invalids.add(tid)
                    blk_size -= txn.txn_size
                    blk_txns.remove(tid)
                    if txn.idy == -1:
                        temp_bal[txn.idx] -= txn.amt
                    else:
                        temp_bal[txn.idx] += txn.amt
                        temp_bal[txn.idy] -= txn.amt
            if blk.pid == -1:
                blk.update_parent(self.latest_blk)
                for tid in self.txn_exc:
                    if tid not in invalids:
                        blk.txns.add(tid)
        # add block to chain
        self.latest_blk = blk
        if self.adv:
            Peer.adv_blks += 1
            self.own_chain.append(blk)
        blk.blk_size = blk_size
        self.blk_all[blk.blk_id] = eve.timestamp
        self.blk_sent.setdefault(blk.blk_id,set())
        for tid in blk.txns:
            self.txn_exc.remove(tid)
        # update balance
        self.curr_balance = temp_bal
        # generation delay
        blk_gen_delay = np.random.exponential(sim.Tblk/self.alpha)
        if not self.adv:
            # forward if regular peer
            fwd_eve = Event(eve.timestamp + blk_gen_delay,5,self,None,self,blk)
            sim.push(fwd_eve)
            print(eve.timestamp,blk_gen_delay,sim.T)
        # back to mining
        if eve.timestamp + blk_gen_delay < sim.T:
            mine = Event(eve.timestamp + blk_gen_delay,4,self)
            sim.push(mine)

    # forward blk
    def forward_blk(self, sim, eve:Event):
        '''forward a blk'''
        blk = eve.blk
        # check whom to forward
        if (self.adv and blk.miner.pid == self.pid) or (not self.adv and
            ((blk.miner.pid == self.pid and blk == self.latest_blk) or
            blk.pid in self.curr_tree)):
            for pid in sim.adj[self.pid]:
                # prevent looping
                if pid != self.pid and pid != eve.fro.pid and pid not in self.blk_sent[blk.blk_id]:
                    self.blk_sent.setdefault(blk.blk_id,set())
                    self.blk_sent[blk.blk_id].add(pid)
                    # calculate delay
                    link_speed = sim.sls if self.slow or sim.peers[pid].slow else sim.fls
                    queuing_delay = np.random.exponential(sim.qdn/link_speed)
                    latency = sim.rho[self.pid][pid] + queuing_delay + blk.blk_size/link_speed
                    # set hear event
                    hear_eve = Event(eve.timestamp + latency,6,sim.peers[pid],None,self,blk)
                    sim.push(hear_eve)

    # hear blk
    def hear_blk(self, sim, eve:Event):
        '''hear a blk'''
        blk = eve.blk
        if not self.adv:
            # honest
            if blk.blk_id not in self.blk_all:
                self.blk_all[blk.blk_id] = eve.timestamp
                self.blk_exc.add(blk.blk_id)
                for tid in blk.txns:
                    self.txn_all.add(tid)
                    self.txn_exc.add(tid)
                self.blk_sent.setdefault(blk.blk_id,set())
                if blk.blk_id in self.blk_trig or blk.pid in self.curr_tree:
                    tree = Event(eve.timestamp,7,self)
                    sim.push(tree)
                else:
                    self.blk_trig.add(blk.pid)
        else:
            # adversary
            if blk.blk_id not in self.blk_all:
                self.blk_all[blk.blk_id] = eve.timestamp
                self.blk_exc.add(blk.blk_id)
                for tid in blk.txns:
                    self.txn_all.add(tid)
                    self.txn_exc.add(tid)
                self.blk_sent.setdefault(blk.blk_id,set())
            # take action based on lead
            while len(self.own_chain) != 0 and blk.height >= self.own_chain[0].height:
                fwd_eve = Event(eve.timestamp,5,self,None,self,self.own_chain.pop(0))
                sim.push(fwd_eve)
                print(eve.timestamp,sim.T)
            last = self.latest_blk
            if blk.height == last.height:
                tree = Event(eve.timestamp,7,self)
                sim.push(tree)
            elif sim.mode == 'selfish' and blk.height == last.height - 1:
                fwd_eve = Event(eve.timestamp,5,self,None,self,last)
                sim.push(fwd_eve)
                print(eve.timestamp,sim.T)
                self.own_chain = []

    # update tree
    def update_tree(self, sim, eve:Event):
        '''update peer tree'''
        curr_chain = set()
        bptr = copy(self.latest_blk)
        txns_inc = set()
        # traverse current chain
        while bptr.blk_id != 0:
            curr_chain.add(bptr)
            for tid in bptr.txns:
                txns_inc.add(tid)
            bptr = Blk.blk_i2p[bptr.pid]
        for tid in txns_inc:
            if tid in self.txn_exc:
                self.txn_exc.remove(tid)
        # ensure current chain in tree
        if self.latest_blk.blk_id not in self.curr_tree:
            for blk in curr_chain:
                self.curr_tree.add(blk.blk_id)
        # roll back
        for blk in curr_chain:
            for tid in blk.txns:
                txn = Txn.txn_i2p[tid]
                if txn.idy == -1:
                    self.curr_balance[txn.idx] -= txn.amt
                else:
                    self.curr_balance[txn.idx] += txn.amt
                    self.curr_balance[txn.idy] -= txn.amt
                self.txn_exc.add(tid)
        # check new addition of blocks
        pending = True
        while pending:
            temp_inc = set()
            for bid in self.blk_exc:
                blk = Blk.blk_i2p[bid]
                if not self.check_blk(blk):
                    continue
                if blk.pid == -1 or blk.pid in self.curr_tree:
                    blk.update_parent(Blk.blk_i2p[blk.pid])
                    self.curr_tree.add(blk.blk_id)
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
                if Blk.blk_i2p[blk.pid] is None or blk.pid in self.curr_tree:
                    pending = True
                    break
        for bid in self.curr_tree:
            if bid in self.blk_trig:
                self.blk_trig.remove(bid)
        # sort the tree
        new_tree = sorted(self.curr_tree, key = lambda x: Blk.blk_i2p[x].height, reverse = True)
        last = self.latest_blk
        for bid in new_tree:
            blk = Blk.blk_i2p[bid]
            # find a new longer chain (if any)
            if blk.height > self.latest_blk.height:
                bptr = blk
                temp_bal = deepcopy(self.curr_balance)
                while bptr.blk_id != 0:
                    for tid in bptr.txns:
                        txn = Txn.txn_i2p[tid]
                        if txn.idy == -1:
                            temp_bal[txn.idx] += txn.amt
                        else:
                            temp_bal[txn.idx] -= txn.amt
                            temp_bal[txn.idy] += txn.amt
                    bptr = Blk.blk_i2p[bptr.pid]
                for bal in temp_bal:
                    if bal < 0:
                        break
                else:
                    last = blk
                    break
            else:
                break
        # set to found chain
        bptr = last
        txns_inc = set()
        while bptr.blk_id != 0:
            for tid in bptr.txns:
                txn = Txn.txn_i2p[tid]
                if txn.idy == -1:
                    self.curr_balance[txn.idx] += txn.amt
                else:
                    self.curr_balance[txn.idx] -= txn.amt
                    self.curr_balance[txn.idy] += txn.amt
                txns_inc.add(tid)
            bptr = Blk.blk_i2p[bptr.pid]
        for tid in txns_inc:
            if tid in self.txn_exc:
                self.txn_exc.remove(tid)
        self.latest_blk = last

    # print txns
    def print_txns(self, fptr:TextIOWrapper):
        '''print txns'''
        fptr.write(f'Peer {self.pid} txns: ')
        for tid in self.txn_all:
            fptr.write(f'{tid} ')
        fptr.write('\n')

    # print longest chain
    def print_lc(self, fptr:TextIOWrapper):
        '''longest chain'''
        fptr.write(f'Peer {self.pid} longest chain: ')
        bptr = self.latest_blk
        while bptr.blk_id != 0:
            fptr.write(f'{bptr.blk_id} -> ')
            bptr = Blk.blk_i2p[bptr.pid]
        fptr.write(f'{bptr.blk_id}')
        fptr.write('\n')

    # invalidity of balance
    def check_bal(self, balance):
        '''check balances'''
        for bal in balance:
            if bal < -1e-5:
                return False
        return True

    # check blk from genesis
    def check_blk(self, blk):
        '''check validity of block'''
        temp_bal = [0 for _ in range(self.n)]
        while blk.blk_id != 0:
            for tid in blk.txns:
                txn = Txn.txn_i2p[tid]
                if txn.idy == -1:
                    temp_bal[txn.idx] += txn.amt
                else:
                    temp_bal[txn.idx] -= txn.amt
                    temp_bal[txn.idy] += txn.amt
            blk = Blk.blk_i2p[blk.pid]
        for bal in temp_bal:
            if bal < -1e-5:
                return False
        return True
