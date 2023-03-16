from sys import argv
import urllib.request
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-exp', '--exp', type = int, help = 'Experiment ID', default=0)
parser.add_argument('-mode', '--mode', type = str, help = 'selfish/stubborn', default='selfish')

args = parser.parse_args()

exp_id = args.exp
mode = args.mode

filename = f"data/{exp_id}/{mode}-tree.txt"

edges = ""

with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
        line_processed = line.strip().split(" ")
        if len(line_processed)!=2:
            continue
        edges += line_processed[0]+"->"+line_processed[1]+";"

urllib.request.urlretrieve(f"https://chart.googleapis.com/chart?cht=gv&chl=digraph{{{edges}}}", f"{mode}-tree.png")
