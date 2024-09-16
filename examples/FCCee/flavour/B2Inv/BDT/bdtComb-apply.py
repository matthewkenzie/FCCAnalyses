# bdtComb-apply.py   TEMPORARY
# Train BDTCOMB using stage1 files
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
from efficiency_finder import efficiency_calc

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
            ax.hist(x[sample]['XGB'], bins=50, density=True, histtype='stepfilled', color='gold', alpha=0.7, label=cfg.titles[sample])
        else:
            ax.hist(x[sample]['XGB'], bins=50, density=True, histtype='step', label=cfg.titles[sample])
   
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

def plot_punzi_significance(x, cuts, sigma, eff_before_bdt):
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
                count = 6e12*cfg.branching_fractions[sample][0]*eff_before_bdt[sample]*after/before
                temp_B += count
        
        B = np.append(B, temp_B)

    fig, ax = plt.subplots()
    punzi = np.divide(epsilon_s, np.sqrt(B) + sigma/2)
    ax.plot(cuts, punzi)
    ax.axvline(cuts[np.argmax(punzi)], color='black', 
               linestyle='--', label = f'Optimal cut ({cuts[np.argmax(punzi)]:.3f})')
    ax.set_xlabel('BDT1 cut value')
    ax.set_ylabel(r'$\frac{\epsilon_s}{\sqrt{B} + \sigma/2},\ \sigma = $'+f'{sigma}')
    ax.set_title('Punzi significance for BDTCOMB')
    ax.legend(loc='best')
    fig.tight_layout()

# Plots shaded area between S/sqrt(S+B) assuming the signal error is sqrt(S) and the background error is sqrt(B)
def plot_significance(x, bdtvals, branching_fracs, eff_before_bdt):
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    for bdt in bdtvals:
        S = np.array([])
        B = 0
        for sample in x:
            if sample in cfg.sample_allocations['signal']:
                before = len(x[sample])
                after  = len(x[sample].query(f"XGB > {bdt}"))
                temp_S = 6e12*cfg.branching_fractions['p8_ee_Zbb_ecm91'][0]*2*cfg.prod_frac['Bs']*eff_before_bdt[sample]*after/before*branching_fracs
                S = np.append(S, temp_S)
            else:
                before = len(x[sample])
                after  = len(x[sample].query(f"XGB > {bdt}"))
                count = 6e12*cfg.branching_fractions[sample][0]*eff_before_bdt[sample]*after/before
                B += count
    
        significance = np.divide(S, np.sqrt(S+B+1e-10))
        ax.plot(branching_fracs, significance, label=f'BDT1 $>$ {bdt:.3f}')
    
    ax.axvline(1e-6, color='black', linestyle='--')
    ax.axhline(5,    color='black', linestyle='--')
    ax.set_xlabel(r'$\mathcal{B}(B_s\to\nu\bar{\nu})$')
    ax.set_ylabel(r'$\frac{S}{\sqrt{S+B}}$')
    ax.set_ylim(0, 10)
    ax.legend(loc='best')
    ax.set_title('BDTCOMB significance (expected "signal to noise" ratio)')
    fig.tight_layout()

def plot_feature(x, cut, responsevars, eff_before_bdt, placeholder_bf):
    fig, ax = plt.subplots()
    for sample in x:
        if sample in cfg.sample_allocations['signal']:
            # Weight per bin = (Number before bdt)*(efficiency of cut) / (Length of array after bdt) = (Number before bdt) / (Length of array before bdt)
            N_before = 2*6e12*cfg.branching_fractions['p8_ee_Zbb_ecm91'][0]*cfg.prod_frac['Bs']*eff[sample]*placeholder_bf
            ax.hist(x[sample].query(f"XGB > {cut}")[responsevars], 
                    bins=50, 
                    weights=np.ones(x[sample].query(f"XGB > {cut}").shape[0])*N_before/x[sample].shape[0], 
                    histtype='stepfilled', 
                    color='gold', 
                    alpha=0.7, 
                    label=cfg.titles[sample])
        else:
            N_before = 6e12*cfg.branching_fractions[sample][0]*eff[sample]
            ax.hist(x[sample].query(f"XGB > {cut}")[responsevars], 
                    bins=50, 
                    weights=np.ones(x[sample].query(f"XGB > {cut}").shape[0])*N_before/x[sample].shape[0], 
                    histtype='step', 
                    label=cfg.titles[sample])
    
    ax.set_yscale('log')
    ax.set_xlabel(f'{responsevars}')
    ax.set_ylabel("Counts")
    ax.legend(loc='best')
    ax.set_title(f"{responsevars} with BDTCOMB $>$ {cut} and signal bf = {placeholder_bf:.1e}")
    fig.tight_layout()

#############################
# MAIN
#############################
if __name__ == "__main__":
    
    # Load configuration
    plt.style.use(os.path.abspath(os.path.join(cfg.FCCAnalysesPath, 'fcc.mplstyle')))
    inputpath    = check_inputpath(cfg.bdtComb_opts['inputPath'])
    outputpath   = set_outputpath(cfg.bdtComb_opts['outputPath'])
    yamlpath     = check_inputpath(cfg.fccana_opts['yamlPath'])
    bdtvars      = vars_fromyaml(yamlpath, cfg.bdtComb_opts['mvaBranchList'])
    # Variables not used by the bdt which you want to plot
    responsevars = ["EVT_hemisEmin_Emiss"]

    # Efficiencies of pre-selection cuts and branching fractions
    bfs = {sample: cfg.branching_fractions[sample][0] for sample in cfg.samples}
    eff = {sample: cfg.efficiencies[cfg.bdtComb_opts['efficiencyKey']][sample][0] for sample in cfg.samples}  
    
    print(f"----> INFO: Efficiencies loaded from config.py using key `{cfg.bdtComb_opts['efficiencyKey']}`")
    print(f"----> INFO: Using {cfg.bdtComb_opts['mvaBranchList']} from")
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
    #if (args.nchunks is not None):
    #    if (len(args.nchunks) == 1):
    #        files = {sample: glob(paths[sample])[:int(args.nchunks[0])] for sample in cfg.samples}
    #    elif (len(args.nchunks) == len(cfg.samples)):
    #        files = {sample: glob(paths[sample])[:int(args.nchunks[i])] for i, sample in enumerate(cfg.samples)}
    #    warn_about_slowGridSearch = 0
    #else:
    #    print(f"----> INFO: --nchunks is None or invalid, skipping...")
    #    files = {sample: glob(paths[sample]) for sample in cfg.samples}
    #    warn_about_slowGridSearch = 1
    
    files = {sample: glob(path[sample])[5:] for sample in cfg.samples}

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
    x_train = pd.concat([x[sample].sample(frac=0.8, random_state=rand_state) for sample in cfg.samples], copy=True, ignore_index=True)
    y_train = pd.concat([y[sample].sample(frac=0.8, random_state=rand_state) for sample in cfg.samples], copy=True, ignore_index=True)
    # Normalise weights by dividing by the total number of events of each type
    w_train = pd.concat([w[sample].sample(frac=0.8, random_state=rand_state)/(0.8*len(x[sample])) for sample in cfg.samples], copy=True, ignore_index=True)
    
    # Create test dataframes by sampling the indices not used in x/y/w_train
    x_test = pd.concat([x[sample].drop(x[sample].sample(frac=0.8, random_state=rand_state).index) for sample in cfg.samples], copy=True, ignore_index=True)
    y_test = pd.concat([y[sample].drop(y[sample].sample(frac=0.8, random_state=rand_state).index) for sample in cfg.samples], copy=True, ignore_index=True)
    # Normalise weights by dividing by the total number of events of each type
    w_test = pd.concat([w[sample].drop(w[sample].sample(frac=0.8, random_state=rand_state).index)/((1-0.8)*len(w[sample])) for sample in cfg.samples], copy=True, ignore_index=True)
    
    #############################
    # LOAD BDT
    #############################
    # Define BDT
    bdt = xgb.XGBClassifier(early_stopping_rounds=10, eval_metric="auc", n_jobs=-1, objective='binary:logistic')
    bdt.load_model(cfg.bdtComb_opts['jsonPath'])

    #############################
    # VALIDATION
    #############################
    data_dmatrix = xgb.DMatrix(data=x_test[bdtvars].to_numpy(), label=y_test.to_numpy(), weight=w_test.to_numpy())
    xgb_cv = xgb.cv(dtrain=data_dmatrix, params=cv_dict, nfold=5, num_boost_round=50, early_stopping_rounds=10, metrics="auc", as_pandas=True, seed=123)
    print('\n', xgb_cv.head())
    print(f'...')
    print(xgb_cv.tail())
    print(f"{30*'-'}\n")

    #############################
    # RESPONSE PLOTS
    #############################
    for df in x.values():
        df['XGB'] = bdt.predict_proba(df[bdtvars])[:, 1]
    
    prefix = 'trained-'

    plot_bdt_response(x, "BDTCOMB response")
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

    plot_punzi_significance(x, np.linspace(0, 1, 20), 5, eff)
    punzipath = os.path.join(outputpath, f"{prefix}punzi.pdf")
    plt.savefig(punzipath)
    print(f'Punzi significance plot saved to')
    print(f"{15*' '}{punzipath}")
    plt.close()

    plot_significance(x, [0.2, 0.6, 0.8, 0.9, 0.99], np.logspace(-9, -4, 100), eff)
    significancepath = os.path.join(outputpath, f"{prefix}significance.pdf")
    plt.savefig(significancepath)
    print(f'Significance plot saved to')
    print(f"{15*' '}{significancepath}")
    plt.close()

    for feature in responsevars:
        for i, _bf in enumerate([1e-5, 1e-6, 1e-7]):
            plot_feature(x, 0.9, feature, eff, _bf)
            figpath = os.path.join(outputpath, f"{prefix}{feature}-withcut-bf{i}.pdf")
            plt.savefig(figpath)
            print(f'Feature plot with bdt cut saved to')
            print(f"{15*' '}{figpath}")
            plt.close()

            plot_feature(x, 0, feature, eff, _bf)
            figpath = os.path.join(outputpath, f"{prefix}{feature}-nocut{i}.pdf")
            plt.savefig(figpath)
            print(f'Feature plot without cuts saved to')
            print(f"{15*' '}{figpath}")
            plt.close()


    for cut in [0.5, 0.7, 0.9]:
        for sample in cfg.samples:
            mode, error = efficiency_calc(x[sample].shape[0], x[sample].query(f'XGB > {cut}').shape[0])

            
