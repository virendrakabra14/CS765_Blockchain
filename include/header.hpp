#ifndef HEADER
#define HEADER

#include "cxxopts.hpp"
#include <iostream>
#include <chrono>
#include <random>
#include <vector>
#include <set>
#include <unordered_set>
#include <queue>
#include <cassert>
using namespace std;

typedef long long ll;
typedef long double ld;     // better precision [12 bytes]

extern mt19937 rng;
extern mt19937_64 rng_64;
// extern mt19937& rng_to_use;     // can't use auto (!?)

extern int n;
extern ld current_time;

class simulator;
class peer;
class event;
struct compare_events;
struct compare_events_desc;
class txn;
struct compare_txns;

class event {
    public:
        ld timestamp;
        int type;
        peer* p;        // can this be done with just `peer& p`?

        event(ld timestamp, int type, peer* p);
        void run(simulator& sim);
};

struct compare_events {
    // compare events based on timestamp [ascending order]
    inline bool operator() (const event& e1, const event& e2) {
        if(e1.timestamp==e2.timestamp) return &e1<&e2;
        else return e1.timestamp<e2.timestamp;
    }
};

struct compare_events_desc {
    // compare events based on timestamp [descending order]
    inline bool operator() (const event& e1, const event& e2) {
        if(e1.timestamp==e2.timestamp) return &e1>&e2;
        else return e1.timestamp>e2.timestamp;
    }
};

class txn {
    public:
        static int curr_txn_id;
        int txn_id;
        int IDx, IDy;
        ll C;
        bool coinbase;
        txn(int IDx, bool coinbase, int IDy, ll C);
};

struct compare_txns {
    // compare events based on id [ascending order]
    inline bool operator() (const txn& txn1, const txn& txn2) {
        return txn1.txn_id<txn2.txn_id;
    }
};

class peer {
    public:
        int id;
        vector<ld> curr_balances;
        bool slow, lowCPU;
        set<txn, compare_txns> txns_not_included;   // txns not included in any block till now
                                                    // (according to this node)

        peer(int id);
        void generate_txn(simulator& sim);
};

class simulator {
    private:
        int seed;
        ld z0, z1, Ttx;
        ld current_time;
        
        vector<peer> peers_vec;
        vector<vector<int>> adj;    // adjacency list representation
        vector<bool> visited;       // temporary; used for network creation
        priority_queue<event, vector<event>, compare_events_desc> pq_events;
                                            // descending for min heap

        void create_graph(int a, int b);
        vector<int> pick_random(int n, int k);
        void dfs(int node, vector<unordered_set<int>>& adj_sets);

    public:
        simulator(int seed, ld z0, ld z1, ld Ttx, int min_ngbrs, int max_ngbrs);
        void print_graph();
        void run();
        void push(event& e);

};

#endif