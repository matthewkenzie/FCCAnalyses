# BDT1 using stage1 files
import xgboost as xgb # Has to be imported first to avoid conflicts with PyROOT

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
plt.rcParams['text.usetex'] = True
outpath="/r01/lhcb/rrm42/fcc/bdt1out/"
inpath="/r01/lhcb/rrm42/fcc/stage1_postBDT/"
yamlpath = "/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv/bdt.yaml"

# Return list of variables to use in the bdt as a python list
def vars_fromyaml(path, bdtlist):
    with open(path) as stream:
        try:
            file = safe_load(stream)
            bdtvars = file[bdtlist]
        except YAMLError as exc:
            print(exc)

    return bdtvars
    
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

    w = pd.DataFrame(eff*np.ones(x.shape[0]), columns=['weights'])

    return df, x, y, w

#############################
# PLOTTERS
#############################
def plot_bdt_response():
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    _, bins, _ = ax.hist(sg_x['XGB'], bins=100, density=True, histtype='stepfilled', color = 'gold', label=r'$B_s^0 \to \nu\bar{\nu}$')
    ax.hist(bb_x['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to b\bar{b}$')
    ax.hist(cc_x['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to c\bar{c}$')
    ax.hist(ss_x['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to s\bar{s}$')
    ax.hist(ud_x['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to ud$')
    
    ax.set_xlabel("BDT Response")
    ax.set_ylabel("Normalised counts")
    #ax.set_xlim((0, 1))
    ax.legend(loc='best')
    ax.set_title('BDT1 applied to stage1')
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

def plot_significance(bdt, x_test, y_test, w_test, n_sig, n_bkg):
    y_score = bdt.predict_proba(x_test)[:,1]
    fpr, tpr, thresholds = roc_curve(y_test, y_score, sample_weight=w_test)
    S = n_sig*tpr
    B = n_bkg*fpr
    epsilon = 1e-10
    metric = S/np.sqrt(S+B+epsilon)

    plt.plot(thresholds, metric, label=f'XGB')
    plt.xlabel('$P_{XGB}$ cut value')
    plt.ylabel('Signal significance: $\\frac{S}{\\sqrt{S+B}}$')
    plt.xlim(0, 1)

    optimal_cut = thresholds[np.argmax(metric)]
    plt.axvline(optimal_cut, color='black', linestyle='--', label = f'Optimal cut ({optimal_cut:.3f})')
    plt.legend(loc='best')
    plt.tight_layout()

if __name__ == "__main__":
    start = time()
    print(f"\n{30*'-'}\n")
    print("Initialising...\n")

    # Efficiencies of pre-selection cuts + branching fraction
    sig_bf = cfg.branching_fractions['p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu'][0]
    bb_bf  = cfg.branching_fractions['p8_ee_Zbb_ecm91'][0]
    cc_bf  = cfg.branching_fractions['p8_ee_Zcc_ecm91'][0]
    ss_bf  = cfg.branching_fractions['p8_ee_Zss_ecm91'][0]
    ud_bf  = cfg.branching_fractions['p8_ee_Zud_ecm91'][0]
    bb_bf /= (bb_bf + cc_bf + ss_bf + ud_bf)
    cc_bf /= (bb_bf + cc_bf + ss_bf + ud_bf)
    ss_bf /= (bb_bf + cc_bf + ss_bf + ud_bf)
    ud_bf /= (bb_bf + cc_bf + ss_bf + ud_bf)
    
    sig_eff = cfg.efficiencies['post_bdt1_cut']['p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu']
    bb_eff  = cfg.efficiencies['post_bdt1_cut']['p8_ee_Zbb_ecm91']
    cc_eff  = cfg.efficiencies['post_bdt1_cut']['p8_ee_Zcc_ecm91']
    ss_eff  = cfg.efficiencies['post_bdt1_cut']['p8_ee_Zss_ecm91']
    ud_eff  = cfg.efficiencies['post_bdt1_cut']['p8_ee_Zud_ecm91']

    sig_eff *= sig_bf
    bb_eff  *= bb_bf
    cc_eff  *= cc_bf
    ss_eff  *= ss_bf
    ud_eff  *= ud_bf
    
    print("Efficiencies loaded")
    path_to_yaml = yamlpath
    whichvars = 'bdt1-training-vars'
    bdtvars = vars_fromyaml(path_to_yaml, whichvars)
    print(f"Using {whichvars} from {path_to_yaml}\n")

    sigpath = os.path.join(inpath, cfg.samples[0], "*.root")
    bbpath  = os.path.join(inpath, cfg.samples[1], "*.root")
    ccpath  = os.path.join(inpath, cfg.samples[2], "*.root")
    sspath  = os.path.join(inpath, cfg.samples[3], "*.root")
    udpath  = os.path.join(inpath, cfg.samples[4], "*.root")
    
    sigfiles = glob(sigpath)[:10]
    bbfiles  = glob(bbpath)
    ccfiles  = glob(ccpath)
    ssfiles  = glob(sspath)
    udfiles  = glob(udpath)
    
    #print(f"Using {sigfiles} for the signal")
    #print(f"Using {bbfiles}\n, {ccfiles}\n, {ssfiles}\n, {udfiles}\n for the background\n\n")
    sg_df, sg_x, sg_y, sg_w = load_data(sigfiles, 'signal',    sig_eff, bdtvars)
    bb_df, bb_x, bb_y, bb_w = load_data(bbfiles,  'background', bb_eff, bdtvars)
    cc_df, cc_x, cc_y, cc_w = load_data(ccfiles,  'background', cc_eff, bdtvars)
    ss_df, ss_x, ss_y, ss_w = load_data(ssfiles,  'background', ss_eff, bdtvars)
    ud_df, ud_x, ud_y, ud_w = load_data(udfiles,  'background', ud_eff, bdtvars)

    tot_x = pd.concat([sg_x, bb_x, cc_x, ss_x, ud_x], copy=True, ignore_index=True)
    tot_y = pd.concat([sg_y, bb_y, cc_y, ss_y, ud_y], copy=True, ignore_index=True)
    tot_w = pd.concat([sg_w, bb_w, cc_w, ss_w, ud_w], copy=True, ignore_index=True)
    print(f"{30*'-'}")
    print(f"Number of signal events = {sg_x.shape[0]}")
    print(f"Number of bb events = {bb_x.shape[0]}")
    print(f"Number of cc events = {cc_x.shape[0]}")
    print(f"Number of ss events = {ss_x.shape[0]}")
    print(f"Number of ud events = {ud_x.shape[0]}")

    x_train, x_test, y_train, y_test, w_train, w_test = train_test_split(tot_x, tot_y, tot_w, test_size=0.5, random_state=27)

    #sc = StandardScaler()
    #sc.set_output(transform = 'pandas')
    #sc.fit(x_train)
    #x_train = sc.transform(x_train)

    #sc.fit(x_test)
    #x_test = sc.transform(x_test)
    
    #sc.fit(tot_forsc)
    #for x in [sg_x, bb_x, cc_x, ss_x, ud_x]:
    #    x = sc.transform(x)
    
    print(f"{30*'-'}")
    print("Preprocessing done")
    print(f"Using {len(x_train)} events to train")
    print(f"Using {len(x_test)} events to test")
    print(f"{30*'-'}")
    
    # Define BDT
    config_dict = {
        "n_estimators": 200,
        "learning_rate": 0.3,
        "max_depth": 3,
        "subsample": 1.0,
    }
    
    param_grid = {
        "n_estimators": [50, 200, 400],
        "learning_rate": [0.01, 0.1, 0.3],
        "max_depth": [3, 4],
        "subsample": [0.5, 0.8, 1.0],
        "gamma": [0, 0.1]
    }
    bdt = xgb.XGBClassifier()
    
    #grid_search = GridSearchCV(estimator=bdt, param_grid=param_grid, cv=4, scoring="roc_auc", verbose=True, n_jobs=-1)
    #grid_search.fit(x_train.to_numpy(), y_train.to_numpy(), sample_weight=w_train.to_numpy())
    
    #print(f"Best cross validation score = {grid_search.best_score_}")
    #print(f"Best params = {grid_search.best_params_}")

    #bdt.set_params(**grid_search.best_params_)
    bdt.set_params(**config_dict)
    bdt.fit(x_train.to_numpy(), y_train.to_numpy(), sample_weight=w_train.to_numpy())
    data_dmatrix = xgb.DMatrix(data=x_train.to_numpy(), label=y_train.to_numpy(), weight=w_train.to_numpy())
    
    xgb_cv = xgb.cv(dtrain=data_dmatrix, params=config_dict, nfold=4, num_boost_round=50, early_stopping_rounds=10, metrics="auc", as_pandas=True, seed=123)
    print(f"{30*'-'}")
    print("BDT OUTPUT")
    print(xgb_cv.head())
    
    # Save model to output file
    bdt.save_model(os.path.join(outpath, "bdt1_test.json"))
    ROOT.TMVA.Experimental.SaveXGBoost(bdt, "bdt", os.path.join(outpath, "tmva1_test.root"), num_inputs=x_train.shape[1])
    print(f"Model saved to {os.path.join(outpath, 'bdt1.json')}")
    print(f"Model saved to {os.path.join(outpath, 'tmva1.root')}")
    #print("Model already saved, skipping...")

    feature_importances = pd.DataFrame(bdt.feature_importances_,
                                       index = bdtvars,
                                       columns=['importance']).sort_values('importance',ascending=False)
    
    print("\nFeature importances")
    print(feature_importances)
    print(f"{30*'-'}\n")

    # bdt response
    for df in [sg_x, bb_x, cc_x, ss_x, ud_x]:
        df['XGB'] = bdt.predict_proba(df)[:, 1]
        after = df.query('XGB > 0.5').shape[0]
        print(f'{after}')

    # plotting
    print(f"{30*'-'}")
    print("PLOTTING")
    plot_bdt_response()
    plt.savefig(os.path.join(outpath, "bdt1-response-test.pdf"))
    print(f'BDT1 response curve saved to {os.path.join(outpath, "bdt1-response-test.pdf")}')
    plt.close()

    plot_roc(bdt, x_test, y_test, w_test)
    plt.savefig(os.path.join(outpath, "roc-test.pdf"))
    print(f'ROC saved to {os.path.join(outpath, "roc-test.pdf")}')
    plt.close()

    #plot_significance(bdt, x_test, y_test, w_test, 0.25*sg_x.shape[0], 0.25*(tot_x.shape[0]-sg_x.shape[0]))
    #plt.savefig(os.path.join(outpath, "significance.pdf"))
    #print(f'Significance plot saved to {os.path.join(outpath, "significance.pdf")}')
    #plt.close()

    end = time()
    exec_time = end - start
    hours, rem = divmod(exec_time, 3600)
    minutes, sec = divmod(exec_time, 60)
    print(f"{30*'-'}")
    print(f"Execution time in H:M:S = {int(hours):02}:{int(minutes):02}:{sec:.3f}")
    print(f"{30*'-'}")
