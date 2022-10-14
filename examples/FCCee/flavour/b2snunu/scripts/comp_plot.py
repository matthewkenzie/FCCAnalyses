import sys,os, argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import roc_curve, auc
#from root_pandas import read
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

    signal = uproot.concatenate( files=[s+":events" for s in args.signal], expressions=[args.var], library="np", entry_stop=1e6 )[args.var]
    bbbar = uproot.concatenate( files=[s+":events" for s in args.bbbar], expressions=[args.var], library="np", entry_stop=1e6 )[args.var]
    ccbar = uproot.concatenate( files=[s+":events" for s in args.ccbar], expressions=[args.var], library="np", entry_stop=1e6 )[args.var]
    qqbar = uproot.concatenate( files=[s+":events" for s in args.qqbar], expressions=[args.var], library="np", entry_stop=1e6 )[args.var]

    fig, ax = plt.subplots()

    nh, xe, _ = ax.hist( signal, label='signal', bins=args.bins, range=args.range, fill=True, alpha=0.5, density=True )
    ax.hist( bbbar, label='Z->bb', ec='C1', bins=xe, fill=False , density=True)
    ax.hist( ccbar, label='Z->cc', ec='C2', bins=xe, fill=False , density=True)
    ax.hist( qqbar, label='Z->qq', ec='C3', bins=xe, fill=False , density=True)

    ax.set_xlabel( args.var )

    fig.tight_layout()
    fig.savefig(args.output)

def listvars(signal, bbbar, ccbar, qqbar):

    branches = [ br.name for br in uproot.open( signal[0]+":events").branches ]
    print('Variables available:')
    for branch in branches:
        print('  ', branch )
    #bbbar = [ br.name for br in uproot.open( bbbar[0]+":events").branches ]
    #ccbar = [ br.name for br in uproot.open( ccbar[0]+":events").branches ]
    #qqbar = [ br.name for br in uproot.open( qqbar[0]+":events").branches ]



def main():
    parser = argparse.ArgumentParser(description='Train xgb model stage2 for Z -> bb -> b2snunu vs. Z -> qq, cc, bb')
    parser.add_argument("--signal", nargs="+", required=True, help="signal ntuples")
    parser.add_argument("--bbbar", nargs="+", required=True, help="bkg Z -> bb ntuples")
    parser.add_argument("--ccbar", nargs="+", required=True, help="bkg Z -> cc ntuples")
    parser.add_argument("--qqbar", nargs="+", required=True, help="bkg Z -> qq ntuples")
    parser.add_argument("--var", type=str, default=None, help="variable name")
    parser.add_argument("--listvars", default=False, action="store_true", help="list variables")
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument("--bins", type=int, default=50, help='Number of bins')
    parser.add_argument("--range", type=str, default=None, help='Range')

    args = parser.parse_args()

    if args.var is None:
        args.listvars = True

    if args.listvars:
        listvars(args.signal, args.bbbar, args.ccbar, args.qqbar)
    else:
        run(args) #args.signal, args.inclusive_bbbar, args.inclusive_ccbar, args.inclusive_qqbar, args.var, args.output)

if __name__ == '__main__':
    main()
