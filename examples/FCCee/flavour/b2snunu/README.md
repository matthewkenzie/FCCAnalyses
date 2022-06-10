# Contact
- Yasmine Amhis (yasmine.sara.ahmis@cern.ch)
- Matt Kenzie (matthew.william.kenzie@cern.ch)
- Aidan Wiederhold (aidan.richard.wiederhold@cern.ch)

# Environment Setup

## Initial Setup
- Clone the repos (pull from someone's fork/branch if needed): [FCCeePhysicsPerformance](https://github.com/HEP-FCC/FCCeePhysicsPerformance) and [FCCAnalyses](https://github.com/HEP-FCC/FCCAnalyses)
- Either follow the instructions below or just do: `source ./FCCAnalyses/examples/FCCee/flavour/b2snunu/setup.sh`
- Start off in FCCeePhysicsPerformance to install Snakemake locally (hopefully it will get added to the FCC stack)
```bash
cd FCCeePhysicsPerformance/case-studies/flavour/tools
source /cvmfs/fcc.cern.ch/sw/latest/setup.sh
source install.sh $PWD/localPythonTools
```
- Now go to FCCAnalyses to pick up the FCC specific stuff
```bash
cd ../../../../FCCAnalyses/
source ./setup.sh
mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install
pip3 install --user xgboost #hopefully I can get this to work in the initial setup
```

## When starting up a new shell either follow the instructions below or just do `source ./FCCAnalyses/examples/FCCee/flavour/b2snunu/startup.sh`
- Pick up local packages such as Snakemake
```bash
cd FCCeePhysicsPerformance/case-studies/flavour/tools
source /cvmfs/fcc.cern.ch/sw/latest/setup.sh
source ./localSetup.sh $PWD/localPythonTools
```
- Pick up FCC software # TODO do we really need to do this bit every time?
```bash
cd ../../../../FCCAnalyses/
source ./setup.sh
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install
```
<br />

# Running The Analysis
## Where To Run From
All of the code used in this analysis is designed to be used from the `FCCAnalyses/examples/FCCee/flavour/b2snunu/` directory assuming that the `FCCAnalyses` and `FCCeePhysicsPerformance` repositories have been cloned alongside each other.

## EOS Cache
In order to speed up Snakemake solving the workflow we cache the files available in EOS in a JSON, using `scripts/eos_cacher.py` so that Snakemake doesn't need to verify their existence every time it runs. However the current environment doesn't include XRootD which is used to glob the EOS directory remotely. Instead of the analysis environment you should use any environment with XRootD available to create the bookkeeping json and then proceed to use the analysis environment described above for the rest of the analysis. Hopefully I can get XRootD working in the analysis environment so we can avoid switching environments just for this. A suitable environment for running `scripts/eos_cacher.py` can be created by doing `mamba env create -f environment.yaml` using the `yaml` in `FCCAnalyses/examples/FCCee/flavour/b2snunu/`.

The final file of the workflow that depends on all possible steps is `./output/snakemake_flags/all` so request this from Snakemake if you want to run the entire analysis.

## To run the workflow locally
```bash
cd FCCAnalyses/examples/FCCee/flavour/b2snunu/
snakemake <target_output> -s ./scripts/Snakefile --jobs N --latency-wait 120
```

## To run the workflow on a Slurm cluster (deprecated method)
```bash
cd FCCAnalyses/examples/FCCee/flavour/b2snunu/
snakemake <target_output> -s ./scripts/Snakefile --jobs N --latency-wait 120 --cluster ./scripts/slurm_wrapper.py; mv ./slurm-* ./SlurmLogs
```
Other cluster types are possible but require a different wrapper which shouldn't be hard to make based off of our Slurm one.

## To run the workflow on a cluster (new method)
```bash
TODO
```
<br />

# Workflow Description

## Workflow Control
- `scripts/config.py` defines all objects that are common to the various scripts. In particular any non-integer wildcards used in the `Snakefile` have their constraints defined based on lists in `config.py`.
- `scripts/Snakefile` defines all the rules and their wildcards that control the workflow.
- `scripts/eos_cacher.py` creates a bookkeeping `json` for all the MC to avoid telling Snakemake about it all directly as that results in extremely slow workflow solving. This also groups the MC for grouped processing by analysis scripts and picks which portion of the MC will be used for training/testing the BDTs.

## BDT and Initial Tuple Production
- `scripts/stage1.py` is used in `training` mode to produce some tuples from a randomly selected (by `scripts/eos_cacher.py`) 20% of the available MC to be used for training the BDT.
- NOT IMPLEMENTED `scripts/pickler.py` is used to turn the output of `scripts/stage1.py` into `pickle` files for input to `XGBoost`.
- `FCCeePhysicsPerformance/case-studies/flavour/b2snunu/train_xgb.py` is used to train a BDT and save the weights.
- `scripts/stage1.py` is then used not in `training` mode to produce tuples with an MVA branch but no MVA cut applied.
- `scripts/mva_plot.py` produces plots of MVA response in training/testing tuples to study the performance.
- NOT IMPLEMENTED `scripts/mva_cut.py` finds an optimal cut to apply to the tuples.
- NOT IMPLEMENTED `scripts/bkg_types.py` adds branches to the tuples corresponding to the true PDG IDs of the signal candidate, their siblings and (grand)parents to be used to determine the types of background decays present after the MVA filtering.
<br />

# What to do if something breaks
- Check if `master` has been updated in either FCCAnalyses or FCCeePhysicsPerformance as this may be related to some deeper changes in the stack that are harder to track. Pulling these updates should hopefully fix things.