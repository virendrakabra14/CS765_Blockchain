#include "include/header.hpp"

// https://stackoverflow.com/questions/16284629/undefined-reference-to-static-variable-c
ll txn::curr_txn_id = 0;
ld txn::txn_size = 8*(1<<10);       // 1 KB (bits)

txn::txn(int IDx, bool coinbase=false, int IDy=-1, ll C=-1) {
    // TxnID: IDx pays IDy C coins
    // TxnID: IDk mines 50 coins

    assert(IDx>=0 && IDx<=n);
    assert(coinbase || (IDy>=0 && IDy<=n && C>=0));

    this->txn_id = txn::curr_txn_id++;
    this->IDx = IDx;
    this->IDy = IDy;
    this->C = (coinbase ? 50 : C);
}