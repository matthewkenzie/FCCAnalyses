import sys,os, argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import roc_curve, auc
import uproot
import ROOT
import joblib
import glob

from matplotlib import rc
rc('font',**{'family':'serif','serif':['Roman']})
rc('text', usetex=True)

#Local code
import config as cfg

def run(args):

    varlist = cfg.train_var_lists[args.vars]

    nfiles = len(args.input)

    prc_evs = sum( [ uproot.open(fname)["metadata"]["eventsProcessed"].array(library="pd")[0] for fname in args.input ] )
    st2_evs = sum( [ uproot.open(fname)["events"].num_entries for fname in args.input ] )

    tot_evs = 0
    kep_evs = 0
    df = None
    for inf in args.input:
        if df is not None:
            if len(df)>args.n_events:
                break
        with uproot.open(inf+":events") as tree:
            cut = None
            tot_evs += tree.num_entries
            if args.ediff_cut is not None:
                cut = f"EVT_ThrustDiff_E{args.ediff_cut}"
            tf = tree.arrays( library="pd", filter_name=varlist, cut=cut )
            kep_evs += len(tf)
            if df is None:
                df = tf
            else:
                df = pd.concat( [df,tf] )

    #out_eff = { 'processed': { 'total': prc_evs, 'passed': st2_evs, 'efficiency': st2_evs / prc_evs } }
    out_eff = {}
    out_eff["efficiency"] = st2_evs / prc_evs

    if args.ediff_cut is not None:
        #out_eff['ediff_cut'] = { 'total': tot_evs, 'passed': kep_evs, 'efficiency': kep_evs / tot_evs }
        out_eff["efficiency"] = (st2_evs / prc_evs) * (kep_evs / tot_evs)

    print(out_eff)
    with open(args.output_eff,'w') as f:
        json.dump(out_eff, f)

    print(df)

    df.to_pickle(args.output)

def main():
    parser = argparse.ArgumentParser(description='Prepare training files for stage2 for Z -> bb -> b2snunu vs. Z -> qq, cc, bb')
    parser.add_argument("--input", nargs="+", default=[], required=True, help="signal ntuples")
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('--output_eff', type=str, required=True, help='Output efficiency file.')
    parser.add_argument('--decay', type=str, required=True, help='Select the decay.')
    parser.add_argument('--n_events', type=int, default=1e6, help='Max size of each sample')
    parser.add_argument('--vars', type=str, required=True, help='Select the variables to keep, e.g "train_vars_vtx", "train_vars_stage2"')
    parser.add_argument('--ediff_cut', type=str, default=None, help='Apply cut to EVT_ThrustDiff_E, e.g. ">5"')
    args = parser.parse_args()

    print( args.input )

    assert( args.vars in cfg.train_var_lists.keys() )

    run(args)

if __name__ == '__main__':
    main()

