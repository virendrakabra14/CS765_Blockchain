# CS765
IIT Bombay (Spring 2023).

Command
```
g++ -Wall -Wextra main.cpp simulator.cpp peer.cpp event.cpp txn.cpp
```

timestamp correct value
Event to the txns in peers 



1. [x] There are n peers, each with a unique ID, where n is set at the time of initiation of the network. Some of
these nodes (say z0 percent, where z0 is a command line simulation parameter) are labeled “slow” and the others
“fast”. In addition, some of these nodes (say z1 percent, where z1 is a command line simulation parameter) are
labeled “low CPU” and the others “high CPU”.

2. [x] Each peer generates transactions randomly in time. The interarrival between transactions generated by
any peer is chosen from an exponential distribution whose mean time(Ttx) can be set as a parameter of the
simulator.

3. [x] Each transaction has the format: “TxnID: IDx pays IDy C coins”. You must ensure that C is less than
or equal to the coins currently owned by IDx (ID of the peer generating the transaction) before including it in
a block. IDy should be the ID of any other peer in the network where transaction is destined. The size of each
transaction is assumed to be 1 KB.
 
4. [x] Each peer is randomly connected to between 4 and 8 other peers. Check that the
resulting network is a connected graph, and recreate the graph from scratch if it is not a connected graph. 

5. [x] Simulate latencies Lij between pairs of peers i and j connected by a link. Latency is the time between
which a message m was transmitted from sender i and received by another node j.

6. [x] A node forwards any transaction heard from one peer to another connected peer, provided it has not
already sent the same transaction to that peer, or provided it did not hear (receive) the transaction from that
peer
 
7. [ ] Simulating PoW: All nodes have the genesis block at the start of the simulation. 
