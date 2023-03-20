'''Import defaults, Blk, Event and Simulator'''
from sys import stdout
from copy import copy
from argparse import ArgumentParser as ap
from block import Blk
from event import Event
from simulator import Simulator

curr_time = 0.0

parser = ap()
parser.add_argument('-n', '--nodes', type = int, help = 'Number of nodes', default = 10)
parser.add_argument('-z0', '--slow', type = float, help = 'Fraction of slow nodes', default = 0.5)
parser.add_argument('-z1', '--low', type = float, help = 'Fraction of low CPU nodes', default = 0.9)
parser.add_argument('-mode', '--mode', type = str, help = 'Mode of adversary', default = 'selfish')
parser.add_argument('-zeta', '--zeta', type = float, help = 'Fraction of honest connected to adversary', default = 0.25)
parser.add_argument('-f', '--frac', type = float, help = 'Fraction of hashing power of adversary', default = 0.3)
parser.add_argument('-Ttx', '--txn-inter-mean', type = int,
                    help = 'Mean interarrival time for txns', default = 10)
parser.add_argument('-Tblk', '--blk-inter-mean', type = int,
                    help = 'Mean interarrival time for blks', default = 600)
parser.add_argument('-m', '--min-ngbrs', type = int, help = 'Min neighbors per node', default = 4)
parser.add_argument('-M', '--max-ngbrs', type = int, help = 'Max neighbors per node', default = 8)
parser.add_argument('-s', '--seed', type = int, help = 'Random seed', default = 0)
parser.add_argument('-T', '--sim-time', type = int, help = 'Simulation time', default = 10000)
parser.add_argument('-exp', '--exp', type = int, help = 'Experiment ID', default=0)

args = parser.parse_args()
n = args.nodes
z0 = args.slow
z1 = args.low
mode = args.mode
zeta = args.zeta
frac = args.frac
Ttx = args.txn_inter_mean
Tblk = args.blk_inter_mean
m = args.min_ngbrs
M = args.max_ngbrs
s = args.seed
T = args.sim_time
exp_id = args.exp

sim = Simulator(n + 1,s,z0,z1,mode,zeta,frac,Ttx,Tblk,m,M,T)
sim.print_graph()
sim.run()
eve = Event(0,7)
with open(f'data/{exp_id}/{mode}-peers.txt','w',encoding = 'utf-8') as f1:
    with open(f'data/{exp_id}/{mode}-ratios.txt','w',encoding = 'utf-8') as f2:
        for p in sim.peers:
            p.update_tree(sim,eve)
            print(f'------------ PEER {p.pid} ------------')
            print('Tree blocks:', end = ' ')
            f1.write(f'{p.pid}\n')
            for bid in p.curr_tree:
                blk = Blk.blk_i2p[bid]
                print(f'{blk.blk_id}({p.blk_all[blk.blk_id]}):{blk.height}, ', end = '')
                # for tid in blk.txns:
                #     print(f'{tid},', end = '')
                # print('),', end = ' ')
                f1.write(f'id_{blk.blk_id}_time_{round(p.blk_all[blk.blk_id])}_miner_{"G" if blk.miner is None else blk.miner.pid}_valid_{int(not blk.invalid)}')
                if blk.pid != -1:
                    blk_parent = Blk.blk_i2p[blk.pid]
                    f1.write(f' id_{blk.pid}_time_{round(p.blk_all[blk.pid])}_miner_{"G" if blk_parent.miner is None else blk_parent.miner.pid}_valid_{int(not blk_parent.invalid)}')
                else:
                    f1.write(' id_0_time_0_miner_G_valid_1')
                f1.write('\n')
            print()
            pre = 0
            bptr = copy(p.latest_blk)
            while bptr.blk_id != 0:
                if bptr.miner.pid == p.pid:
                    pre += 1
                bptr = Blk.blk_i2p[bptr.pid]
            tot = 0
            for bid in p.blk_all:
                blk = Blk.blk_i2p[bid]
                if blk.miner is not None and blk.miner.pid == p.pid:
                    tot += 1
            if tot == 0:
                f2.write(f'{p.pid} ({int(p.slow)}|{int(p.low)}): -1\n')
            else:
                f2.write(f'{p.pid} ({int(p.slow)}|{int(p.low)}): {pre/tot}\n')
            # print('Txns left:', end = ' ')
            # for tid in p.txn_exc:
            #     print(f'{tid} ', end = '')
            # print()
            # with open(f'peer-files/peer{p.pid}-txns.txt','w',encoding = 'utf-8') as f5:
            #     p.print_txns(f5)
            p.print_lc(stdout)
with open(f'data/{exp_id}/{mode}-tree.txt','w',encoding = 'utf-8') as f3:
    sim.print_tree_and_chains(f3)
with open(f'data/{exp_id}/{mode}-lengths.txt','w',encoding = 'utf-8') as f4:
    sim.print_lengths(f4)
