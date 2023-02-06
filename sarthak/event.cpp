#include "include/header.hpp"

event::event(ld timestamp, int type, peer* p=nullptr, txn* t=nullptr) {
    this->timestamp = timestamp;
    this->type = type;
    this->p = p;
    this->t = t;
}

void event::run(simulator& sim) {
    cout << "event run: type=" << type << '\n';
    switch (type) {
        case 1:
            p->generate_txn(sim);
            break;
        case 2:
            p->forward_txn(sim, t);
            break;
        default:
            cout << "incorrect event type: " << type << '\n';
            break;
    }
}