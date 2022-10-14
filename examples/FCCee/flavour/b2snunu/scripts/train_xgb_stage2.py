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

def read_eff(fname):
    with open(fname) as f:
        dic = json.load(f)
    return dic['efficiency']

def run(args):

    print('Signal file:')
    print('    sig:  ', args.signal)
    print('Background files:')
    print('    bbbar:', args.bbbar)
    print('    ccbar:', args.ccbar)
    print('    qqbar:', args.qqbar)


    vars_list = cfg.train_vars_stage2
    print("TRAINING VARS")
    print(vars_list)

    # read efficiencies
    print('READING EFFICIENCIES')
    stage2_efficiencies = {}
    bkgs = list(cfg.branching_fractions.keys())
    for mode, eff in zip( ['signal']+bkgs, [args.signal_eff, args.bbbar_eff, args.ccbar_eff, args.qqbar_eff] ):
        stage2_efficiencies[mode] = read_eff(eff)

    #print("Expected efficiencies")
    #print(cfg.stage2_efficiencies)
    print("Actual efficiencies")
    print(stage2_efficiencies)

    df_sig = pd.read_pickle( args.signal )

    df_sig = df_sig.sample(int(1e6), random_state=10)
    print(f"Number of signal events: {len(df_sig)}")

    df_bkg = {}
    for bkg in bkgs:
        print(f"Stage2 efficiency of {bkg}: {stage2_efficiencies[bkg]}")

    total_bkg = 1e6
    total_BF = sum([stage2_efficiencies[bkg]*cfg.branching_fractions[bkg] for bkg in bkgs])
    # sample each bkg to weight them against their BF and efficiency
    for bkg in bkgs:
        print(f"Desired number of {bkg} events: {int(total_bkg*(stage2_efficiencies[bkg]*cfg.branching_fractions[bkg]/total_BF))}")
    for bkg, bkg_file in zip(bkgs, [args.bbbar, args.ccbar, args.qqbar]):
        df_bkg[bkg] = pd.read_pickle(bkg_file)
        sample_n = int(total_bkg*(stage2_efficiencies[bkg]*cfg.branching_fractions[bkg]/total_BF))
        if sample_n<= len(df_bkg[bkg]):
            df_bkg[bkg] = df_bkg[bkg].sample(n=sample_n,random_state=10)
        print(f"Number of {bkg} events in combined sample: {len(df_bkg[bkg])}")

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
    print('Plotted ROC curve to', args.roc_plot)
    fig.savefig(args.roc_plot)

    print("Writing xgboost model to ROOT file")
    ROOT.TMVA.Experimental.SaveXGBoost(bdt, f"{args.decay}_BDT", args.output, num_inputs=len(vars_list))

    #Write model to joblib file
    joblib.dump(bdt, args.output_joblib)

def main():
    parser = argparse.ArgumentParser(description='Train xgb model stage2 for Z -> bb -> b2snunu vs. Z -> qq, cc, bb')
    parser.add_argument("--signal", type=str, required=True, help="signal pkl")
    parser.add_argument("--bbbar" , type=str, required=True, help="bkg Z -> bb pkl")
    parser.add_argument("--ccbar" , type=str, required=True, help="bkg Z -> cc pkl")
    parser.add_argument("--qqbar" , type=str, required=True, help="bkg Z -> qq pkl")
    parser.add_argument("--signal_eff", type=str, required=True, help="signal eff")
    parser.add_argument("--bbbar_eff" , type=str, required=True, help="bkg Z -> bb eff")
    parser.add_argument("--ccbar_eff" , type=str, required=True, help="bkg Z -> cc eff")
    parser.add_argument("--qqbar_eff" , type=str, required=True, help="bkg Z -> qq eff")
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('--output_joblib', type=str, required=True, help='Select the output file.')
    parser.add_argument('--roc_plot', type=str, required=True, help='Select the output file.')
    parser.add_argument('--decay', type=str, required=True, help='Select the decay.')

    args = parser.parse_args()

    run(args)

if __name__ == '__main__':
    main()
