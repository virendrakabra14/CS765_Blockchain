#!/bin/bash

echo 'Running sim'
python3 main.py -mode $1
echo 'Tree...'
python3 plot-tree.py $1
echo 'Peer trees...'
python3 plot-ptree.py $1
echo 'Lengths...'
python3 plot-lengths.py $1
echo 'Ratios...'
python3 plot-ratios.py $1
