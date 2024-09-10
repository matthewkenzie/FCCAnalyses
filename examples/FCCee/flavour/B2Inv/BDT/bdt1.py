# bdt1.py
# Train BDT1 using stage1 files
import xgboost as xgb # Has to be imported first to avoid conflicts with PyROOT

import sys
# Path to config.py and variable_plotter.py
sys.path.append("/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv/")

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

from time import time
from datetime import timedelta
from glob import glob
from yaml import safe_load, YAMLError, dump
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_curve, auc

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
    ax.set_ylim([1e-3, 1e2])
    ax.set_yscale('log')
    for sample in x:
        if sample in cfg.sample_allocations['signal']:
            ax.hist(x[sample]['XGB'], bins=100, density=True, histtype='stepfilled', color='gold', alpha=0.7, label=cfg.titles[sample])
        else:
            ax.hist(x[sample]['XGB'], bins=100, density=True, histtype='step', label=cfg.titles[sample])
   
    ax.set_xlabel("BDT Response")
    ax.set_ylabel("Normalised counts")
    #ax.set_xlim((0, 1))
    ax.legend(loc='upper center')
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
    ax.set_ylabel(r'$\frac{\epsilon_s}{\sqrt{B} + \sigma/2},\ \sigma = $'+f'{sigma}')
    ax.set_title('Punzi significance for BDT1')
    ax.legend(loc='best')
    fig.tight_layout()

# Plots shaded area between S/sqrt(S+B) assuming the signal error is sqrt(S) and the background error is sqrt(B)
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
        ax.plot(branching_fracs, significance, label=f'BDT1 $>$ {bdt:.3f}')
    
    ax.axvline(1e-6, color='black', linestyle='--')
    ax.set_xlabel(r'$\mathcal{B}(B_s\to\nu\bar{\nu})$')
    ax.set_ylabel(r'$\frac{S}{\sqrt{S+B}}$')
    ax.set_ylim(0, 10)
    ax.legend(loc='best')
    ax.set_title('BDT1 significance (expected "signal to noise" ratio)')
    fig.tight_layout()

def plot_feature(x, cut, responsevars):
    fig, ax = plt.subplots()
    for sample in x:
        if sample in cfg.sample_allocations['signal']:
            ax.hist(x[sample].query(f"XGB > {cut}")[responsevars], bins=100, density=True, histtype='stepfilled', color='gold', alpha=0.7, label=cfg.titles[sample])
        else:
            ax.hist(x[sample].query(f"XGB > {cut}")[responsevars], bins=100, density=True, histtype='step', label=cfg.titles[sample])
    
    ax.set_xlabel(f'{responsevars}')
    ax.set_ylabel("Density")
    ax.legend(loc='best')
    ax.set_title(f"{responsevars} with BDT1 $>$ {cut}")
    fig.tight_layout()

#############################
# MAIN
#############################
if __name__ == "__main__":

    from argparse import ArgumentParser
    
    parser = ArgumentParser(description='Trains BDT1 using bdt1_opts from config.py')
    method = parser.add_argument("--method",           required=True, choices=['gridsearch', 'fixed-hyperparams'])
    nchunk = parser.add_argument("--nchunks",          default=None,  nargs='*')
    trainf = parser.add_argument("--train-frac",       default=0.75,  type=float)
    savehp = parser.add_argument("--save-hyperparams", default=False, action='store_true')
    loadhp = parser.add_argument("--load-hyperparams", default=False, action='store_true')
    savemo = parser.add_argument("--save-model",       default=False, action='store_true')
    plotre = parser.add_argument("--plot-results",     default=False, action='store_true')

    # Modify the help message here
    method.help = "Method to train the BDT"
    nchunk.help = "Number of chunks to process, default = None (all are processed)"
    trainf.help = "Fraction of data to use for training, default = 0.75"
    savehp.help = "If using `gridsearch` method, save the optimum hyperparameters to `best_params_bdt1.yaml`, default = False"
    loadhp.help = "If using `fixed-hyperparams` method, use `best_params_bdt1.yaml`, default = False"
    savemo.help = "Save model to `bdt1.json` and `tmva1.root`, default = False"
    plotre.help = "Plot and save BDT responses, default = False"

    args = parser.parse_args()
    
    #############################
    # PREPROCESSING
    #############################
    start = time()
    print(f"{30*'-'}")
    print(f"BDT1 TRAINING")
    print(f"{30*'-'}\n")
    print("Initialising...")

    # Load configuration
    plt.style.use(os.path.abspath(os.path.join(cfg.FCCAnalysesPath, 'fcc.mplstyle')))
    inputpath    = check_inputpath(cfg.bdt1_opts['inputpath'])
    outputpath   = set_outputpath(cfg.bdt1_opts['outputpath'])
    yamlpath     = check_inputpath(cfg.fccana_opts['yamlPath'])
    bdtvars      = vars_fromyaml(yamlpath, cfg.bdt1_opts['mvaBranchList'])
    # Variables not used by the bdt which you want to plot
    responsevars = ["EVT_hemisEmin_Emiss"]

    # Efficiencies of pre-selection cuts and branching fractions
    bfs = {sample: cfg.branching_fractions[sample][0] for sample in cfg.samples}
    eff = {sample: cfg.efficiencies['presel'][sample] for sample in cfg.samples}  
    
    print(f"----> INFO: Efficiencies loaded")
    print(f"----> INFO: Using {cfg.bdt1_opts['mvaBranchList']} from")
    print(f"{15*' '}{yamlpath}")
    print(f"----> INFO: Loading files from")
    print(f"{15*' '}{inputpath}")
    print(f"----> INFO: Output will be saved to")
    print(f"{15*' '}{outputpath}")
    
    paths = {sample: os.path.join(inputpath, sample, "*.root") for sample in cfg.samples}
    
    # Depending on the value passed to --nchunks:
    # Single int: use this number of chunks for every sample
    # len(cfg.samples) ints: use corresponding number
    # None or mismatched length or other: use all chunks
    if (args.nchunks is not None):
        if (len(args.nchunks) == 1):
            files = {sample: glob(paths[sample])[:int(args.nchunks[0])] for sample in cfg.samples}
        elif (len(args.nchunks) == len(cfg.samples)):
            files = {sample: glob(paths[sample])[:int(args.nchunks[i])] for i, sample in enumerate(cfg.samples)}
        warn_about_slowGridSearch = 0
    else:
        print(f"----> INFO: --nchunks is None or invalid, skipping...")
        files = {sample: glob(paths[sample]) for sample in cfg.samples}
        warn_about_slowGridSearch = 1
    
    x = {sample: None for sample in cfg.samples}
    y = {sample: None for sample in cfg.samples}
    w = {sample: None for sample in cfg.samples}
    
    for sample in cfg.samples:
        # Weigh each sample by the number of expected events of that sample
        weight = 6e12*eff[sample]*bfs[sample]
        if sample in cfg.sample_allocations['signal']:
            weight *= 2*bfs['p8_ee_Zbb_ecm91']*cfg.prod_frac['Bs']
            x[sample], y[sample], w[sample] = load_data(files[sample], 'signal', weight, bdtvars+responsevars)
        else: 
            x[sample], y[sample], w[sample] = load_data(files[sample], 'background', weight, bdtvars+responsevars)
    
    for sample in cfg.samples:
        if (sample in cfg.sample_allocations['signal']) and (np.any(y[sample].to_numpy() == 0)):
            raise ValueError
        elif (sample not in cfg.sample_allocations['signal']) and (np.any(y[sample].to_numpy() == 1)):
            raise ValueError
    
    rand_state = 7 # For reproducibility
    x_train = pd.concat([x[sample].sample(frac=args.train_frac, random_state=rand_state) for sample in cfg.samples], copy=True, ignore_index=True)
    y_train = pd.concat([y[sample].sample(frac=args.train_frac, random_state=rand_state) for sample in cfg.samples], copy=True, ignore_index=True)
    # Normalise weights by dividing by the total number of events of each type
    w_train = pd.concat([w[sample].sample(frac=args.train_frac, random_state=rand_state)/(args.train_frac*len(x[sample])) for sample in cfg.samples], copy=True, ignore_index=True)
    
    # Create test dataframes by sampling the indices not used in x/y/w_train
    x_test = pd.concat([x[sample].drop(x[sample].sample(frac=args.train_frac, random_state=rand_state).index) for sample in cfg.samples], copy=True, ignore_index=True)
    y_test = pd.concat([y[sample].drop(y[sample].sample(frac=args.train_frac, random_state=rand_state).index) for sample in cfg.samples], copy=True, ignore_index=True)
    # Normalise weights by dividing by the total number of events of each type
    w_test = pd.concat([w[sample].drop(w[sample].sample(frac=args.train_frac, random_state=rand_state).index)/((1-args.train_frac)*len(w[sample])) for sample in cfg.samples], copy=True, ignore_index=True)
    
    print(f"\n{30*'-'}\n")
    for sample in cfg.samples:
        print(f"Number of {sample:31} events = {x[sample].shape[0]:>8} using {len(files[sample]):>4} chunks")
    print("\n----> INFO: Preprocessing done")
    print(f"{15*' '}Using {len(x_train):>8} events to train ({100*args.train_frac:.1f}% of total)")
    print(f"{15*' '}Using {len(x_test):>8} events to  test ({100*(1-args.train_frac):.1f}% of total)")
    print(f"\n{30*'-'}\n")
    
    #############################
    # TRAINING
    #############################
    # Define BDT
    bdt = xgb.XGBClassifier(early_stopping_rounds=10, eval_metric="auc", n_jobs=-1, objective='binary:logistic')
    print(f"BDT OUTPUT")
    # Tuning hyperparameters
    if args.method == 'gridsearch':
        param_grid = {
            "n_estimators": [100, 150, 200],
            "learning_rate": [0.1, 0.3],
            "max_depth": [3, 5, 7],
            "subsample": [0.7, 1.0],
            "colsample_bytree": [0.8, 1.0],
            "gamma": [0, 0.1, 0.2],
            "min_child_weight": [1, 5],
        }
        if warn_about_slowGridSearch:
            print(f"----> WARNING: `gridsearch` method is used without specifying --nchunks, hyperparameter tuning may take a long time")
        # Use GridSearchCV to find the best hyperparameters
        # Need to convert to numpy to save to ROOT TMVA file
        grid_search = GridSearchCV(estimator=bdt, param_grid=param_grid, cv=4, scoring="roc_auc", verbose=1, n_jobs=-1)
        grid_search.fit(x_train[bdtvars].to_numpy(), y_train.to_numpy(), sample_weight=w_train.to_numpy(),
                        eval_set = [(x_test[bdtvars].to_numpy(), y_test.to_numpy())], sample_weight_eval_set = [w_test.to_numpy()], verbose=False)
        
        print(f"Best cross validation score = {grid_search.best_score_:.5f}")
        print(f"Best params = {grid_search.best_params_}\n")

        bdt = grid_search.best_estimator_
        cv_dict = grid_search.best_params_

        ### Save optimum combination of hyperparameters
        if args.save_hyperparams:
            with open(os.path.join(outputpath, 'best_params_bdt1.yaml'), 'w') as outfile:
                dump(cv_dict, outfile)
            print(f"----> INFO: Optimum hyperparameters saved to")
            print(f"{15*' '}{os.path.join(outputpath, 'best_params_bdt1.yaml')}")
        else:
            print(f"----> INFO: --save-hyperparams not set, skipping...")
    
    # Using fixed hyperparameters
    elif args.method == 'fixed-hyperparams':
        
        ### Load hyperparameters
        if args.load_hyperparams:
            with open(os.path.join(outputpath, 'best_params_bdt1.yaml'), 'r') as stream:
                config_dict = safe_load(stream)
            print(f"----> INFO: Loading hyperparameters from")
            print(f"{15*' '}{os.path.join(outputpath, 'best_params_bdt1.yaml')}")
        else:
            config_dict = {'gamma': 0.2, 'learning_rate': 0.1, 'n_estimators': 200, 'subsample': 1.0, 'max_depth': 4}
            config_dict = {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 7, "subsample": 1.0, "colsample_bytree": 1.0, "gamma": 0.2, "min_child_weight": 1}
            print(f'----> INFO: --load-hyperparams not set, using default values')

        bdt.set_params(**config_dict)
        bdt.fit(x_train[bdtvars].to_numpy(), y_train.to_numpy(), sample_weight=w_train.to_numpy(), 
                eval_set = [(x_test[bdtvars].to_numpy(), y_test.to_numpy())], sample_weight_eval_set=[w_test.to_numpy()], verbose=100)
        cv_dict = config_dict

    # xgb.cv does not use n_estimators, num_boost_round=50 instead
    cv_dict.pop('n_estimators', None)
    
    #############################
    # VALIDATION
    #############################
    data_dmatrix = xgb.DMatrix(data=x_train[bdtvars].to_numpy(), label=y_train.to_numpy(), weight=w_train.to_numpy())
    xgb_cv = xgb.cv(dtrain=data_dmatrix, params=cv_dict, nfold=5, num_boost_round=50, early_stopping_rounds=10, metrics="auc", as_pandas=True, seed=123)
    print('\n', xgb_cv.head())
    print(f'...')
    print(xgb_cv.tail())
    print(f"{30*'-'}\n")

    #############################
    # SAVING MODEL
    #############################
    print(f"SAVING")
    if args.save_model: 
        bdt.save_model(os.path.join(outputpath, "bdt1.json"))
        ROOT.TMVA.Experimental.SaveXGBoost(bdt, cfg.bdt1_opts['mvaRBDTName'], os.path.join(outputpath, "tmva1.root"), num_inputs=len(bdtvars))
        print(f"----> INFO: Model saved to")
        print(f"{15*' '}1. {os.path.join(outputpath, 'bdt1.json')}")
        print(f"{15*' '}2. {os.path.join(outputpath, 'tmva1.root')}")

    else:
        print(f"----> INFO: --save-model flag not set, skipping model saving...")

    feature_importances = pd.DataFrame(bdt.feature_importances_,
                                       index = bdtvars,
                                       columns=['importance']).sort_values('importance',ascending=False)
    
    print(f"\n{30*'-'}\n")
    print(f"FEATURE IMPORTANCES")
    print(feature_importances)
    print(f"\n{30*'-'}\n")
    print("PLOTTING")

    #############################
    # RESPONSE PLOTS
    #############################
    if args.plot_results:
        for df in x.values():
            df['XGB'] = bdt.predict_proba(df[bdtvars])[:, 1]
        
        if args.method == 'gridsearch':
            prefix = 'bdt1-grid-'
        else:
            prefix = 'bdt1-'

        plot_bdt_response(x, "BDT1 response")
        responsepath = os.path.join(outputpath, f"{prefix}response.pdf")
        plt.savefig(responsepath)
        print(f'BDT1 response curve saved to')
        print(f"{15*' '}{responsepath}")
        plt.close()

        plot_roc(bdt, x_test[bdtvars], y_test, w_test)
        rocpath = os.path.join(outputpath, f"{prefix}roc.pdf")
        plt.savefig(rocpath)
        print(f'ROC saved to')
        print(f"{15*' '}{rocpath}")
        plt.close()

        plot_punzi_significance(x, np.linspace(0, 1, 20), 5)
        punzipath = os.path.join(outputpath, f"{prefix}punzi.pdf")
        plt.savefig(punzipath)
        print(f'Punzi significance plot saved to')
        print(f"{15*' '}{punzipath}")
        plt.close()

        plot_significance(x, [0.2, 0.6, 0.8, 0.9, 0.99], np.logspace(-9, -4, 100))
        significancepath = os.path.join(outputpath, f"{prefix}significance.pdf")
        plt.savefig(significancepath)
        print(f'Significance plot saved to')
        print(f"{15*' '}{significancepath}")
        plt.close()

        for feature in responsevars:
            plot_feature(x, 0.6, feature)
            figpath = os.path.join(outputpath, f"{prefix}{feature}-withcut.pdf")
            plt.savefig(figpath)
            print(f'Feature plot with bdt cut saved to')
            print(f"{15*' '}{figpath}")
            plt.close()

            plot_feature(x, 0, feature)
            figpath = os.path.join(outputpath, f"{prefix}{feature}-nocut.pdf")
            plt.savefig(figpath)
            print(f'Feature plot without cuts saved to')
            print(f"{15*' '}{figpath}")
            plt.close()

    else:
        print(f"---->INFO: --plot-results flag not set, skipping plotting...")
    
    end = time()
    print(f"\n{30*'-'}")
    print(f"Execution time  = {timedelta(seconds=end-start)}")
    print(f"{30*'-'}")
