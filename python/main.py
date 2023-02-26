'''Import defaults, Blk, Event and Simulator'''
from copy import copy
from argparse import ArgumentParser as ap
from block import Blk
from event import Event
from simulator import Simulator

curr_time = 0.0

parser = ap()
parser.add_argument('-n', '--nodes', type = int, help = 'Number of nodes', default = 10)
parser.add_argument('-z0', '--slow', type = float, help = 'Fraction of slow nodes', default = 0.2)
parser.add_argument('-z1', '--low', type = float, help = 'Fraction of low CPU nodes', default = 0.2)
parser.add_argument('-Ttx', '--txn-inter-mean', type = int,
                    help = 'Mean interarrival time for txns', default = 100)
parser.add_argument('-Tblk', '--blk-inter-mean', type = int,
                    help = 'Mean interarrival time for blks', default = 600)
parser.add_argument('-m', '--min-ngbrs', type = int, help = 'Min neighbors per node', default = 4)
parser.add_argument('-M', '--max-ngbrs', type = int, help = 'Max neighbors per node', default = 8)
parser.add_argument('-s', '--seed', type = int, help = 'Random seed', default = 0)
parser.add_argument('-T', '--sim-time', type = int, help = 'Simulation time', default = 100)

args = parser.parse_args()
n = args.nodes
z0 = args.slow
z1 = args.low
Ttx = args.txn_inter_mean
Tblk = args.blk_inter_mean
m = args.min_ngbrs
M = args.max_ngbrs
s = args.seed
T = args.sim_time

sim = Simulator(n,s,z0,z1,Ttx,Tblk,m,M,T)
sim.print_graph()
sim.run()
eve = Event(0,7)
f1 = open('peers.txt','w',encoding = 'utf-8')
f2 = open('ratios.txt','w',encoding = 'utf-8')
for p in sim.peers:
    p.update_tree(sim,eve)
    print(f'------------ PEER {p.pid} ------------')
    print('Tree blocks:', end = ' ')
    f1.write(f'{p.pid}\n')
    for blk in p.curr_tree:
        print(f'{blk.blk_id}({p.blk_all[blk.blk_id]}):{blk.height}(', end = '')
        for tid in blk.txns:
            print(f'{tid},', end = '')
        print('),', end = ' ')
        f1.write(f'id_{blk.blk_id}_time_{p.blk_all[blk.blk_id]}')
        if blk.parent is not None:
            f1.write(f' id_{blk.parent.blk_id}_time_{p.blk_all[blk.parent.blk_id]}')
        f1.write('\n')
    print()
    f1.write('\n')
    pre = 0
    bptr = copy(p.latest_blk)
    while bptr.parent is not None:
        if bptr.miner.pid == p.pid:
            pre += 1
        bptr = bptr.parent
    tot = 0
    for bid in p.blk_all:
        blk = Blk.blk_i2p[bid]
        if blk.miner is not None and blk.miner.pid == p.pid:
            tot += 1
    if tot == 0:
        f2.write(f'{p.pid} ({int(p.slow)}|{int(p.low)}): -1\n')
    else:
        f2.write(f'{p.pid} ({int(p.slow)}|{int(p.low)}): {pre/tot}\n')
    print('Txns left:', end = ' ')
    for tid in p.txn_exc:
        print(f'{tid} ', end = '')
    print()
    p.print_txns()
    p.print_lc()
f1.close()
f2.close()
f3 = open('tree.txt','w',encoding = 'utf-8')
sim.print_tree(f3)
f4 = open('lengths.txt','w',encoding = 'utf-8')
sim.print_lengths(f4)
f3.close()
f4.close()
