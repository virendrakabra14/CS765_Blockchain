from sys import argv
import urllib.request
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-exp', '--exp', type = int, help = 'Experiment ID', default=0)
parser.add_argument('-mode', '--mode', type = str, help = 'selfish/stubborn', default='selfish')

args = parser.parse_args()

exp_id = args.exp
mode = args.mode

filename = f"data/{exp_id}/{mode}-peers.txt"

edges = ""
count = 0

with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
        line_processed = line.strip().split(" ")
        if len(line_processed)!=2:
            if line_processed==["0"]:
                continue
            urllib.request.urlretrieve(f"https://chart.googleapis.com/chart?cht=gv&chl=digraph{{{edges}}}", f"plots/{mode}-peer{count}.png")
            count += 1
            edges = ""
            continue
        edges += line_processed[1].split('.')[0]+"->"+line_processed[0].split('.')[0]+";"
    urllib.request.urlretrieve(f"https://chart.googleapis.com/chart?cht=gv&chl=digraph{{{edges}}}", f"plots/{mode}-peer{count}.png")
