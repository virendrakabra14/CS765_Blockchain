#include "include/header.hpp"

vector<txn*> t;
blk* peer::genesis = new blk(nullptr, nullptr, t);

peer::peer(int id) {
    this->id = id;
    this->slow = false;
    this->lowCPU = false;
    this->curr_balances = vector<ld>(n, 0ll);
    this->latest_blk = genesis;
    this->curr_tree.insert(genesis);
	this->fraction_hashing_power = 0;
}

void peer::generate_txn(simulator& sim, event* e) {
    // this peer pays someone (possibly to self);
    // there would be a signature, so can't make someone else pay
    
    int IDx=id, IDy=uniform_int_distribution<>(0,n)(rng);   // IDy might equal IDx
    ld C;

    // txn can be invalid (pays more than current balance)
    bool invalid = uniform_real_distribution<ld>()(rng) < 0.1L;     // can put prob as cmdline arg

    if(invalid) {
        C = curr_balances[id] + uniform_real_distribution<ld>(1e-8L,10.0L)(rng_64); // 1 satoshi = 1e-8 BTC
    }
    else {
        C = uniform_real_distribution<ld>(0,curr_balances[id])(rng_64);
    }

    txn* t = new txn(IDx, false, IDy, C);
    txns_not_included.insert(t);
    txns_all.insert(t->txn_id);
    txn_sent_to[t->txn_id] = vector<ll>();

    event* fwd_txn = new event(e->timestamp + 0, 2, this, t, this);  // 0 (assume no delay within self)
    sim.push(fwd_txn);
    // cout << "INSIDE PEER: " << sim.pq_events.top()->tran->txn_id << ',' << fwd_txn->tran->txn_id << '\n';
	
	
	// schedule the next transaction created
	ld time_txn = exponential_distribution<ld>(1.0L/sim.Ttx)(rng);
    if (e->timestamp + time_txn < sim.Simulation_Time) {
        event* next_gen_event = new event(e->timestamp + time_txn, 1, this);
        sim.push(next_gen_event);
    }

    cout << "generate_txn: node " << this->id << " generated " << (invalid ? "invalid " : "valid ") << t->txn_id << endl;
	cout << "[TXN] " << t->IDx << " -> " << t->IDy << " : " << t->C << endl;  
}

void peer::forward_txn(simulator& sim, event* e) {
    // fwd txn to peers (except the sender)
    // sets up hear events for peers
	
	txn* tran = e->tran;
	ld timestamp = e->timestamp;

    for(int to:sim.adj[this->id]) {
        if(to != this->id && to != e->from->id &&
            find(txn_sent_to[e->tran->txn_id].begin(),txn_sent_to[e->tran->txn_id].end(),
            to) == txn_sent_to[e->tran->txn_id].end()) {
            cout << "forward_txn: node " << this->id << " forwarded " << e->tran->txn_id << " to " << to << endl;
            txn_sent_to[e->tran->txn_id].push_back(to);

            ld link_speed = ((this->slow || sim.peers_vec[to].slow) ? sim.slow_link_speed : sim.fast_link_speed);
            ld queuing_delay = exponential_distribution<ld>(link_speed/sim.queuing_delay_numerator)(rng);
            ld latency = sim.rho[this->id][to] + queuing_delay + e->tran->txn_size/link_speed;

            event* hear_tran = new event(timestamp + latency, 3, &sim.peers_vec[to], tran, this);
            sim.push(hear_tran);
        }
    }
}

void peer::hear_txn(simulator& sim, event* e) {
    // return if already heard
	//
	txn* tran = e->tran;
	peer* from = e->from;
	ld timestamp = e->timestamp;

    if(this->txns_all.find(e->tran->txn_id) != this->txns_all.end()) {
        cout << "hear_txn: node " << this->id << " already heard " << e->tran->txn_id << endl;
        return;
    }
    else {
        cout << "hear_txn: node " << this->id << " heard " << e->tran->txn_id << " from " << e->from->id << endl;
        this->txns_all.insert(e->tran->txn_id);
        this->txns_not_included.insert(e->tran);
        txn_sent_to[e->tran->txn_id] = vector<ll>();
        
        // set up forward event for self
        event* fwd_txn = new event(timestamp + 0, 2, this, tran, from);    // 0 (assume no delay within self)
        sim.push(fwd_txn);
    }
}

void peer::print_all_txns() {
    cout << "IDs of txns heard by " << this->id << ": ";
    for(int i:this->txns_all) {
        cout << i << ' ';
    }
    cout << endl;
}

void peer::print_longest_chain() {
    cout << "Longest chain as seen by " << this->id << ": ";
    blk* tmp_blk = latest_blk;
    vector<pair<ll,ll>> edges;
    while(tmp_blk != nullptr) {
        cout << tmp_blk->blk_id << "->";
        tmp_blk = tmp_blk->parent;
    }
    cout << endl;
}

bool peer::is_invalid(vector<ld> balances) {
    for (int i=0; i<balances.size(); i++) {
        if(balances[i]<0) return true;
    }
    return false;
}

void peer::generate_blk(simulator& sim, event* e ) {

	cout << "GENERATING CODE START" << endl;
	

	cout << "[BALANCE] " << this->id << " : ";
	for(int i = 0; i < this->curr_balances.size(); i++){
		cout << this->curr_balances[i] << " ";
	}
	cout << endl;

    vector<ld> tmp_balances = this->curr_balances;
    bool invalid = uniform_real_distribution<ld>(0.0L,1.0L)(rng) < 0.1L;     // can put prob as cmdline arg

    vector<txn*> curr_blk_txns;
    txn* coinbase_txn = new txn(this->id, true, -1, e->tran->coinbase_fee);
    txns_all.insert(coinbase_txn->txn_id);
    curr_blk_txns.push_back(coinbase_txn); // does this need to be included?

    ll curr_blk_size = txn::txn_size;
    tmp_balances[coinbase_txn->IDx] += coinbase_txn->C;

    blk* b = new blk(this, nullptr, curr_blk_txns);
    blk::blk_id_to_blk_ptr.insert(make_pair(b->blk_id,b));

    if(invalid) {       // doesn't necessarily generate an invalid block
                        // (when blk size exceeds before encountering an invalid txn)

        for(txn* t_ptr:txns_not_included) {     // iterate on txns by txn_id
			cout << "[DEBUG] " << t_ptr->C << " VALID " << invalid << " IDx " << t_ptr -> IDx <<  " IDy " << t_ptr->IDy << endl;;
            if(is_invalid(tmp_balances) || curr_blk_size+t_ptr->txn_size > blk::max_blk_size) {
                if(is_invalid(tmp_balances)) b->originally_invalid = true;
                b->update_parent(this->latest_blk);
                b->txns = curr_blk_txns;
                break;
            }
            curr_blk_size += t_ptr->txn_size;
            curr_blk_txns.push_back(t_ptr);
            if (t_ptr->IDy == -1) {
                tmp_balances[t_ptr->IDx] += t_ptr->C;
            }
            else {
                tmp_balances[t_ptr->IDx] -= t_ptr->C;
                tmp_balances[t_ptr->IDy] += t_ptr->C;
            }
            // if(is_invalid(tmp_balances)) {
            //     // rollback the above changes
            //     curr_blk_size -= t_ptr->txn_size;
            //     curr_blk_txns.pop_back();
            //     if (t_ptr->IDy == -1) {
            //         tmp_balances[t_ptr->IDx] -= t_ptr->C;
            //     }
            //     else {
            //         tmp_balances[t_ptr->IDx] += t_ptr->C;
            //         tmp_balances[t_ptr->IDy] -= t_ptr->C;
            //     }
            // }
        }
        if(b->parent==nullptr) {
            // size wasn't exceeded above, so include all txns
            b->update_parent(this->latest_blk);
            b->txns = vector<txn*>(txns_not_included.begin(), txns_not_included.end());
        }
    }
    else {
        set<txn*, compare_txn_ptrs> curr_invalid;
        for(txn* t_ptr:txns_not_included) {     // iterate on txns by txn_id
			cout << "[DEBUG] " << t_ptr->C << " VALID " << invalid <<" IDX " << t_ptr -> IDx <<  " IDy " << t_ptr->IDy << endl;;
            if(curr_blk_size+t_ptr->txn_size > blk::max_blk_size) {
                b->update_parent(this->latest_blk);
                b->txns = curr_blk_txns;
                break;
            }
            curr_blk_size += t_ptr->txn_size;
            curr_blk_txns.push_back(t_ptr);
            if (t_ptr->IDy == -1) {
                tmp_balances[t_ptr->IDx] += t_ptr->C;
            }
            else {
                tmp_balances[t_ptr->IDx] -= t_ptr->C;
                tmp_balances[t_ptr->IDy] += t_ptr->C;
            }
            if(is_invalid(tmp_balances)) {
                curr_invalid.insert(t_ptr);
                // rollback the above changes
                curr_blk_size -= t_ptr->txn_size;
                curr_blk_txns.pop_back();
                if (t_ptr->IDy == -1) {
                    tmp_balances[t_ptr->IDx] -= t_ptr->C;
                }
                else {
                    tmp_balances[t_ptr->IDx] += t_ptr->C;
                    tmp_balances[t_ptr->IDy] -= t_ptr->C;
                }
            }
        }
        if(b->parent == nullptr) {
            // size wasn't exceeded above, so include all valid txns
            b->update_parent(this->latest_blk);
            for(txn* t_ptr:txns_not_included) {
                if(curr_invalid.find(t_ptr)==curr_invalid.end()) {
                    b->txns.push_back(t_ptr);
                }
            }
        }
    }

    this->latest_blk = b;
    b->blk_size = curr_blk_size;
    blks_all.insert(b);
    blk_arrivals[b] = e->timestamp;
    blk_sent_to[b->blk_id] = vector<ll>();

	curr_balances = tmp_balances;

    // remove included txns
    for (txn* t:b->txns) {
        txns_not_included.erase(t);
    }
	
	cout << "[BALANCE] " << this->id << " : ";
	for(int i = 0; i < this->curr_balances.size(); i++){
		cout << this->curr_balances[i] << " ";
	}
	cout << endl;

    // done creating the block
    // set up forward events

    ld blk_genr_delay = exponential_distribution<ld>(this->fraction_hashing_power /sim.Tblk)(rng);
	cout << "TBLK " << sim.Tblk << " fraction " << this->fraction_hashing_power << endl;
	cout << sim.Tblk / this -> fraction_hashing_power << " AVERAGE TIME " << blk_genr_delay << endl;

    event* fwd_blk = new event(e->timestamp + blk_genr_delay, 5, this, nullptr, this, b);
    sim.push(fwd_blk);

    cout << "generate_blk: node " << this->id << " generated " << b->blk_id << endl;

    if (e->timestamp + blk_genr_delay < sim.Simulation_Time) {
		event* mine = new event(e->timestamp + blk_genr_delay, 4, this);
		sim.push(mine);
    } 
}


void peer::forward_blk(simulator& sim, event* e) {

    // check the longest chain and broadcast block accordingly
    blk* b = e->block;
    if ((b->miner->id==id && b==latest_blk) || (curr_tree.find(b->parent) != curr_tree.end())) {
        // same longest chain so broadcast
        // cout << "Previous block ID: " << this->latest_blk->blk_id << endl;
        // cout << "Transactions in block:" << endl;
        // for (txn* t:b->txns) {
        //     if (t->coinbase) {
        //         cout << t->txn_id << ": " << t->IDx << " mines " << t->C << " coins" << endl;
        //     }
        //     else {
        //         cout << t->txn_id << ": " << t->IDx << " pays " << t->IDy << " " << t->C << " coins" << endl;
        //     }
        // }
        // broadcast block
        for(int to:sim.adj[this->id]) {
            if(to != this->id && to != e->from->id &&
                find(blk_sent_to[b->blk_id].begin(),blk_sent_to[b->blk_id].end(),
                to) == blk_sent_to[b->blk_id].end()) {
                cout << "forward_blk: node " << this->id << " forwarded " << b->blk_id << " to " << to << endl;
                blk_sent_to[b->blk_id].push_back(to);

                ld link_speed = ((this->slow || sim.peers_vec[to].slow) ? sim.slow_link_speed : sim.fast_link_speed);
				// IS THIS CORRECT???? [wasn't, now it is]
                ld queuing_delay = exponential_distribution<ld>(link_speed/sim.queuing_delay_numerator)(rng);
                ld latency = sim.rho[this->id][to] + queuing_delay + b->blk_size/link_speed;

                event* hear_blk = new event(e->timestamp + latency, 6, &sim.peers_vec[to], nullptr, this, b);
                sim.push(hear_blk);
            }
        }
    }

}

void peer::hear_blk(simulator& sim, event* e) {

    blk* b = e->block;

    if(this->blks_all.find(b) != this->blks_all.end()) {
        cout << "hear_blk: node " << this->id << " already heard " << b->blk_id << endl;
        return;
    }
    else {

        cout << "hear_blk: node " << this->id << " heard " << b->blk_id << " from " << e->from->id << endl;
        this->blks_all.insert(b);
        blk_arrivals[b] = e->timestamp;
        blk_sent_to[b->blk_id] = vector<ll>();
		cout << "[BALANCE] " << this->id << " : ";
		for(int i = 0; i < this->curr_balances.size(); i++){
			cout << this->curr_balances[i] << " ";
		}
		cout << endl;
        // validate
        bool is_valid = check_blk(b);

        if (is_valid) {
            // need to check if block needs to be taken or not
            if ((b->height == 0 && this->latest_blk == nullptr) || (b->parent == this->latest_blk && b->height == this->latest_blk->height + 1)) {
                b->update_parent(this->latest_blk);
                this->latest_blk = b;
                // update txns and balance
                for (txn* t:b->txns) {
					cout << "[DEBUG] " << t->C << " VALID " << is_valid <<" IDX " << t -> IDx <<  " IDy " << t->IDy << endl;;
                    txns_all.insert(t->txn_id);
					if (t->IDy == -1) {
						curr_balances[t->IDx] += t->C;
					}
					else {
						curr_balances[t->IDx] -= t->C;
						curr_balances[t->IDy] += t->C;
					}
                }
                // set up forward event for self
                event* fwd_blk = new event(e->timestamp + 0, 5, this, nullptr, e->from, b);    // 0 (assume no delay within self)
                sim.push(fwd_blk);
            }
            else {
                blks_not_included.insert(b);
                for (txn* t:b->txns) {
                    txns_all.insert(t->txn_id);
					cout << "[DEBUG] " << t->C << " INVALID " << is_valid <<" IDX " << t -> IDx <<  " IDy " << t->IDy << endl;;
                    txns_not_included.insert(t);
                }
            }
        }
        else {
            blks_not_included.insert(b);
            for (txn* t:b->txns) {
                txns_all.insert(t->txn_id);
                cout << "[DEBUG] " << t->C << " INVALID " << is_valid <<" IDX " << t -> IDx <<  " IDy " << t->IDy << endl;;
                txns_not_included.insert(t);
            }
        }
    }
	cout << "[BALANCE] " << this->id << " : ";
	for(int i = 0; i < this->curr_balances.size(); i++){
		cout << this->curr_balances[i] << " ";
	}
	cout << endl;

    // update tree
    event* tree = new event(e->timestamp, 7, this);
    sim.push(tree);

}

bool peer::check_blk(blk* b) {

    // validating txns in blk
    vector<ld> tmp_balances = curr_balances;

    // loop over txns
    for (txn* t:b->txns) {
        if (is_invalid(tmp_balances)) {
            return false;
        }
        if (t->IDy == -1) {
            tmp_balances[t->IDx] += t->C;
        }
        else {
            tmp_balances[t->IDx] -= t->C;
            tmp_balances[t->IDy] += t->C;
        }
    }
    if (is_invalid(tmp_balances)) {
        return false;
    }

    // txns valid
    return true;

}

bool compare(blk* a, blk* b) {
    if (a->height == b->height) return a>b;
    if (a->height > b->height) {
        return true;
    }
    return false;
}

bool peer::check_blk_from_genesis(blk* b) {
    vector<ld> tmp_balances(n, 0);
    while(b != nullptr) {
        // cout << "in loop for node " << this->id << " with blk_id " << b->blk_id << endl;
        for (txn* t:b->txns) {
            if (t->IDy == -1) {
                tmp_balances[t->IDx] += t->C;
            }
            else {
                tmp_balances[t->IDx] -= t->C;
                tmp_balances[t->IDy] += t->C;
            }
        }
        b = b->parent;
    }
    return !is_invalid(tmp_balances);
}

void peer::update_tree(simulator& sim, event* e) {

    // get longest chain
    if (latest_blk != nullptr) {
        cout << "update_tree: " << id << " current latest is " << latest_blk->blk_id  << " with height " << latest_blk->height << endl;
    }
    for(int i = 0; i < this->curr_balances.size(); i++){
        cout << this->curr_balances[i] << " ";
    }
    cout << endl;
    
    set<blk*> curr_chain;
    blk* b_iter = latest_blk;
    while (b_iter != nullptr) {
        curr_chain.insert(b_iter);
        for (txn* t:b_iter->txns) {
            txns_not_included.erase(t);
        }
        b_iter = b_iter->parent;
    }

    // ensure longest chain is in the tree
    if (curr_tree.find(latest_blk) == curr_tree.end()) {
        for (blk* b_iter:curr_chain) {
            curr_tree.insert(b_iter);
        }
    }

    // temporarily roll back
    for (blk* b_iter:curr_chain) {
        for (txn* t:b_iter->txns) {
            // roll back
            if (t->IDy == -1) {
                curr_balances[t->IDx] -= t->C;
            }
            else {
                curr_balances[t->IDx] += t->C;
                curr_balances[t->IDy] -= t->C;
            }
            txns_not_included.insert(t);
        }
    }

    // update the tree
    bool pending = true;
    while (pending) {
        for (auto it = blks_not_included.begin(); it != blks_not_included.end();) {
            if(!check_blk_from_genesis(*it)) {
                it++;
                continue;
            };
            if (((*it)->parent == nullptr || curr_tree.find((*it)->parent) != curr_tree.end())) {
                // adding block to tree
                (*it)->update_parent((*it)->parent);
                curr_tree.insert(*it);
                event* fwd_blk = new event(e->timestamp, 5, this, nullptr, this, *it);
                sim.push(fwd_blk);
                it = blks_not_included.erase(it);
            }
            else {
                it++;
            }
        }
        pending = false;
        for (blk* b:blks_not_included) {
            if(!check_blk_from_genesis(b)) continue;
            if ((b->parent == nullptr || curr_tree.find(b->parent) != curr_tree.end())) {
                // more blocks can be added
                pending = true;
                break;
            }
        }
    }

    // find new longest valid chain
    vector<blk*> v(curr_tree.begin(),curr_tree.end());
    sort(v.begin(),v.end(),compare);

    blk* last = latest_blk;
    for (blk* b:v) {
        if (b->height > latest_blk->height) {
            b_iter = b;
            vector<ld> tmp_balances = this->curr_balances;
            while (b_iter != nullptr) {
                for (txn* t:b_iter->txns) {
                    // new txns
                    if (t->IDy == -1) {
                        tmp_balances[t->IDx] += t->C;
                    }
                    else {
                        tmp_balances[t->IDx] -= t->C;
                        tmp_balances[t->IDy] += t->C;
                    }
                }
                b_iter = b_iter->parent;
            }
            if (!is_invalid(tmp_balances)) {
                last = b;
                break;
            }
        }
        else {
            break;
        }
    }

    // txns update
    b_iter = last;
    while (b_iter != nullptr) {
        for (txn* t:b_iter->txns) {
            // new txns
            if (t->IDy == -1) {
                curr_balances[t->IDx] += t->C;
            }
            else {
                curr_balances[t->IDx] -= t->C;
                curr_balances[t->IDy] += t->C;
            }
            txns_not_included.erase(t);
        }
        b_iter = b_iter->parent;
    }
    latest_blk = last;
    
    if (last != nullptr) {
        cout << "update_tree: " << id << " updated latest block to " << last->blk_id << " with height " << last->height << endl;
    }
    for(int i = 0; i < this->curr_balances.size(); i++){
        cout << this->curr_balances[i] << " ";
    }
    cout << endl;

    // back to mining
    // event* mine = new event(e->timestamp, 4, this);
    // sim.push(mine);

}
