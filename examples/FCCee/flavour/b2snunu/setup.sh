source /cvmfs/fcc.cern.ch/sw/latest/setup.sh
cd FCCeePhysicsPerformance/case-studies/flavour/tools
source install.sh $PWD/localPythonTools
cd ../../../../FCCAnalyses/
source ./setup.sh
mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install
#pip3 install --user xgboost #hopefully I can get this to work in the initial setup