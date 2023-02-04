#include "include/header.hpp"

int main(int argc, const char* argv[]) {

    ios_base::sync_with_stdio(false); cin.tie(0);

    // argument parser: https://github.com/jarro2783/cxxopts

    cxxopts::Options options(argv[0], "P2P Cryptocurrency Network");

    options.add_options()
        ("n, nodes", "number of nodes", cxxopts::value<int>()->default_value("10"))
        ("z0, slow", "percentage of slow nodes", cxxopts::value<ld>()->default_value("10"))
        ("z1, low", "percentage of low CPU nodes", cxxopts::value<ld>()->default_value("10"))
        ("Ttx, txn_interarrival_mean", "transations' mean interarrival time", cxxopts::value<ld>()->default_value("10"))
        ("min_ngbrs", "minimum number of neighbors per node", cxxopts::value<int>()->default_value("4"))
        ("max_ngbrs", "maximum number of neighbors per node", cxxopts::value<int>()->default_value("8"))
        ("seed", "random seed", cxxopts::value<int>()->default_value("0"))
    ;

    auto result = options.parse(argc, argv);

    int n = result["n"].as<int>();
    ld z0 = result["z0"].as<ld>();
    ld z1 = result["z1"].as<ld>();
    ld Ttx = result["Ttx"].as<ld>();
    int min_ngbrs = result["min_ngbrs"].as<int>();
    int max_ngbrs = result["max_ngbrs"].as<int>();
    int seed = result["seed"].as<int>();

    simulator sim(seed, n, z0, z1, Ttx, min_ngbrs, max_ngbrs);
    sim.print_graph();

}