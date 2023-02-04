#ifndef HEADER
#define HEADER

#include "include/cxxopts.hpp"
#include <iostream>
#include <chrono>
#include <random>
#include <vector>
#include <unordered_set>
using namespace std;

typedef long long ll;
typedef long double ld;

// https://codeforces.com/blog/entry/61587
// Usage: rng(), rng.min(), rng.max()
mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
mt19937_64 rng_64(chrono::steady_clock::now().time_since_epoch().count());
auto&& rng_to_use = rng;

class peer {
    private:
        bool is_slow, is_lowCPU;
    public:
        peer(bool is_slow, bool is_lowCPU);
};

class simulator {
    private:
        int seed, n;
        ld z0, z1, Ttx;
        
        vector<peer> peers_vec;
        vector<vector<int>> adj;    // adjacency list representation
        vector<bool> visited;       // temporary; used for network creation

        void create_graph(int a, int b);
        vector<int> pick_random(int n, int k);
        void dfs(int node, vector<unordered_set<int>>& adj_sets);

    public:
        simulator(int seed, int n, ld z0, ld z1, ld Ttx, int min_ngbrs, int max_ngbrs);
        void print_graph();

};

#endif