#include "include/header.hpp"

peer::peer(int id) {
    this->id = id;
    curr_balances = vector<ld>(n, 0ll);
}

void peer::generate_txn(simulator& sim) {
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
    txns_not_included.insert(*t);
    txns_all.insert(t->txn_id);

    event* fwd_txn = new event(0, 2, this, t);  // 0 (assume no delay within self)
    sim.push(fwd_txn);
    // cout << "INSIDE PEER: " << sim.pq_events.top()->tran->txn_id << ',' << fwd_txn->tran->txn_id << '\n';

    cout << "generate_txn: node " << this->id << " generated " << t->txn_id << endl;

}

void peer::forward_txn(simulator& sim, txn* tran) {
    // fwd txn to peers (except the sender)
    // sets up hear events for peers

    for(int to:sim.adj[this->id]) {
        if(to != this->id) {
            cout << "forward_txn: node " << this->id << " forwarded " << tran->txn_id << " to " << to << endl;

            ld link_speed = ((this->slow || sim.peers_vec[to].slow) ? sim.slow_link_speed : sim.fast_link_speed);
            ld queuing_delay = exponential_distribution<ld>(sim.queuing_delay_numerator/link_speed)(rng);
            ld latency = sim.rho[this->id][to] + queuing_delay + tran->txn_size/link_speed;

            event* hear_tran = new event(latency, 3, &sim.peers_vec[to], tran, this);
            sim.push(hear_tran);
        }
    }
}

void peer::hear_txn(simulator& sim, txn* tran, peer* from) {
    // return if already heard

    if(this->txns_all.find(tran->txn_id) != this->txns_all.end()) {
        return;
    }
    else {
        cout << "hear_txn: node " << this->id << " heard " << tran->txn_id << " from " << from->id << endl;
        this->txns_all.insert(tran->txn_id);
        
        // set up forward event for self
        event* fwd_txn = new event(0, 2, this, tran);    // 0 (assume no delay within self)
        sim.push(fwd_txn);
    }
}