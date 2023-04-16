// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract Payment {

    // edge in the network
    struct Edge {
        int other_id;
        int self_bal;
        int other_bal;
    }

    int[] ids;

    // mapping to store data
    mapping(int => uint) id_to_index;
    mapping(int => string) id_to_name;
    mapping(int => Edge[]) edges;

    // register user
    function registerUser(int user_id, string memory user_name) public {
        id_to_index[user_id] = ids.length;
        ids.push(user_id);
        id_to_name[user_id] = user_name;
        // edges[user_id] default to []
    }

    // create account
    function createAcc(int user_id_1, int user_id_2, int balance) public {
        require(balance%2 == 0, "Initial balance must be divisible by 2");
        edges[user_id_1].push(Edge(user_id_2, balance/2, balance/2));
        edges[user_id_2].push(Edge(user_id_1, balance/2, balance/2));
    }

    // transaction
    function sendAmount(int user_id_1, int user_id_2, int amount) public {
        // python client ensures that there is an account
        uint i;

        // validating joint accounts
        for(i=0; i<edges[user_id_1].length; i++) {
            if(edges[user_id_1][i].other_id == user_id_2) {
                require(edges[user_id_1][i].self_bal >= amount);
                edges[user_id_1][i].self_bal -= amount;
                edges[user_id_1][i].other_bal += amount;
            }
        }
        for(i=0; i<edges[user_id_2].length; i++) {
            if(edges[user_id_2][i].other_id == user_id_1) {
                require(edges[user_id_2][i].other_bal >= amount);
                edges[user_id_2][i].other_bal -= amount;
                edges[user_id_2][i].self_bal += amount;
            }
        }
    }

    // remove edge
    function closeAccount(int user_id_1, int user_id_2) public {
        uint i;
        for(i=0; i<edges[user_id_1].length; i++) {
            if(edges[user_id_1][i].other_id == user_id_2) {
                // copy last elem at this place, and delete last elem
                edges[user_id_1][i] = edges[user_id_1][edges[user_id_1].length-1];
                edges[user_id_1].pop();     // delete is implicitly called
            }
        }
        for(i=0; i<edges[user_id_2].length; i++) {
            if(edges[user_id_2][i].other_id == user_id_1) {
                edges[user_id_2][i] = edges[user_id_2][edges[user_id_2].length-1];
                edges[user_id_2].pop();
            }
        }
    }

    function getIndexFromId(int id) public view returns (uint) {
        // get index of a given user_id
        return id_to_index[id];
    }

    function getIdFromIndex(uint index) public view returns (int) {
        // get user_id of a given index
        require(index < ids.length);
        return ids[index];
    }

    function getEdges() public view returns (int[][] memory) {
        // return adjacency matrix with balances
        int[][] memory arr = new int[][](ids.length);
        uint self_index;
        uint other_index;
        uint i;
        uint j;

        for(i=0; i<ids.length; i++) {
            arr[i] = new int[](ids.length);
            for(j=0; j<ids.length; j++) {   // -1 => no edge
                (arr[i])[j] = -1;
            }
        }

        // fill adjacency matrix with balances
        // if arr[i][j] >= 0, then there is i-j
        // joint account, with i's balance = arr[i][j]
        for(i=0; i<ids.length; i++) {
            for(j=0; j<edges[ids[i]].length; j++) {
                self_index = i;
                other_index = id_to_index[edges[ids[i]][j].other_id];
                (arr[self_index])[other_index] = edges[ids[i]][j].self_bal;
            }
        }
        return arr;
    }

}