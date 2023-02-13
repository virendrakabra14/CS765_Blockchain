#include "include/header.hpp"

// https://codeforces.com/blog/entry/61587
mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
mt19937_64 rng_64(chrono::steady_clock::now().time_since_epoch().count());
// mt19937& rng_to_use = rng;

int n = 0;
ld current_time = 0.0L;

int main(int argc, const char* argv[]) {

    ios_base::sync_with_stdio(false); cin.tie(0);

    // argument parser: https://github.com/jarro2783/cxxopts

    cxxopts::Options options(argv[0], "P2P Cryptocurrency Network");

    options.add_options()
        ("n, nodes", "number of nodes", cxxopts::value<int>()->default_value("10"))
        ("z0, slow", "percentage of slow nodes", cxxopts::value<ld>()->default_value("10"))
        ("z1, low", "percentage of low CPU nodes", cxxopts::value<ld>()->default_value("10"))
        ("Ttx, txn_interarrival_mean", "transactions' mean interarrival time", cxxopts::value<ld>()->default_value("10"))
        ("min_ngbrs", "minimum number of neighbors per node", cxxopts::value<int>()->default_value("4"))
        ("max_ngbrs", "maximum number of neighbors per node", cxxopts::value<int>()->default_value("8"))
        ("seed", "random seed", cxxopts::value<int>()->default_value("0"))
    ;

    auto result = options.parse(argc, argv);

    n = result["n"].as<int>();
    ld z0 = result["z0"].as<ld>();
    ld z1 = result["z1"].as<ld>();
    ld Ttx = result["Ttx"].as<ld>();
    int min_ngbrs = result["min_ngbrs"].as<int>();
    int max_ngbrs = result["max_ngbrs"].as<int>();
    int seed = result["seed"].as<int>();

    simulator sim(seed, z0, z1, Ttx, min_ngbrs, max_ngbrs);
    sim.print_graph();

    sim.run();

	cout << "NUMBER OF PEERS SAVED " << sim.peers_vec.size() <<  endl;
    for(auto&& p : sim.peers_vec) {
		cout << "START " << endl;
        p.print_all_txns();
		cout << "ONE DONE" << endl;
    }
	cout << "PROGRAM ENDING" << endl;

}
