#include "include/header.hpp"

peer::peer(bool is_slow=false, bool is_lowCPU=false) {
    this->is_slow = is_slow;
    this->is_lowCPU = is_lowCPU;
}