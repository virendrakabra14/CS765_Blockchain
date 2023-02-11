#include "include/header.hpp"

peer::peer(int id) {
    this->id = id;
    this->next_time = 0;
    curr_balances = vector<ld>(n, 0ll);
}

void peer::generate_txn(simulator& sim) {
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
    // calculating latency
    ll c = 100 * 1024 * 1024; // link speed in bits per second
    if(sim.peers_vec[IDx].slow || sim.peers_vec[IDy].slow) {
        c = 5 * 1024 * 1024;
    }
    ld d = 0; // need expo with mean (96.0 * 1024 / c)
    ld latency = sim.rho + (sim.m / c) + d;

    txn t(IDx, false, IDy, C);
    txns_not_included.insert(t);

    event fwd_txn = event(next_time, 2, this, &t);
    sim.push(fwd_txn);

    next_time += 0; // need expo with mean (sim.Ttx)

}

void peer::forward_txn(simulator& sim, txn* t) {

}