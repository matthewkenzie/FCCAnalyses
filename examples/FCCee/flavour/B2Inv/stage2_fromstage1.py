# stage2_fromstage1.py - must be in the same directory as config.py
# Saves BDT2 and BDTCOMB values for stage1 files
# Since this does not use `fccanalysis` run this using lb-conda default python (better and faster)
import os

import xgboost # Must be imported before ROOT to avoid conflicts with PyROOT
import ROOT

import numpy as np
import config as cfg
from glob import glob
from yaml import safe_load
from time import time
from datetime import timedelta

ROOT.EnableImplicitMT()

if __name__ == "__main__":
    
    #############################
    # INITIALISE
    #############################
    start = time()
    print(f"\n{30*'-'}")
    print(f"SAVE STAGE2 FILES FROM STAGE1")
    print(f"{30*'-'}\n")
    print("Initialising...")

    stage1path = cfg.fccana_opts['outputDir']['stage1']
    stage2path = cfg.fccana_opts['outputDir']['stage2']
    bdt2path = cfg.bdt2_opts['jsonPath']
    bdtCombpath = cfg.bdtComb_opts['jsonPath']

    # Info
    print(f"----> INFO: Using files from")
    print(f"{15*' '}{stage1path}")
    print(f"----> INFO: Saving files to")
    print(f"{15*' '}{stage2path}")
    print(f"----> INFO: Loading BDT2 model from")
    print(f"{15*' '}{bdt2path}")
    print(f"----> INFO: Loading BDTCOMB model from")
    print(f"{15*' '}{bdtCombpath}")

    # Load branch names used by the BDTs    
    with open(cfg.fccana_opts['yamlPath']) as stream:
        yamlFile = safe_load(stream)
        bdt2vars = stream[cfg.bdt2_opts['mvaBranchList']]
        bdtCombvars = stream[cfg.bdtComb_opts['mvaBranchList']]

    # Combine the two branchLists into one
    bdtvars = list(set(bdt2vars + bdtCombvars))

    # Get a list of all stage1 files
    stage1filepaths = {sample: os.path.join(stage1path, sample, "*.root") for sample in cfg.samples}
    stage1files = {sample: glob(stage1filepaths[sample]) for sample in cfg.samples}

    # Load the BDT models -- xgboost
    #bdt2 = xgboost.XGBClassifier()
    #bdt2.load_model(bdt2path)
    #bdtComb = xgboost.XGBClassifier()
    #bdtComb.load_model(bdtCombpath)

    # Load the BDT models -- ROOT
    ROOT.gInterpreter.ProcessLine(f'''
    TMVA::Experimental::RBDT bdt2("{cfg.bdt2_opts['mvaRBDTName']}", "{bdt2path}");
    auto computeModel2 = TMVA::Experimental::Compute<{len(bdt2vars)}, float>(bdt2);

    TMVA::Experimental::RBDT bdtComb("{cfg.bdtComb_opts['mvaRBDTName']}", "{bdtCombpath}");
    auto computeModelComb = TMVA::Experimental::Compute<{len(bdtCombvars)}, float>(bdtComb); 
    ''')

    print(f"\n{30*'-'}\n")
    for sample in cfg.samples:
        print(f"----> INFO: Found {len(stage1files[sample])} stage1 files for sample")
        print(f"{15*' '}{sample}")

        if len(stage1files[sample]) == 0:
            print(f"----> WARNING: No files found for {sample}, skipping...")
            continue

        for file in stage1files[sample]:

            # Load the ROOT file
            f = ROOT.TFile(file, "READ")
            t = f.Get("events")

            # Load the stage1 data
            df = ROOT.RDataFrame(t)

            # Save BDT prediction - xgboost
            #df = df.Define("EVT_MVA2", bdt2.predict_proba(df.AsNumpy(bdt2vars))[:, 1])
            #df = df.Define("EVT_MVACOMB", bdtComb.predict_proba(df.AsNumpy(bdtCombvars))[:, 1])

            # Save BDT prediction - ROOT
            df2 = (
                df
                .Define("MVA2Vec",     ROOT.computeModel2, bdt2vars)
                .Define("MVACOMBVec",  ROOT.computeModelComb, bdtCombvars)
                .Define("EVT_MVA2",    "MVA2Vec.at(0)")       
                .Define("EVT_MVACOMB", "MVACOMBVec.at(0)")
            )

            # Save the stage2 data
            df2.Snapshot("events", os.path.join(stage2path, sample, os.path.basename(file)))
            f.Close()

        print(f"----> INFO: Saved {len(stage1files[sample])} stage2 files\n")
    
    end = time()
    print(f"{30*'-'}")
    print(f"Execution time = {timedelta(seconds=end-start)}")
    print(f"{30*'-'}")