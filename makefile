SOURCE=./
BUILD=./build/

all: $(BUILD)simulator.o $(BUILD)peer.o $(BUILD)event.o $(BUILD)txn.o $(BUILD)main.o ./simulation

$(BUILD)simulator.o : $(SOURCE)simulator.cpp ./include/header.hpp ./include/cxxopts.hpp
	$(CXX) -c -o $(BUILD)simulator.o $(SOURCE)simulator.cpp

$(BUILD)peer.o : $(SOURCE)peer.cpp ./include/header.hpp ./include/cxxopts.hpp
	$(CXX) -c -o $(BUILD)peer.o $(SOURCE)peer.cpp

$(BUILD)event.o : $(SOURCE)event.cpp ./include/header.hpp ./include/cxxopts.hpp
	$(CXX) -c -o $(BUILD)event.o $(SOURCE)event.cpp

$(BUILD)txn.o : $(SOURCE)simulator.cpp ./include/header.hpp ./include/cxxopts.hpp
	$(CXX) -c -o $(BUILD)txn.o $(SOURCE)txn.cpp

$(BUILD)main.o : $(SOURCE)main.cpp ./include/header.hpp ./include/cxxopts.hpp
	$(CXX) -c -o $(BUILD)main.o $(SOURCE)main.cpp

./simulation : $(BUILD)simulator.o $(BUILD)peer.o $(BUILD)event.o $(BUILD)txn.o $(BUILD)main.o
	$(CXX) -o ./simulation $(BUILD)simulator.o $(BUILD)peer.o $(BUILD)event.o $(BUILD)txn.o $(BUILD)main.o
