#include "include/header.hpp"

peer::peer(int id) {
    this->id = id;
    this->slow = false;
    this->lowCPU = false;
    this->curr_balances = vector<ld>(n, 0ll);
    this->latest_blk = nullptr;
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
	event* next_gen_event = new event(e->timestamp + time_txn, 1, this);
	sim.push(next_gen_event);

    cout << "generate_txn: node " << this->id << " generated " << t->txn_id << endl;
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
            ld queuing_delay = exponential_distribution<ld>(sim.queuing_delay_numerator/link_speed)(rng);
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
    curr_blk_txns.push_back(coinbase_txn); // does this need to be included?

    ll curr_blk_size = txn::txn_size;

    blk* b = new blk(this, nullptr, curr_blk_txns);

    if(invalid) {       // doesn't necessarily generate an invalid block
                        // (when blk size exceeds before encountering an invalid txn)

        for(txn* t_ptr:txns_not_included) {     // iterate on txns by txn_id
			cout << "[DEBUG] " << t_ptr->C << " INVALID " << invalid << " IDx " << t_ptr -> IDx <<  " IDy " << t_ptr->IDy << endl;;
            if(is_invalid(tmp_balances) || curr_blk_size+t_ptr->txn_size > blk::max_blk_size) {
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
			cout << "[DEBUG] " << t_ptr->C << " INVALID " << invalid <<" IDX " << t_ptr -> IDx <<  " IDy " << t_ptr->IDy << endl;;
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

    if (this->latest_blk == nullptr) {
        this->latest_blk = b;
    }
    b->blk_size = curr_blk_size;
    blks_all.insert(b->blk_id);
    blk_sent_to[b->blk_id] = vector<ll>();

	curr_balances = tmp_balances;
	
	cout << "[BALANCE] " << this->id << " : ";
	for(int i = 0; i < this->curr_balances.size(); i++){
		cout << this->curr_balances[i] << " ";
	}
	cout << endl;

    // done creating the block
    // set up forward events

    ld blk_genr_delay = exponential_distribution<ld>(sim.Tblk/this->fraction_hashing_power)(rng);

    event* fwd_blk = new event(e->timestamp + blk_genr_delay, 5, this, nullptr, this, b);
    sim.push(fwd_blk);

    cout << "generate_blk: node " << this->id << " generated " << b->blk_id << endl;

}

void peer::forward_blk(simulator& sim, event* e) {

    // check the longest chain and broadcast block accordingly
    blk* b = e->block;
    if (b->height == 0 || b->height == this->latest_blk->height + 1) {
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
                ld queuing_delay = exponential_distribution<ld>(sim.queuing_delay_numerator/link_speed)(rng);
                ld latency = sim.rho[this->id][to] + queuing_delay + b->blk_size/link_speed;

                event* hear_blk = new event(e->timestamp + latency, 6, &sim.peers_vec[to], nullptr, this, b);
                sim.push(hear_blk);
            }
        }
    }

}

void peer::hear_blk(simulator& sim, event* e) {

    blk* b = e->block;

    if(this->blks_all.find(b->blk_id) != this->blks_all.end()) {
        cout << "hear_blk: node " << this->id << " already heard " << b->blk_id << endl;
        return;
    }
    else {

        cout << "hear_blk: node " << this->id << " heard " << b->blk_id << " from " << e->from->id << endl;
        this->blks_all.insert(b->blk_id);
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
            if ((b->height == 0 && this->latest_blk == NULL) || (b->parent == this->latest_blk && b->height == this->latest_blk->height + 1)) {
                b->update_parent(this->latest_blk);
                this->latest_blk = b;
                // update txns and balance
                for (txn* t:b->txns) {
					cout << "[DEBUG] " << t->C << " INVALID " << is_valid <<" IDX " << t -> IDx <<  " IDy " << t->IDy << endl;;
                    txns_all.insert(t->txn_id);
					if (t->IDy == -1) {
						curr_balances[t->IDx] += t->C;
					}
					else {
						curr_balances[t->IDx] -= t->C;
						curr_balances[t->IDy] += t->C;
					}
                }
            }
            else {
                blks_not_included.insert(b);
                for (txn* t:b->txns) {
					cout << "[DEBUG] " << t->C << " INVALID " << is_valid <<" IDX " << t -> IDx <<  " IDy " << t->IDy << endl;;
                    txns_not_included.insert(t);
                }
            }
            if (b->height == 0 || blks_all.find(b->parent->blk_id) != blks_all.end()) {
                // set up forward event for self
                event* fwd_blk = new event(e->timestamp + 0, 5, this, nullptr, e->from, b);    // 0 (assume no delay within self)
                sim.push(fwd_blk);
            }
        }
    }
	cout << "[BALANCE] " << this->id << " : ";
	for(int i = 0; i < this->curr_balances.size(); i++){
		cout << this->curr_balances[i] << " ";
	}
	cout << endl;
    // back to mining
    event* mine = new event(0, 4, this);
    sim.push(mine);

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

    // txns valid
    return true;

}
