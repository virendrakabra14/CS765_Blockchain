#include "include/header.hpp"

ll blk::curr_blk_id = 0;
ll blk::max_blk_size = 8*(1<<20);       // 1 MB (bits)

blk::blk(peer* miner, blk* parent, vector<txn*>& vec_txns) {
    this->blk_id = blk::curr_blk_id++;
    this->miner = miner;
    this->parent = parent;
    if(parent != nullptr) {
        parent->children.push_back(this);
        this->height = parent->height+1;
    }
    this->txns = vec_txns;
}