import itertools
import subprocess as sp
import shlex
import sys
import os
import pathlib

n_vals = [10]
Ttx_vals = [10]
zetas = [0.25, 0.5, 0.75]
fracs = [0.1]   # attacker hashing power
z0s = [0.5]     # slow
z1s = [0.9]     # lowCPU
modes = ['selfish', 'stubborn']
exp_id = 0

executable = "python"

data_dir = "./data"
plots_dir = "./plots"

def run_command(command):
    global exp_id

    print("COMMAND:", command)
    p = sp.Popen(shlex.split(command), stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = p.communicate()
    out, err = out.decode('utf-8'), err.decode('utf-8')
    
    if "main.py" in command:
        with open(os.path.join(data_dir, str(exp_id), 'main_output.txt'), 'w') as out_file:
            print(out, file=out_file)
    elif out:
        print(out)
    
    if err:
        print("-"*15+"EXP ERROR"+"-"*15)
        print(err)
        sys.exit(1)

commands_file = open('commands.txt', 'w', encoding='utf-8')

for n, Ttx, zeta, frac, z0, z1, mode in list(itertools.product(n_vals, Ttx_vals, zetas, fracs, z0s, z1s, modes)):

    pathlib.Path(os.path.join(data_dir,str(exp_id))).mkdir(exist_ok=True, parents=True)
    pathlib.Path(os.path.join(plots_dir,str(exp_id))).mkdir(exist_ok=True, parents=True)

    commands = [
        f"{executable} main.py -n {n} -Ttx {Ttx} -zeta {zeta} --frac {frac} -z0 {z0} -z1 {z1} -mode {mode} -exp {exp_id}",
        f"{executable} plot-tree.py -exp {exp_id} -mode {mode}",
        # f"{executable} plot-ptree.py -exp {exp_id} -mode {mode}",
    ]
    print(commands[0], file=commands_file)

    for command in commands:
        run_command(command)
    
    exp_id += 1

# lengths and ratios
for mode in modes:
    commands = [
        # f"{executable} plot-lengths.py -mode {mode}",     # A1
        # f"{executable} plot-ratios.py -mode {mode}"       # A1
        f"{executable} plot-ratios-a2.py -mode {mode}"
    ]
    for command in commands:
        run_command(command)

commands_file.close()