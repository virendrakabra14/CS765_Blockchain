#include "include/header.hpp"
#include <random>

simulator::simulator(int seed, ld z0, ld z1, ld Ttx, int min_ngbrs, int max_ngbrs, ld sim_time) {
    this->seed = seed;
    rng.seed(seed);
    rng_64.seed(seed);

    this->z0 = min(1.0L, max(0.0L, z0));    // fraction in [0,1]
    this->z1 = min(1.0L, max(0.0L, z1));
    this->Ttx = Ttx;
    this->Tblk = 600;
    this->Simulation_Time = sim_time;

    // bits per second
    fast_link_speed = 100*(1<<20);          // 100 Mbps
    slow_link_speed = 5*(1<<20);            // 5 Mbps
    queuing_delay_numerator = 96*(1<<10);   // 96 kbps
	
    vector<int> slow_indices = pick_random(n, z0*n);
    vector<int> lowCPU_indices = pick_random(n, z1*n);

    peers_vec.reserve(n);

	for(int i = 0; i < n; i++){
		peers_vec.push_back(peer(i));
	}

    for(int& i:slow_indices) {
        peers_vec[i].slow = true;
    }
    for(int& i:lowCPU_indices) {
        peers_vec[i].lowCPU = true;
    }
    for (int i=0; i<n; i++) {
        if(peers_vec[i].lowCPU) peers_vec[i].fraction_hashing_power = 1.0L/(10.0L*(n-lowCPU_indices.size())+lowCPU_indices.size());
        else peers_vec[i].fraction_hashing_power = 10.0L/(10.0L*(n-lowCPU_indices.size())+lowCPU_indices.size());
		cout << "FRA " << peers_vec[i].fraction_hashing_power << " n " << n << " size " << lowCPU_indices.size() << endl;
    }

    for (int i=0; i<n; i++) {
        // peers_vec.push_back(peer(i));
        // initialize events (generate_txn)
        ld time_txn = exponential_distribution<ld>(1.0L/Ttx)(rng);
		cout << "time_txn " << time_txn << endl;
        event* e = new event(time_txn, 1, &peers_vec[i]);
        this->push(e);

		cout << "SANCHIT " << this->Tblk << " ----- " << peers_vec[i].fraction_hashing_power <<endl;
		ld time_blk = exponential_distribution<ld>(peers_vec[i].fraction_hashing_power/this->Tblk)(rng);
		cout << time_blk << endl;

 
        event* blk_gen = new event(time_blk, 4, &peers_vec[i]);
        this->push(blk_gen);
    }


    adj = vector<vector<int>>(n);
    rho = vector<vector<ld>>(n, vector<ld>(n, 0.0L));
    visited = vector<bool>(n, false);

    this->create_graph(min_ngbrs, max_ngbrs);

    blk::blk_id_to_blk_ptr.insert(make_pair(peer::genesis->blk_id,peer::genesis));
}

vector<int> simulator::pick_random(int n, int k) {
    // generate k random numbers in 0 to n-1
    // https://stackoverflow.com/a/28287865/17786040

    k = min(n, k);

    unordered_set<int> elems;

    for (int r=n-k; r<n; r++) {
        int v = uniform_int_distribution<>(0, r)(rng);  // [0,r]
        if (!elems.insert(v).second) {
            elems.insert(r);
        }
    }

    // deterministic order, so shuffle it
    vector<int> result(elems.begin(), elems.end());
    shuffle(result.begin(), result.end(), rng);

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
                int req_ngbrs = uniform_int_distribution<>(min_ngbrs,max_ngbrs)(rng) - adj_sets[i].size();
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

    for (int i=0; i<n; i++) {
        for(auto&& j:adj[i]) {
            rho[i][j] = (10.0L + (490.0L * uniform_real_distribution<ld>()(rng))) * 0.001;
        }
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

void simulator::run() {
    // https://www.cs.cmu.edu/~music/cmsip/readings/intro-discrete-event-sim.html
	//

    while(!pq_events.empty()) {
        // cout << pq_events.size() << '\n';
        event* e = pq_events.top();
        pq_events.pop();
        
        if(e->timestamp > Simulation_Time && (e->type==1 || e->type==4)) continue;

        // if(e->tran) cout << "SIM TXN: " << e->tran->txn_id << '\n';
        e->run(*this);
        
        // clean up (delete event, and probably the associated txn)
        // (define destructor for event)
    }
}

void simulator::push(event* e) {
    pq_events.push(e);
}

void simulator::print_entire_tree(ostream& out) {
    for (ll i=0; i<blk::curr_blk_id; i++) {
        auto it = blk::blk_id_to_blk_ptr.find(i);
        if(it == blk::blk_id_to_blk_ptr.end() || it->second==nullptr) continue;

        for(blk* child:it->second->children) {
            if(child==nullptr) continue;
            out << it->first << ' ' << child->blk_id << endl;
        }
    }
}