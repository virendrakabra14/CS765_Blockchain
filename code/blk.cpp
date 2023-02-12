#include "include/header.hpp"

ll blk::curr_blk_id = 0;
ll blk::max_blk_size = 8*(1<<20);       // 1 MB (bits)

blk::blk(peer* miner, blk* parent, vector<txn*>& vec_txns) {
    this->blk_id = blk::curr_blk_id++;
    this->miner = miner;
    this->txns = vec_txns;
    this->blk_size = 0;
    this->update_parent(parent);
}

void blk::update_parent(blk* new_parent) {

    this->parent = new_parent;
    if (new_parent != nullptr) {
        cout << this->blk_id << " " << new_parent->blk_id << endl;
        new_parent->children.insert(this);
        this->height = new_parent->height + 1;
    }
    else {
        this->height = 0;
    }

}