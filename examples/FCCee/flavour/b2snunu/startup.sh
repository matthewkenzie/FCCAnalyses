cd FCCeePhysicsPerformance/case-studies/flavour/tools
source /cvmfs/fcc.cern.ch/sw/latest/setup.sh
source ./localSetup.sh $PWD/localPythonTools
cd ../../../../FCCAnalyses/
source ./setup.sh
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install