#include "include/header.hpp"

event::event(ld timestamp, int type, peer* p/*=nullptr*/, txn* tran/*=nullptr*/, peer* from/*=nullptr*/) {
    this->timestamp = timestamp;
    this->type = type;
    this->p = p;
    this->tran = tran;
    this->from = from;
}

void event::run(simulator& sim) {
    cout << "event run: type=" << type << '\n';
    switch (type) {
        case 1: {
            p->generate_txn(sim);
            break;
        }
        case 2: {
            // if(tran==nullptr) exit(1);
            cout << this->tran->txn_id << '\n';
            p->forward_txn(sim, this->tran);
            break;
        }
        case 3: {
            // if(from==nullptr || tran==nullptr) exit(1);
            cout << this->tran->txn_id << '\n';
            p->hear_txn(sim, this->tran, from);
            break;
        }
        default: {
            cout << "incorrect event type: " << type << '\n';
            break;
        }
    }
}