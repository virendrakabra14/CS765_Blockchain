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
    bool invalid = uniform_real_distribution<ld>()(rng) < 0.1L;     // can put prob as cmdline arg

    if(invalid) {
        C = curr_balances[id] + uniform_real_distribution<ld>(1e-8L,10.0L)(rng_64); // 1 satoshi = 1e-8 BTC
    }
    else {
        C = uniform_real_distribution<ld>(0,curr_balances[id])(rng_64);
    }

    txn t(IDx, false, IDy, C);
    txns_not_included.insert(t);

    event fwd_txn = event(0, 2, this);
    sim.push(fwd_txn);

}