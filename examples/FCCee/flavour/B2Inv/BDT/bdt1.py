# BDT1 using stage1 files
import xgboost as xgb # Has to be imported first to avoid conflicts with PyROOT

import sys
sys.path.append("/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv/")

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

from time import time
from glob import glob
from yaml import safe_load, YAMLError
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import roc_curve, auc, accuracy_score

import config as cfg

ROOT.EnableImplicitMT()

# Return list of variables to use in the bdt as a python list
def vars_fromyaml(path, bdtlist):
    with open(path) as stream:
        try:
            file = safe_load(stream)
            bdtvars = file[bdtlist]
        except YAMLError as exc:
            print(exc)

    return bdtvars

def check_inputpath(inputpath):
    if not os.path.exists(inputpath):
        raise FileNotFoundError(f"{inputpath} does not exist")
    return inputpath

def set_outputpath(outputpath):
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    return outputpath

#############################
# LOAD_DATA FUNCTION
#############################
def load_data(filenames, category, eff, cols):
    df = ROOT.RDataFrame("events", filenames)
    df_np = df.AsNumpy(columns=cols)
    x = pd.DataFrame(df_np)

    if category=='signal':
        y = pd.DataFrame(np.ones(x.shape[0]), columns=['category'])
    elif category=='background':
        y = pd.DataFrame(np.zeros(x.shape[0]), columns=['category'])
    else:
        raise ValueError(f"{category} is invalid, must be 'signal' or 'background'")

    #w = pd.DataFrame(eff*np.ones(x.shape[0]), columns=['weights'])
    # For correct weighting must divide by the total number of events of each type
    w = pd.DataFrame(eff*np.ones(x.shape[0]), columns=['weights'])

    return x, y, w

#############################
# PLOTTERS
#############################
def plot_bdt_response(x, title):
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    for sample in x:
        if sample in cfg.sample_allocations['signal']:
            ax.hist(x[sample]['XGB'], bins=100, density=True, histtype='stepfilled', color='gold', label=cfg.titles[sample])
        else:
            ax.hist(x[sample]['XGB'], bins=100, density=True, histtype='step', label=cfg.titles[sample])
   
    ax.set_xlabel("BDT Response")
    ax.set_ylabel("Normalised counts")
    #ax.set_xlim((0, 1))
    ax.legend(loc='best')
    ax.set_title(title)
    fig.tight_layout()

def plot_roc(bdt, x_test, y_test, w_test):
    y_score = bdt.predict_proba(x_test)[:,1]
    fpr, tpr, thresholds = roc_curve(y_test, y_score, sample_weight=w_test)
    area = auc(fpr, tpr)

    plt.plot([0, 1], [0, 1], color='grey', linestyle='--')
    plt.plot(fpr, tpr, label=f'ROC curve (AUC = {area:.4f})')
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc='lower right')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()

#def plot_significance(bdt, x_test, y_test, w_test, n_sig, n_bkg):
#    y_score = bdt.predict_proba(x_test)[:,1]
#    fpr, tpr, thresholds = roc_curve(y_test, y_score, sample_weight=w_test)
#    S = n_sig*tpr
#    B = n_bkg*fpr
#    epsilon = 1e-10
#    metric = S/np.sqrt(S+B+epsilon)
#
#    plt.plot(thresholds, metric, label=f'XGB')
#    plt.xlabel('$P_{XGB}$ cut value')
#    plt.ylabel('Signal significance: $\\frac{S}{\\sqrt{S+B}}$')
#    plt.xlim(0, 1)
#
#    optimal_cut = thresholds[np.argmax(metric)]
#    plt.axvline(optimal_cut, color='black', linestyle='--', label = f'Optimal cut ({optimal_cut:.3f})')
#    plt.legend(loc='best')
#    plt.tight_layout()

def plot_punzi_significance(x, cuts, sigma):
    n_before = {sample: x[sample].shape[0] for sample in x}
    B = np.array([])
    epsilon_s = np.array([])
    for cut in cuts:
        temp_B = 0
        for sample in x:
            if sample in cfg.sample_allocations['signal']:
                before = len(x[sample])
                after  = len(x[sample].query(f"XGB > {cut}"))
                epsilon_s = np.append(epsilon_s, after/before)
            else:
                before = len(x[sample])
                after  = len(x[sample].query(f"XGB > {cut}"))
                count = 6e12*cfg.branching_fractions[sample][0]*cfg.efficiencies['presel'][sample]*after/before
                temp_B += count
        
        B = np.append(B, temp_B)

    fig, ax = plt.subplots()
    punzi = np.divide(epsilon_s, np.sqrt(B) + sigma/2)
    ax.plot(cuts, punzi)
    ax.axvline(cuts[np.argmax(punzi)], color='black', 
               linestyle='--', label = f'Optimal cut ({cuts[np.argmax(punzi)]:.3f})')
    ax.set_xlabel('BDT1 cut value')
    ax.set_ylabel(r'$\frac{\epsilon_s}{\sqrt{B} + \sigma/2}$'+f' for sigma={sigma}')
    ax.set_title('Punzi significance for BDT1')
    ax.legend(loc='best')
    fig.tight_layout()

def plot_significance(x, bdtvals, branching_fracs):
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    for bdt in bdtvals:
        S = np.array([])
        B = 0
        for sample in x:
            if sample in cfg.sample_allocations['signal']:
                before = len(x[sample])
                after  = len(x[sample].query(f"XGB > {bdt}"))
                temp_S = 6e12*cfg.branching_fractions['p8_ee_Zbb_ecm91'][0]*2*cfg.prod_frac['Bs']*cfg.efficiencies['presel'][sample]*after/before*branching_fracs
                S = np.append(S, temp_S)
            else:
                before = len(x[sample])
                after  = len(x[sample].query(f"XGB > {bdt}"))
                count = 6e12*cfg.branching_fractions[sample][0]*cfg.efficiencies['presel'][sample]*after/before
                B += count
    
        significance = np.divide(S, np.sqrt(S+B+1e-10))
        ax.plot(bdt, significance, label=f'BDT1 > {bdt:.3f}')
    
    ax.axvline(1e-6, color='black', linestyle='--')
    ax.set_xlabel(r'$\mathcal{B}(B_s\to\nu\bar{nu})$')
    ax.set_ylabel(r'$\frac{S}{\sqrt{S+B}}$')
    ax.legend(loc='best')
    ax.set_title('BDT1 significance (expected "signal to noise" ratio)')
    fig.tight_layout()

def plot_feature(x, cut, responsevars):
    fig, ax = plt.subplots()
    for sample in x:
        if sample in cfg.sample_allocations['signal']:
            ax.hist(x[sample].query(f"XGB > {cut}")[responsevars[0]], bins=100, density=True, histtype='stepfilled', color='gold', label=cfg.titles[sample])
        else:
            ax.hist(x[sample].query(f"XGB > {cut}")[responsevars[0]], bins=100, density=True, histtype='step', label=cfg.titles[sample])
    
    ax.set_xlabel(f'{responsevars[0]}')
    ax.set_ylabel("Density")
    ax.legend(loc='best')
    ax.set_title(f"{responsevars[0]} with BDT1 > {cut}")
    fig.tight_layout()

#############################
# MAIN
#############################
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--trainfrac", type=float, default=0.75, required=True, help="Fraction of data to use for training")
    parser.add_argument("--save-model", default=False, action='store_true', help="Save model to output file")
    parser.add_argument("--plot-results", default=False, action='store_true', help="Plot and save BDT responses")
    parser.add_argument("--nchunks", nargs='*', default=None, help="Number of chunks to process, default is None (all are processed)")
    args = parser.parse_args()

    start = time()
    print(f"\n{30*'-'}")
    print(f"BDT1 TRAINING")
    print(f"{30*'-'}\n")
    print("Initialising...")

    #############################
    # PREPROCESSING
    #############################
    # Load configuration
    plt.style.use('fcc.mplstyle')
    inputpath    = check_inputpath(cfg.xgb1_train_opts['inputpath'])
    outputpath   = set_outputpath(cfg.xgb1_train_opts['outputpath'])
    yamlpath     = check_inputpath(cfg.ana_opts['yamlPath'])
    bdtvars      = vars_fromyaml(yamlpath, cfg.bdt1_opts['mvaBranchList'])
    responsevars = ["EVT_hemisEmin_Emiss"]

    # Efficiencies of pre-selection cuts + branching fraction
    bfs = {sample: cfg.branching_fractions[sample][0] for sample in cfg.samples}
    
    eff = {sample: cfg.efficiencies['presel'][sample] for sample in cfg.samples}  
    
    print("Efficiencies loaded")
    print(f"Using {cfg.bdt1_opts['mvaBranchList']} from {yamlpath}")
    print(f"Loading files from {inputpath}")
    print(f"Output will be saved to {outputpath}")
    print(f"{30*'-'}\n")
    
    paths = {sample: os.path.join(inputpath, cfg.samples[sample], "*.root") for sample in cfg.samples}
    
    if (args.nchunks is not None) & (len(args.nchunks) == 1):
        print(f"Using {args.nchunks[0]} chunks for each sample")
        files = {sample: glob(paths[sample])[:args.nchunks[0]] for sample in cfg.samples}
    
    elif (args.nchunks is not None) & (len(args.nchunks) == len(cfg.samples)):
        print(f"Using {args.nchunks} chunks for each sample respectively")
        files = {sample: glob(paths[sample])[:args.nchunks[i]] for i, sample in enumerate(cfg.samples)}
    else:
        print(f"args.nchunks = {args.nchunks} is either null or invalid, using all files")
        files = {sample: glob(paths[sample]) for sample in cfg.samples}
    
    x = {sample: None for sample in cfg.samples}
    y = {sample: None for sample in cfg.samples}
    w = {sample: None for sample in cfg.samples}

    for sample in cfg.samples:
        if sample in cfg.sample_allocations['signal']:
            x[sample], y[sample], w[sample] = load_data(files[sample], 'signal', eff[sample]*bfs[sample], bdtvars+responsevars)
        else: 
            x[sample], y[sample], w[sample] = load_data(files[sample], 'background', eff[sample]*bfs[sample], bdtvars+responsevars)

    x_train = pd.concat([x[sample].sample(frac=args.trainfrac, random_state=7) for sample in cfg.samples], copy=True, ignore_index=True)
    y_train = pd.concat([y[sample].sample(frac=args.trainfrac, random_state=7) for sample in cfg.samples], copy=True, ignore_index=True)
    # Normalise weights by dividing by the total number of events of each type
    w_train = pd.concat([w[sample].sample(frac=args.trainfrac, random_state=7)/len(x[sample].sample(frac=args.trainfrac, random_state=7)) for sample in cfg.samples], copy=True, ignore_index=True)
    
    # Create test dataframes
    x_test = pd.concat([x[sample].drop(x_train.index) for sample in cfg.samples], copy=True, ignore_index=True)
    y_test = pd.concat([y[sample].drop(y_train.index) for sample in cfg.samples], copy=True, ignore_index=True)
    # Normalise weights by dividing by the total number of events of each type
    w_test = pd.concat([w[sample].drop(w_train.index)/len(w[sample].drop(w_train.index)) for sample in cfg.samples], copy=True, ignore_index=True)

    print(f"\n")
    for sample in cfg.samples:
        print(f"Number of {sample} events = {x[sample].shape[0]}")

    print(f"\n")
    print("Preprocessing done")
    print(f"Using {len(x_train)} events to train")
    print(f"Using {len(x_test)} events to test")
    print(f"{30*'-'}\n")
    
    #############################
    # TRAINING
    #############################
    # Define BDT
    config_dict = {
        "n_estimators": 200,
        "learning_rate": 0.3,
        "max_depth": 3,
        "subsample": 1.0,
    }
    
    param_grid = {
        "n_estimators": [50, 150, 400],
        "learning_rate": [0.01, 0.1, 0.3],
        "max_depth": [3, 5],
        "subsample": [0.5, 0.7, 1.0],
        "colsample_bytree": [0.7, 1.0],
        "gamma": [0, 0.2],
        "min_child_weight": [1, 5],
    }

    bdt = xgb.XGBClassifier()
    # Use GridSearchCV to find the best hyperparameters
    # Need to convert to numpy to save to ROOT TMVA file
    grid_search = GridSearchCV(estimator=bdt, param_grid=param_grid, cv=4, scoring="roc_auc", verbose=True, n_jobs=-1)
    grid_search.fit(x_train[bdtvars].to_numpy(), y_train.to_numpy(), sample_weight=w_train.to_numpy())
    
    print(f"Best cross validation score = {grid_search.best_score_}")
    print(f"Best params = {grid_search.best_params_}")

    best_bdt = grid_search.best_estimator_
    data_dmatrix = xgb.DMatrix(data=x_train[bdtvars].to_numpy(), label=y_train.to_numpy(), weight=w_train.to_numpy())
    xgb_cv = xgb.cv(dtrain=data_dmatrix, params=config_dict, nfold=4, num_boost_round=50, early_stopping_rounds=10, metrics="auc", as_pandas=True, seed=123)
    print(f"{30*'-'}")
    print("BDT OUTPUT")
    print(xgb_cv.head())
    
    #############################
    # VALIDATION
    #############################
    val_score = best_bdt.score(x_test[bdtvars], y_test, sample_weight=w_test)
    print(f"\nValidation score = {val_score}")

    #############################
    # SAVING MODEL
    #############################
    if args.save_model:
        best_bdt.save_model(os.path.join(outputpath, "bdt1.json"))
        ROOT.TMVA.Experimental.SaveXGBoost(bdt, "bdt", os.path.join(outputpath, "tmva1.root"), num_inputs=x_train[bdtvars].shape[1])
        print(f"Model saved to {os.path.join(outputpath, 'bdt1.json')}")
        print(f"Model saved to {os.path.join(outputpath, 'tmva1.root')}")
    else:
        print(f"--save-model flag not set, skipping model saving...")

    feature_importances = pd.DataFrame(bdt.feature_importances_,
                                       index = bdtvars,
                                       columns=['importance']).sort_values('importance',ascending=False)
    
    print("\n{30*'-'}")
    print(f"Feature importances")
    print(feature_importances)
    print(f"{30*'-'}\n")

    #############################
    # RESPONSE PLOTS
    #############################
    if args.plot_results:
        for df in x.values():
            df['XGB'] = bdt.predict_proba(df)[:, 1]

        print("PLOTTING")
        plot_bdt_response(x, "BDT1 response")
        plt.savefig(os.path.join(outputpath, "bdt1-response.pdf"))
        print(f'BDT1 response curve saved to {os.path.join(outputpath, "bdt1-response.pdf")}')
        plt.close()

        plot_roc(bdt, x_test[bdtvars], y_test, w_test)
        plt.savefig(os.path.join(outputpath, "bdt1-roc.pdf"))
        print(f'ROC saved to {os.path.join(outputpath, "bdt1-roc.pdf")}')
        plt.close()

        plot_punzi_significance(x, np.linspace(0, 1, 20), 5)
        plt.savefig(os.path.join(outputpath, "bdt1-punzi-significance.pdf"))
        print(f'Punzi significance plot saved to {os.path.join(outputpath, "bdt1-punzi-significance.pdf")}')
        plt.close()

        plot_significance(x, [0.2, 0.6, 0.8, 0.9, 0.99], np.logspace(-9, -4, 100))
        plt.savefig(os.path.join(outputpath, "bdt1-significance.pdf"))
        print(f'Significance plot saved to {os.path.join(outputpath, "bdt1-significance.pdf")}')
        plt.close()

        # responsevars is expected to be a single element list
        plot_feature(x, 0.6, responsevars)
        plt.savefig(os.path.join(outputpath, "bdt1-feature.pdf"))
        print(f'Feature plot saved to {os.path.join(outputpath, "bdt1-feature.pdf")}')
        plt.close()

    else:
        print(f"--plot-results flag not set, skipping plotting...")
    
    end = time()
    exec_time = end - start
    hours, rem = divmod(exec_time, 3600)
    minutes, sec = divmod(exec_time, 60)
    print(f"{30*'-'}")
    print(f"Execution time in H:M:S = {int(hours):02}:{int(minutes):02}:{sec:.3f}")
    print(f"{30*'-'}")
