#!/bin/bash

echo 'Running sim'
python3 main.py
echo 'Tree...'
python3 plot-tree.py
echo 'Peer trees...'
python3 plot-ptree.py
echo 'Lengths...'
python3 plot-lengths.py
echo 'Ratios...'
python3 plot-ratios.py
