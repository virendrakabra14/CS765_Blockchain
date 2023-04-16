#!/bin/bash

# start ganache in another terminal
truffle compile
cp 2_deploy_contracts.js migrations
truffle migrate
