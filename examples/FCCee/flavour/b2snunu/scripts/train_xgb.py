import sys,os, argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import roc_curve, auc
#from root_pandas import read_root
import uproot
import ROOT
import joblib
import glob

from matplotlib import rc
rc('font',**{'family':'serif','serif':['Roman']})
rc('text', usetex=True)

#Local code
import config as cfg

def run(vars, signal_pkl, bbbar_pkl, ccbar_pkl, qqbar_pkl, signal_root, bbbar_root, ccbar_root, qqbar_root, output_root, output_joblib, roc_plot, decay):

    print(signal_pkl, bbbar_pkl, ccbar_pkl, qqbar_pkl, signal_root, bbbar_root, ccbar_root, qqbar_root)

    #Bd -> Kst nu nu signal
    if(vars=="normal"):
        vars_list = cfg.train_vars
    elif(vars=="vtx"):
        vars_list = cfg.train_vars_vtx
    print("TRAINING VARS")
    print(vars_list)

    total_bkg = 1e6

    # count generated events
    bkgs = cfg.branching_fractions.keys()
    stage1_efficiencies = {}
    generated_events = {}
    for bkg, bkg_files in zip(bkgs, [bbbar_root, ccbar_root, qqbar_root]):
        generated_events[bkg] = 0
        for f in bkg_files:
            with uproot.open(f) as inf:
                generated_events[bkg] += int(inf["metadata"]["eventsProcessed"].array(library="pd")[0])

    generated_events["signal"] = 0
    for f in signal_root:
        with uproot.open(f) as inf:
            generated_events["signal"]+= int(inf["metadata"]["eventsProcessed"].array(library="pd")[0])

    # count events that pass stage1 and calculate efficiencies
    df_bkg = {}
    available_events = {}
    for bkg, bkg_files in zip(bkgs, [bbbar_pkl, ccbar_pkl, qqbar_pkl]):
        print(f"{bkg = }")
        df_bkg[bkg] = pd.read_pickle(bkg_files[0])
        df_bkg[bkg] = pd.concat([pd.read_pickle(input_file) for input_file in bkg_files])
        df_bkg[bkg] = df_bkg[bkg][vars_list]
        available_events[bkg] = len(df_bkg[bkg])
        print(f"Number of available {bkg} events: {available_events[bkg]}")
        stage1_efficiencies[bkg] = float(available_events[bkg])/generated_events[bkg]

    df_sig = pd.concat([pd.read_pickle(input_file) for input_file in signal_pkl])
    df_sig = df_sig[vars_list]
    stage1_efficiencies["signal"] = float(len(df_sig))/generated_events["signal"]
    print(f"Wasted signal events: {len(df_sig) - 1e6}")

    print("Expected efficiencies")
    print(cfg.stage1_efficiencies)
    print("Actual efficiencies")
    print(stage1_efficiencies)

    df_sig = df_sig.sample(int(1e6), random_state=10)
    print(f"Number of signal events: {len(df_sig)}")

    for bkg in bkgs:
        print(f"Generated {bkg} events: {generated_events[bkg]}")
        print(f"Stage1 efficiency of {bkg}: {stage1_efficiencies[bkg]}")

    total_BF = sum([stage1_efficiencies[bkg]*cfg.branching_fractions[bkg] for bkg in bkgs])
    # sample each bkg to weight them against their BF and efficiency
    for bkg in bkgs:
        print(f"Desired number of {bkg} events: {int(total_bkg*(stage1_efficiencies[bkg]*cfg.branching_fractions[bkg]/total_BF))}")
    for bkg in bkgs:
        df_bkg[bkg] = df_bkg[bkg].sample(n=int(total_bkg*(stage1_efficiencies[bkg]*cfg.branching_fractions[bkg]/total_BF)),random_state=10)
        print(f"Number of {bkg} events in combined sample: {len(df_bkg[bkg])}")
        print(f"Wasted events for {bkg}: {available_events[bkg] - len(df_bkg[bkg])}")

    #Make a combined background sample according to BFs
    for bkg in bkgs:
        df_bkgs = pd.concat([df_bkg[bkg] for bkg in bkgs])
    df_bkgs = df_bkgs.sample(frac=1)
    print(f"Total bkg events: {len(df_bkgs)}")

    #Signal and background labels
    df_sig["label"] = 1
    df_bkgs["label"] = 0

    #Combine the datasets
    df = pd.concat([df_sig, df_bkgs])

    #Split into class label (y) and training vars (x)
    y = df["label"]
    x = df[vars_list]

    y = y.to_numpy()
    x = x.to_numpy()

    #Sample weights to balance the classes
    weights = compute_sample_weight(class_weight='balanced', y=y)

    #BDT
    config_dict = {
            "n_estimators": 400,
            "learning_rate": 0.3,
            "max_depth": 3,
            }

    bdt = xgb.XGBClassifier(n_estimators=config_dict["n_estimators"],
                            max_depth=config_dict["max_depth"],
                            learning_rate=config_dict["learning_rate"],
                            )

    #Fit the model
    print("Training model")
    bdt.fit(x, y, sample_weight=weights)

    feature_importances = pd.DataFrame(bdt.feature_importances_,
                                     index = vars_list,
                                     columns=['importance']).sort_values('importance',ascending=False)

    print("Feature importances")
    print(feature_importances)

    #Create ROC curves
    decisions = bdt.predict_proba(x)[:,1]

    # Compute ROC curves and area under the curve
    fpr, tpr, thresholds = roc_curve(y, decisions)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(8,8))
    plt.plot(tpr, 1-fpr, lw=1.5, color="k", label='ROC (area = %0.3f)'%(roc_auc))
    plt.plot([0.45, 1.], [0.45, 1.], linestyle="--", color="k", label='50/50')
    plt.xlim(0.45,1.)
    plt.ylim(0.45,1.)
    plt.ylabel('Background rejection',fontsize=30)
    plt.xlabel('Signal efficiency',fontsize=30)
    ax.tick_params(axis='both', which='major', labelsize=25)
    plt.legend(loc="upper left",fontsize=20)
    plt.grid()
    plt.tight_layout()
    print('Plotted ROC curve to', roc_plot)
    fig.savefig(roc_plot)

    print("Writing xgboost model to ROOT file")
    ROOT.TMVA.Experimental.SaveXGBoost(bdt, f"{decay}_BDT", output_root, num_inputs=len(vars_list))

    #Write model to joblib file
    joblib.dump(bdt, output_joblib)

def main():
    parser = argparse.ArgumentParser(description='Train xgb model for Z -> bb -> b2snunu vs. Z -> qq, cc, bb')
    parser.add_argument("--vars", choices=["normal","vtx"], required=True, help="Event-level vars (normal) or added vertex vars (vtx)")
    parser.add_argument("--signal_pkl", nargs="+", required=True, help="signal ntuples")
    parser.add_argument("--inclusive_bbbar_pkl", nargs="+", required=True, help="bkg Z -> bb ntuples")
    parser.add_argument("--inclusive_ccbar_pkl", nargs="+", required=True, help="bkg Z -> cc ntuples")
    parser.add_argument("--inclusive_qqbar_pkl", nargs="+", required=True, help="bkg Z -> qq ntuples")
    parser.add_argument("--signal_root", nargs="+", required=True, help="signal ntuples")
    parser.add_argument("--inclusive_bbbar_root", nargs="+", required=True, help="bkg Z -> bb ntuples")
    parser.add_argument("--inclusive_ccbar_root", nargs="+", required=True, help="bkg Z -> cc ntuples")
    parser.add_argument("--inclusive_qqbar_root", nargs="+", required=True, help="bkg Z -> qq ntuples")
    parser.add_argument('--output_root', type=str, required=True, help='Select the output file.')
    parser.add_argument('--output_joblib', type=str, required=True, help='Select the output file.')
    parser.add_argument('--roc_plot', type=str, required=True, help='Select the output file.')
    parser.add_argument('--decay', type=str, required=True, help='Select the decay.')

    args = parser.parse_args()

    run(args.vars, args.signal_pkl, args.inclusive_bbbar_pkl, args.inclusive_ccbar_pkl, args.inclusive_qqbar_pkl, args.signal_root, args.inclusive_bbbar_root, args.inclusive_ccbar_root, args.inclusive_qqbar_root, args.output_root, args.output_joblib, args.roc_plot, args.decay)

if __name__ == '__main__':
    main()
