import main
import random
import numpy as np

class Simulator:
    '''Simulator'''
    n = main.n

    def __init__(self, seed, z0, z1, Ttx, Tblk, m, M, T):
        self.seed = seed
        random.seed(seed)
        self.z0 = min(1.0,max(0.0,z0))
        self.z1 = min(1.0,max(0.0,z1))
        self.Ttx = Ttx
        self.Tblk = Tblk
        self.T = T
        
        self.fls = 100 * (2 ** 20)
        self.sls = 5 * (2 ** 10)
        self.qdn = 96 * (2 ** 10)
        
        n = Simulator.n
        self.slow = np.random.choice(n,int(z0 * n))
        self.low = np.random.choice(n,int(z1 * n))
        
        peers = []
        for i in range(n):
            peers.append([])
    
    # push events
    def push(self, eve):
        pass