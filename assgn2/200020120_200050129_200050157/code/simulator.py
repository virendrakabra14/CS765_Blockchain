'''Import defaults, Blk, Event and Peer'''
import random
from io import TextIOWrapper
import numpy as np
import heapq
from block import Blk
from peer import Peer
from event import Event

class Simulator:
    '''Simulator'''

    def __init__(self, n, seed, z0, z1, mode, zeta, frac, Ttx, Tblk, m, M, T):
        self.n = n
        n -= 1
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.z0 = min(1.0,max(0.0,z0))
        self.z1 = min(1.0,max(0.0,z1))
        self.mode = mode
        self.zeta = zeta
        self.frac = frac
        self.Ttx = Ttx
        self.Tblk = Tblk
        self.T = T
        self.m = m
        self.M = M
        self.fls = 100 * (2 ** 20)
        self.sls = 5 * (2 ** 10)
        self.qdn = 96 * (2 ** 10)
        self.slow = np.random.choice(n,int(z0 * n))
        self.low = np.random.choice(n,int(z1 * n))
        num_low = len(self.low)
        tot_power = 10.0 * (n - num_low) + num_low
        norm_fac = (tot_power) / (1 - self.frac)
        self.peers = []
        self.prioq = []
        n += 1
        for i in range(n):
            self.peers.append(Peer(n,i))
            if i == n - 1:
                self.peers[i].adv = True
                self.peers[i].alpha = 1
            else:
                if i in self.slow:
                    self.peers[i].slow = True
                if i in self.low:
                    self.peers[i].low = True
                    self.peers[i].alpha = 1.0 / norm_fac
                else:
                    self.peers[i].alpha = 10.0 / norm_fac
        # set initial events
        for i in range(n):
            time_txn = np.random.exponential(self.Ttx)
            txn_eve = Event(time_txn,1,self.peers[i])
            self.push(txn_eve)
            time_blk = np.random.exponential(self.Tblk)
            blk_eve = Event(time_blk,4,self.peers[i])
            self.push(blk_eve)
        self.adj = {i:set() for i in range(n)}
        self.rho = [[0.0 for _ in range(n)] for _ in range(n)]
        self.visited = [False for _ in range(n)]
        self.create_graph()

    # dfs
    def dfs(self, pid):
        '''depth first search traversal'''
        self.visited[pid] = True
        for i in self.adj[pid]:
            if not self.visited[i]:
                self.dfs(i)

    # create graph
    def create_graph(self):
        '''create graph'''
        n = self.n
        self.adj = {i:set() for i in range(n)}
        conn = False
        while not conn:
            self.visited = [False for _ in range(n)]
            self.dfs(0)
            conn = True
            for i in range(n):
                if not self.visited[i]:
                    conn = False
                    break
            if conn:
                break
            done = False
            while not done:
                done = True
                self.adj = {i:set() for i in range(n)}
                for i in reversed(range(n)):
                    if i == n - 1:
                        # first connect the adversary
                        req_ngbrs = int(i * self.zeta) - len(self.adj[i])
                        if req_ngbrs < 0:
                            done = False
                            break
                        new_ngbrs = np.random.choice(i,req_ngbrs,replace = False)
                        for j in new_ngbrs:
                            if j == i or len(self.adj[j]) > self.M:
                                done = False
                                break
                            self.adj[i].add(j)
                            self.adj[j].add(i)
                        for j in range(n):
                            if j == n - 1:
                                if len(self.adj[j]) != int(j * self.zeta):
                                    done = False
                                    break
                            if len(self.adj[j]) < self.m:
                                done = False
                                break
                    else:
                        # connect the rest to required number
                        req_ngbrs = np.random.choice(range(self.m,self.M + 1)) - len(self.adj[i])
                        if req_ngbrs < 0:
                            done = False
                            break
                        new_ngbrs = np.random.choice(n,req_ngbrs,replace = False)
                        for j in new_ngbrs:
                            if j == i or len(self.adj[j]) > self.M:
                                done = False
                                break
                            self.adj[i].add(j)
                            self.adj[j].add(i)
                        for j in range(n):
                            if j == n - 1:
                                if len(self.adj[j]) != int(j * self.zeta):
                                    done = False
                                    break
                            if len(self.adj[j]) < self.m:
                                done = False
                                break
                if not done:
                    break
        for i in range(n):
            for j in self.adj[i]:
                self.rho[i][j] = np.random.uniform(10.0,500.0) * 0.001

    # print graph
    def print_graph(self):
        '''print graph'''
        n = self.n
        for i in range(n):
            print(f'{i}: ', end = '')
            for j in self.adj[i]:
                print(f'{j}, ', end = '')
            print()

    # runner
    def run(self):
        '''runner function'''
        while len(self.prioq) != 0:
            _, _, eve = heapq.heappop(self.prioq)
            if eve.timestamp > self.T and (eve.type == 1 or eve.type == 4):
                continue
            eve.run(self)

    # push events
    def push(self, eve):
        '''push events'''
        # self.prioq.append(eve)
        heapq.heappush(self.prioq, (eve.timestamp, id(eve), eve))
        # self.prioq = sorted(self.prioq, key = lambda x: -x.timestamp)

    # print entire tree [and other data]
    def print_tree_and_chains(self, fptr:TextIOWrapper):
        '''print tree and chains (as seen by peers)'''
        for bid in range(Blk.curr_blk_id):
            blk = Blk.blk_i2p[bid]
            if blk is None:
                continue
            for child in blk.children:
                if child is None:
                    continue
                fptr.write(f'id_{bid}_miner_')
                if blk.miner is None:
                    fptr.write('G_')
                else:
                    fptr.write(f'{blk.miner.pid}_')
                fptr.write(f'inv_{blk.invalid} ')
                fptr.write(f'id_{child.blk_id}_miner_{child.miner.pid}_inv_{child.invalid}\n')
        for peer_id in range(self.n):   # only honest
            self.peers[peer_id].print_lc(fptr)
        fptr.write(f'Total blocks: {Blk.curr_blk_id}\n')
        fptr.write(f'Adversary blocks: {Peer.adv_blks}')

    # print lengths
    def print_lengths(self, fptr:TextIOWrapper):
        '''print branch lengths'''
        for bid in range(Blk.curr_blk_id):
            blk = Blk.blk_i2p[bid]
            if blk is None:
                continue
            if len(blk.children) == 0:
                fptr.write(f'{blk.height}\n')
