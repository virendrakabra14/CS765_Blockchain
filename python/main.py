from argparse import ArgumentParser as ap

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
parser.add_argument('-T', '--sim-time', type = int, help = 'Simulation time', default = 10000)

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

