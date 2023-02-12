#include "include/header.hpp"

peer::peer(int id) {
    this->id = id;
    this->slow = false;
    this->lowCPU = false;
    curr_balances = vector<ld>(n, 0ll);
}

void peer::generate_txn(simulator& sim, event* e) {
    // this peer pays someone (possibly to self);
    // there would be a signature, so can't make someone else pay
    
    int IDx=id, IDy=uniform_int_distribution<>(0,n)(rng);   // IDy might equal IDx
    ld C;

    // txn can be invalid (pays more than current balance)
    bool invalid = uniform_real_distribution<ld>(0.0L,1.0L)(rng) < 0.1L;     // can put prob as cmdline arg

    if(invalid) {
        C = curr_balances[id] + uniform_real_distribution<ld>(1e-8L,10.0L)(rng_64); // 1 satoshi = 1e-8 BTC
    }
    else {
        C = uniform_real_distribution<ld>(0,curr_balances[id])(rng_64);
    }

    txn* t = new txn(IDx, false, IDy, C);
    txns_not_included.insert(t);
    txns_all.insert(t->txn_id);

    event* fwd_txn = new event(0, 2, this, t);  // 0 (assume no delay within self)
    sim.push(fwd_txn);
    // cout << "INSIDE PEER: " << sim.pq_events.top()->tran->txn_id << ',' << fwd_txn->tran->txn_id << '\n';

    cout << "generate_txn: node " << this->id << " generated " << t->txn_id << endl;

}

void peer::forward_txn(simulator& sim, event* e) {
    // fwd txn to peers (except the sender)
    // sets up hear events for peers

    for(int to:sim.adj[this->id]) {
        if(to != this->id) {
            cout << "forward_txn: node " << this->id << " forwarded " << e->tran->txn_id << " to " << to << endl;

            ld link_speed = ((this->slow || sim.peers_vec[to].slow) ? sim.slow_link_speed : sim.fast_link_speed);
            ld queuing_delay = exponential_distribution<ld>(sim.queuing_delay_numerator/link_speed)(rng);
            ld latency = sim.rho[this->id][to] + queuing_delay + e->tran->txn_size/link_speed;

            event* hear_tran = new event(latency, 3, &sim.peers_vec[to], e->tran, this);
            sim.push(hear_tran);
        }
    }
}

void peer::hear_txn(simulator& sim, event* e) {
    // return if already heard

    if(this->txns_all.find(e->tran->txn_id) != this->txns_all.end()) {
        cout << "hear_txn: node " << this->id << " already heard " << e->tran->txn_id << endl;
        return;
    }
    else {
        cout << "hear_txn: node " << this->id << " heard " << e->tran->txn_id << " from " << e->from->id << endl;
        this->txns_all.insert(e->tran->txn_id);
        
        // set up forward event for self
        event* fwd_txn = new event(0, 2, this, e->tran);    // 0 (assume no delay within self)
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

bool peer::is_invalid(vector<ld>& balances) {
    for (int i=0; i<balances.size(); i++) {
        if(balances[i]<0) return true;
    }
    return false;
}

void peer::generate_blk(simulator& sim, event* e) {
    
    vector<ld> tmp_balances = this->curr_balances;
    
    bool invalid = uniform_real_distribution<ld>(0.0L,1.0L)(rng) < 0.1L;     // can put prob as cmdline arg

    vector<txn*> curr_blk_txns(0);
    txn* coinbase_txn = new txn(this->id, true);

    ll curr_blk_size = txn::txn_size;

    blk* b = new blk(this, nullptr, curr_blk_txns);

    if(invalid) {       // doesn't necessarily generate an invalid block
                        // (when blk size exceeds before encountering an invalid txn)

        for(txn* t_ptr:txns_not_included) {     // iterate on txns by txn_id
            if(is_invalid(tmp_balances) || curr_blk_size+t_ptr->txn_size > blk::max_blk_size) {
                b->parent = this->latest_blk;
                b->txns = curr_blk_txns;
                break;
            }
            curr_blk_size += t_ptr->txn_size;
            curr_blk_txns.push_back(t_ptr);
            tmp_balances[t_ptr->IDx] -= t_ptr->C;
            tmp_balances[t_ptr->IDy] += t_ptr->C;
        }
        if(b->parent==nullptr) {
            // size wasn't exceeeded above, so include all txns
            b->parent = this->latest_blk;
            b->txns = vector<txn*>(txns_not_included.begin(), txns_not_included.end());
        }
    }
    else {
        set<txn*, compare_txn_ptrs> curr_invalid;
        for(txn* t_ptr:txns_not_included) {     // iterate on txns by txn_id
            if(curr_blk_size+t_ptr->txn_size > blk::max_blk_size) {
                b->parent = this->latest_blk;
                b->txns = curr_blk_txns;
                break;
            }
            curr_blk_size += t_ptr->txn_size;
            curr_blk_txns.push_back(t_ptr);
            tmp_balances[t_ptr->IDx] -= t_ptr->C;
            tmp_balances[t_ptr->IDy] += t_ptr->C;

            if(is_invalid(tmp_balances)) {
                curr_invalid.insert(t_ptr);
                // rollback the above changes
                curr_blk_size -= t_ptr->txn_size;
                curr_blk_txns.pop_back();
                tmp_balances[t_ptr->IDx] += t_ptr->C;
                tmp_balances[t_ptr->IDy] -= t_ptr->C;
            }
        }
        if(b->parent == nullptr) {
            // size wasn't exceeeded above, so include all valid txns
            b->parent = this->latest_blk;
            for(txn* t_ptr:txns_not_included) {
                if(curr_invalid.find(t_ptr)==curr_invalid.end()) {
                    b->txns.push_back(t_ptr);
                }
            }
        }
    }

    // done creating the block
    // set up forward events

    ld blk_genr_delay = exponential_distribution<ld>(sim.Tblk/this->fraction_hashing_power)(rng);

    event* e = new event(blk_genr_delay, 5, this, nullptr, nullptr, b);
    sim.push(e);

}