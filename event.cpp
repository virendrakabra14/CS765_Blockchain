#include "include/header.hpp"

event::event(ld timestamp, int type, peer* p=nullptr) {
    this->timestamp = timestamp;
    this->type = type;
    this->p = p;
}

void event::run(simulator& sim) {
    cout << "event run: type=" << type << '\n';
    switch (type) {
        case 1:
            p->generate_txn(sim);
            break;
        // case 2:
        //     p->forward_txn(sim);
        //     break;
        default:
            cout << "incorrect event type: " << type << '\n';
            break;
    }
}