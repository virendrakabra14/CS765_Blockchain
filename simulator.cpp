#include "include/header.hpp"

simulator::simulator(int seed, int n, ld z0, ld z1, ld Ttx, int min_ngbrs, int max_ngbrs) {
    this->seed = seed;
    rng.seed(seed);
    rng_64.seed(seed);

    this->n = n;
    this->z0 = z0;
    this->z1 = z1;
    this->Ttx = Ttx;

    peers_vec = vector<peer>(n, peer(0,0));
    adj = vector<vector<int>>(n, vector<int>(0));
    visited = vector<bool>(n, false);

    this->create_graph(min_ngbrs, max_ngbrs);
}

vector<int> simulator::pick_random(int n, int k) {
    // generate k random numbers in 0 to n-1
    // https://stackoverflow.com/a/28287865/17786040

    k = min(n, k);

    unordered_set<int> elems;

    for (int r=n-k; r<n; r++) {
        int v = uniform_int_distribution<>(0, r)(rng_to_use);  // [0,r]
        if (!elems.insert(v).second) {
            elems.insert(r);
        }
    }

    // deterministic order => shuffle it
    vector<int> result(elems.begin(), elems.end());
    shuffle(result.begin(), result.end(), rng_to_use);

    return result;
}

void simulator::dfs(int node, vector<unordered_set<int>>& adj_sets) {
    visited[node] = true;
    for(int i:adj_sets[node]) {
        if(!visited[i]) {
            dfs(i, adj_sets);
        }
    }
}

void simulator::create_graph(int min_ngbrs, int max_ngbrs) {
    // create a random connected graph,
    // where each node has min_ngbrs <= #neighbors <= max_ngbrs

    vector<unordered_set<int>> adj_sets(n);

    while(true) {
        fill(visited.begin(), visited.end(), false);
        dfs(0, adj_sets);
        bool connected = true;
        for (int i=0; i<n; i++) {
            if(!visited[i]) {
                connected = false;
                break;
            }
        }
        if(connected) break;

        while(true) {
            bool done = true;
            for (int i=0; i<n; i++) {
                adj_sets[i].clear();
            }
            for (int i=0; i<n; i++) {
                int req_ngbrs = uniform_int_distribution<>(min_ngbrs,max_ngbrs)(rng_to_use) - adj_sets[i].size();
                if(req_ngbrs<0) {
                    done = false;
                    break;
                }
                vector<int> new_ngbrs = pick_random(n, req_ngbrs);
                for (int j=0; j<new_ngbrs.size(); j++) {
                    if(new_ngbrs[j]==i || adj_sets[new_ngbrs[j]].size()>=max_ngbrs) {
                        done = false;
                        break;
                    }
                    adj_sets[i].insert(new_ngbrs[j]);
                    adj_sets[new_ngbrs[j]].insert(i);     // undirected graph
                }
                for (int j=0; j<n; j++) {
                    if(adj_sets.size()<min_ngbrs) {
                        done = false;
                        break;
                    }
                }
                if(done==false) break;
            }
            if(done) break;
        }

    }

    for (int i=0; i<n; i++) {
        adj[i] = vector<int>(adj_sets[i].begin(), adj_sets[i].end());
    }

}

void simulator::print_graph() {
    // print graph/network adjacency list
    for (int i=0; i<n; i++) {
        cout << i << ": ";
        for(auto&& j:adj[i]) {
            cout << j << ", ";
        }
        cout << '\n';
    }
}