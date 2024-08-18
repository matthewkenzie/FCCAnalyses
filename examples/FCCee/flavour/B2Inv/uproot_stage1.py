import os
import sys
import uproot
import time
import ROOT

import pandas as pd
import numpy as np
import xgboost as xgb
import awkward as ak

from yaml import YAMLError, safe_load

if __name__ == "__main__":
    import argparse
    from glob import glob

    parser = argparse.ArgumentParser(description="Saves EVT_MVA1 branch", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input',nargs="+", required=True, help='Select the input file(s).')
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('--config', type=str, required=True, help='Select the config YAML file.')
    parser.add_argument('--branchnames', type=str, default='stage1-vars', help='Choose the key pointing to stage1 variables in the YAML file')
    parser.add_argument('--bdtnames', type=str, default='bdt1-training-vars', help='Choose the key pointing to bdt training variables in the YAML file')
    parser.add_argument('--MVA_cut', default = None, type=float, help='Choose the MVA cut.')
    parser.add_argument('--mva', default="", type=str, help='Path to the trained MVA ROOT file.')
    args = parser.parse_args()
    print("Initialising...")
    if not os.path.exists( args.config ):
        raise RuntimeError(f"Looking for a config file that doesn't exist {args.config}")
    
    with open(args.config) as stream:
        yaml = safe_load(stream)
        bdt1_training_vars = yaml[args.bdtnames]
        stage1_vars        = yaml[args.branchnames]

    #if not args.training:
    #    if not os.path.exists( args.mva ):
    #        raise RuntimeError(f"Looking for an MVA file that doesn't exist {args.mva}")
    
    if '*' in args.input:
        file_list = glob(args.input)
    else:
        file_list = args.input

    print("===============================STARTUP SUMMARY===============================")
    #print(f"Training Mode     : {args.training}")
    print(f"Input File(s)     : {args.input}")
    print(f"Output File       : {args.output}")
    print(f"Config File       : {args.config}")
    print(f"MVA Cut           : {args.MVA_cut}")
    print("=============================================================================")
    
    start = time.time()
    bdt = xgb.XGBClassifier()
    bdt.load_model(args.mva)
    print("BDT model loaded")
    print("Running")
    with uproot.recreate(args.output) as outfile:
        print(f"Opening {args.output} as WritableFile\n")
        # Create objects to be filled
        #out_df = { key : np.array([]) for key in stage1_vars+["EVT_MVA1"] }
        out_df = ak.Array([])
        totmva = np.array([])
        n_events = 0
        n_selected = 0
        for file in file_list:
            with uproot.open(file) as f:
                tree = f["events"]
                n_events += int(f["eventsSelected"])
                df = uproot.concatenate(tree, expressions=bdt1_training_vars, library='pd')

                mva = bdt.predict_proba(df)[:, 1]
                print(f"BDT score evaluated for {file}")
                cut = mva > args.MVA_cut
                df = uproot.concatenate(tree)[cut]
                n_selected += len(df)
                
                out_df = ak.concatenate([out_df, df])
                #for key in stage1_vars:
                #    out_df[key] = np.append(out_df[key], df[key], axis=0)
                
                totmva = np.append(totmva, mva[cut])

                print(f"Saved {len(df)} out of {int(f['eventsSelected'])} events from {file} to output")
        
        fields = ak.fields(out_df)
        fields.append("EVT_MVA1")
        records = ak.unzip(out_df)
        records = records + (totmva,)
        outfile["events"] = ak.zip({fields[i]: records[i] for i in range(len(fields))}, depth_limit = 1)

    file = ROOT.TFile(args.output, "UPDATE")
    p = ROOT.TParameter(int)("eventsProcessed", n_events)
    p.Write()
    q = ROOT.TParameter(int)("eventsSelected", n_selected)
    q.Write()
    file.Write()
    file.Close()

    elapsed_time = time.time() - start
    print  ("==============================COMPLETION SUMMARY=============================")
    print  ("Elapsed time (H:M:S)     :  ",time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print  ("Events Processed/Second  :  ",int(n_events/elapsed_time))
    print  ("Total Events Processed   :  ",int(n_events))
    print  ("Total Events Selected    :  ",int(n_selected))
    print  ("Preliminary efficiency   :  ",(n_selected/n_events))
    print  ("=============================================================================")
