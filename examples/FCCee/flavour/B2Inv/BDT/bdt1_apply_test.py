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
inpath="/r01/lhcb/rrm42/fcc/stage1/"
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
    df_np = df.AsNumpy(columns=cols+['EVT_Thrust_deltaE'])
    x = pd.DataFrame(df_np)

    if category=='signal':
        y = pd.DataFrame(np.ones(x.shape[0]), columns=['category'])
    elif category=='background':
        y = pd.DataFrame(np.zeros(x.shape[0]), columns=['category'])
    else:
        raise ValueError(f"{category} is invalid, must be 'signal' or 'background'")

    w = pd.DataFrame(eff*np.ones(x.shape[0]), columns=['weights'])

    return df, x, y, w

if __name__ == "__main__":
    # Efficiencies of pre-selection cuts + branching fraction
    sig_bf = cfg.branching_fractions['p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu'][0]
    bb_bf  = cfg.branching_fractions['p8_ee_Zbb_ecm91'][0]
    cc_bf  = cfg.branching_fractions['p8_ee_Zcc_ecm91'][0]
    ss_bf  = cfg.branching_fractions['p8_ee_Zss_ecm91'][0]
    ud_bf  = cfg.branching_fractions['p8_ee_Zud_ecm91'][0]
    bb_bf_norm = bb_bf/(bb_bf + cc_bf + ss_bf + ud_bf)
    cc_bf_norm = cc_bf/(bb_bf + cc_bf + ss_bf + ud_bf)
    ss_bf_norm = ss_bf/(bb_bf + cc_bf + ss_bf + ud_bf)
    ud_bf_norm = ud_bf/(bb_bf + cc_bf + ss_bf + ud_bf)
    
    sig_eff = cfg.efficiencies['stage1']['Bs2NuNu']['eff']
    bb_eff  = cfg.efficiencies['stage1']['bb']['eff']
    cc_eff  = cfg.efficiencies['stage1']['cc']['eff']
    ss_eff  = cfg.efficiencies['stage1']['ss']['eff']
    ud_eff  = cfg.efficiencies['stage1']['ud']['eff']

    #print("Efficiencies loaded")
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
    bbfiles  = glob(bbpath)[:10]
    ccfiles  = glob(ccpath)[:10]
    ssfiles  = glob(sspath)
    udfiles  = glob(udpath)
    
    sg_df, sg_x, sg_y, sg_w = load_data(sigfiles, 'signal',    sig_eff*sig_bf, bdtvars)
    bb_df, bb_x, bb_y, bb_w = load_data(bbfiles,  'background', bb_eff*bb_bf_norm, bdtvars)
    cc_df, cc_x, cc_y, cc_w = load_data(ccfiles,  'background', cc_eff*cc_bf_norm, bdtvars)
    ss_df, ss_x, ss_y, ss_w = load_data(ssfiles,  'background', ss_eff*ss_bf_norm, bdtvars)
    ud_df, ud_x, ud_y, ud_w = load_data(udfiles,  'background', ud_eff*ud_bf_norm, bdtvars)

    #tot_x = pd.concat([sg_x, bb_x, cc_x, ss_x, ud_x], copy=True, ignore_index=True)
    #tot_y = pd.concat([sg_y, bb_y, cc_y, ss_y, ud_y], copy=True, ignore_index=True)
    #tot_w = pd.concat([sg_w, bb_w, cc_w, ss_w, ud_w], copy=True, ignore_index=True)

    # Load BDT
    bdt = xgb.XGBClassifier()
    bdt.load_model('/r01/lhcb/rrm42/fcc/bdt1out/bdt1.json')

    # bdt response
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    ax1.set_xscale('log')
    ax1.set_xlabel(r'BF($B_s \to \nu\bar{\nu}$)', fontsize=12)
    ax1.set_ylabel(r'$\sqrt{S+B}/S$', fontsize=12)
    ax1.set_title('Sensitivity using stage1')

    ax2.set_xscale('log')
    ax2.set_xlabel(r'BF($B_s \to \nu\bar{\nu}$)', fontsize=12)
    ax2.set_ylabel(r'$S/\sqrt{S+B}$')
    ax2.set_title('Sensitivity using stage1')
    x = np.logspace(-7, -3, 200)

    fig3, ax3 = plt.subplots()
    cut = np.linspace(0, 1, 100)
    sens3 = np.array([])
    for xgb in cut:
        bdteff = []
        #print(f'XGB > {cut}')
        for df in [sg_x, bb_x, cc_x, ss_x, ud_x]:
            df['XGB'] = bdt.predict_proba(df[bdtvars])[:, 1]
            before = df.shape[0]
            after = df.query(f'XGB > {xgb}').shape[0]
            bdteff.append(after/before)
            #print(f'Before = {before:.3e}, After = {after}, Efficiency = {after/before:.3e}')
        #print('\n\n\n')
        # plotting
        N_Z = 6e12
        bb_pred = N_Z*bb_bf*bb_eff*bdteff[1]
        cc_pred = N_Z*cc_bf*cc_eff*bdteff[2]
        ss_pred = N_Z*ss_bf*ss_eff*bdteff[3]
        ud_pred = N_Z*ud_bf*ud_eff*bdteff[4]

        S_withoutbf = 2*N_Z*bb_bf*0.096*sig_eff*bdteff[0]
        B = bb_pred+cc_pred+ss_pred+ud_pred
        #S = S_withoutbf*x
        #sens1 = np.sqrt(S + B)/(S)
        #sens2 = S/np.sqrt(S+B)

        sens3 = np.append(sens3, (sig_eff*bdteff[0])/np.sqrt(B + 2.5))
        #ax1.plot(x, sens1, label=f'XGB $>$ {cut}')
        #ax2.plot(x, sens2, label=f'XGB $>$ {cut}')
    
    ax3.plot(cut, sens3)
    #ax1.legend(loc='best', fontsize=12)
    #ax2.legend(loc='best', fontsize=12)
    #fig1.tight_layout()
    #fig2.tight_layout()
    fig3.savefig('/usera/rrm42/out.pdf')
    #fig1.savefig(os.path.join(outpath, "sens1-stage1.pdf"))
    #fig2.savefig(os.path.join(outpath, "sens2-stage1.pdf"))
    print(f'Sensitivity plots saved')
