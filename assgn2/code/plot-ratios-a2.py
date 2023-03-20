import matplotlib.pyplot as plt
import os
import pathlib
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-mode', '--mode', type = str, help = 'selfish/stubborn', default='selfish')
args = parser.parse_args()
mode = args.mode

directory = "./data"
plots_dir = "./plots"
pathlib.Path(plots_dir).mkdir(exist_ok=True)

mpus_adv = {}
mpus_overall = {}
mpus_ratio = {}

for dir in os.listdir(directory):
    filename = os.path.join(directory, dir, f'{mode}-tree.txt')

    if os.path.isfile(filename):

        with open(filename, 'r' , encoding='utf-8') as f:
            miner_to_blocks = {}
            block_to_miner = {}
            chains = {}
            total_blks = None
            adv_blks = None

            for line in f:
                line_split = line.strip().split(' ')
                if len(line_split)==2:
                    for i in range(2):
                        block = int(line_split[i].split('_')[1])
                        miner = -1 if line_split[i].split('_')[3]=='G' else int(line_split[i].split('_')[3])
                        if miner in miner_to_blocks:
                            miner_to_blocks[miner].add(block)
                        else:
                            miner_to_blocks[miner] = set()
                            miner_to_blocks[miner].add(block)
                        block_to_miner[block] = miner
                elif "Total blocks" in line.strip():
                    total_blks = int(line.strip().split(":")[1].strip())
                elif "Adversary blocks" in line.strip():
                    adv_blks = int(line.strip().split(":")[1].strip())
                elif "longest chain" in line.strip():
                    peer = int(line.strip().split(':')[0].split(' ')[1])
                    blocks = [int(blk) for blk in line.strip().split(':')[1].strip().split(' -> ')]
                    chains[peer] = blocks

            # print(miner_to_blocks)
            # print(block_to_miner)
            # print(chains)
            # print(total_blks)
            # print(adv_blks)

            adv = len(chains)-1     # last node is adversary
            adv_in_main_chain = 0
            total_in_main_chain = 0
            num_chains = 0          # should equal `adv`

            for peer, chain in chains.items():
                if peer==adv:
                    continue
                num_chains += 1
                for blk in chain:
                    if blk==0:
                        continue
                    else:
                        if block_to_miner[blk]==adv:
                            adv_in_main_chain += 1
                        total_in_main_chain += 1

            mpu_adv = (adv_in_main_chain/num_chains)/adv_blks
            mpu_overall = (total_in_main_chain/num_chains)/total_blks

            mpus_adv[int(dir)] = mpu_adv
            mpus_overall[int(dir)] = mpu_overall
            mpus_ratio[int(dir)] = mpu_adv/mpu_overall

mpus_adv = dict(sorted(mpus_adv.items()))
mpus_overall = dict(sorted(mpus_overall.items()))
mpus_ratio = dict(sorted(mpus_ratio.items()))

# print(mpus_adv)
# print(mpus_overall)
# print(mpus_ratio)

fig, (ax1, ax2) = plt.subplots(1,2)

ax1.scatter(mpus_adv.keys(), mpus_adv.values(), edgecolors='r', facecolors='none', label='MPU_adv')
ax1.scatter(mpus_overall.keys(), mpus_overall.values(), edgecolors='b', facecolors='none', label='MPU_overall')
ax2.scatter(mpus_ratio.keys(), mpus_ratio.values(), edgecolors='b', facecolors='none', label='MPU_ratio')

ax1.set_xticks(list(range(len(mpus_adv))))
ax2.set_xticks(list(range(len(mpus_ratio))))
ax1.set_yticks([e/10 for e in list(range(11))])
ax2.set_ylim(bottom=0)

ax1.legend()
ax2.legend()

ax1.set_xlabel('Experiment Number')
ax2.set_xlabel('Experiment Number')
ax1.set_ylabel('MPU')
ax2.set_ylabel('MPU_adv/MPU_overall')
ax1.set_title('MPU (adversary and overall)')
ax2.set_title('Ratio of adversary and overall MPU')

fig.set_size_inches(15, 8)

# plt.show()
fig.savefig(os.path.join(plots_dir, f"{mode}-ratios2.png"), bbox_inches="tight")