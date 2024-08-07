import os, sys
import ROOT

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import awkward as ak

from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import roc_curve, auc
from sklearn.utils.class_weight import compute_sample_weight
import xgboost as xgb

ROOT.EnableImplicitMT()
plt.rcParams['text.usetex'] = True

filepath = "/r01/lhcb/mkenzie/fcc/B2Inv/stage0/"
outpath = "/r01/lhcb/rrm42/fcc"

folders = [
        "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu",
        "p8_ee_Zbb_ecm91",
        "p8_ee_Zcc_ecm91",
        "p8_ee_Zss_ecm91",
        "p8_ee_Zud_ecm91",
        ]

listvars = {"EVT_Thrust_Emin_e",
            "EVT_Thrust_Emax_e",
            "EVT_Thrust_Emin_e_charged",
            "EVT_Thrust_Emin_e_neutral",
            "EVT_Thrust_Emax_e_charged",
            "EVT_Thrust_Emax_e_neutral",
            "EVT_Thrust_Emin_n_charged",
            "EVT_Thrust_Emin_n_neutral",
            "EVT_Thrust_Emax_n_charged",
            "EVT_Thrust_Emin_n_neutral",
            "Rec_pv_ntracks",
            "Rec_vtx_n",
            "EVT_Thrust_Emin_ndv",
            "EVT_Thrust_Emax_ndv",
            "Rec_vtx_d2pv_min",
            "Rec_vtx_d2pv_max",
            "Rec_vtx_d2pv_avg",
            "EVT_Thrust_mag",
            "EVT_Thrust_x",
            "EVT_Thrust_y",
            "EVT_Thrust_z"}

listvarslist = list(listvars)

plotvarslist = listvarslist + ["Rec_e", "Rec_type", "Rec_px", "Rec_py", "Rec_pz", "Rec_p"]
plotvars = set(plotvarslist)
cols = [
        "EVT_ThrustEmin_E", 
        "EVT_ThrustEmax_E",
        "EVT_ThrustEmin_Echarged",
        "EVT_ThrustEmax_Echarged",
        "EVT_ThrustEmin_Eneutral",
        "EVT_ThrustEmax_Eneutral",
        "EVT_ThrustEmin_Ncharged",
        "EVT_ThrustEmax_Ncharged",
        "EVT_ThrustEmin_Nneutral",
        "EVT_ThrustEmax_Nneutral",
        "EVT_NtracksPV",
        "EVT_NVertex",
        "EVT_ThrustEmin_NDV",
        "EVT_ThrustEmax_NDV",
        "EVT_dPV2DVmin",
        "EVT_dPV2DVmax",
        "EVT_dPV2DVave",
        "EVT_Thrust_Mag",
        "EVT_Thrust_X", 
        "EVT_Thrust_Y", 
        "EVT_Thrust_Z",
        "EVT_ThrustDiff_E",
        ] 

plotcols = cols+["Rec_cos", "Rec_e", "Rec_type"]

#sg_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[0], "*.root"), listvars)
#bb_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[1], "*.root"), listvars)
#cc_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[2], "*.root"), listvars)
#ss_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[3], "*.root"), listvars)
#ud_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[4], "*.root"), listvars)

sg_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[0], "*.root"), plotvars)
bb_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[1], "*.root"), plotvars)
cc_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[2], "*.root"), plotvars)
ss_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[3], "*.root"), plotvars)
ud_df = ROOT.RDataFrame("events", os.path.join(filepath, folders[4], "*.root"), plotvars)

print(f"{'-'*50}\n\n")
print("RDataFrames instantiated")

def getaliases(df):
    df2 = (
        df
        .Define("Rec_cos", "(Rec_px*EVT_Thrust_x + Rec_py*EVT_Thrust_y + Rec_pz*EVT_Thrust_z)/(Rec_p*(EVT_Thrust_x**2+EVT_Thrust_y**2+EVT_Thrust_z**2)**0.5)")
        .Alias("EVT_ThrustEmin_E",        "EVT_Thrust_Emin_e")
        .Alias("EVT_ThrustEmax_E",        "EVT_Thrust_Emax_e")
        .Alias("EVT_ThrustEmin_Echarged", "EVT_Thrust_Emin_e_charged")
        .Alias("EVT_ThrustEmax_Echarged", "EVT_Thrust_Emax_e_charged")
        .Alias("EVT_ThrustEmin_Eneutral", "EVT_Thrust_Emin_e_neutral")
        .Alias("EVT_ThrustEmax_Eneutral", "EVT_Thrust_Emax_e_neutral")
        .Alias("EVT_ThrustEmin_Ncharged", "EVT_Thrust_Emin_e_charged")
        .Alias("EVT_ThrustEmax_Ncharged", "EVT_Thrust_Emax_n_charged")
        .Alias("EVT_ThrustEmin_Nneutral", "EVT_Thrust_Emin_n_neutral")
        .Alias("EVT_ThrustEmax_Nneutral", "EVT_Thrust_Emax_n_neutral")
        .Alias("EVT_NtracksPV",           "Rec_pv_ntracks")
        .Alias("EVT_NVertex",             "Rec_vtx_n")
        .Alias("EVT_ThrustEmin_NDV",      "EVT_Thrust_Emin_ndv")
        .Alias("EVT_ThrustEmax_NDV",      "EVT_Thrust_Emax_ndv")
        .Alias("EVT_dPV2DVmin",           "Rec_vtx_d2pv_min")
        .Alias("EVT_dPV2DVmax",           "Rec_vtx_d2pv_max")
        .Alias("EVT_dPV2DVave",           "Rec_vtx_d2pv_ave")
        .Alias("EVT_Thrust_Mag",          "EVT_Thrust_mag")
        .Alias("EVT_Thrust_X",            "EVT_Thrust_x")
        .Alias("EVT_Thrust_Y",            "EVT_Thrust_y")
        .Alias("EVT_Thrust_Z",            "EVT_Thrust_z")
    
        .Define("EVT_ThrustDiff_E",       "EVT_ThrustEmax_E - EVT_ThrustEmin_E")
    )
    return df2

outlist = []
for df in [sg_df, bb_df, cc_df, ss_df, ud_df]:
    outlist.append(getaliases(df))

print("Necessary variables defined")

#sg_df_pd = pd.DataFrame(outlist[0].AsNumpy(columns=cols))
#bb_df_pd = pd.DataFrame(outlist[1].AsNumpy(columns=cols))
#cc_df_pd = pd.DataFrame(outlist[2].AsNumpy(columns=cols))
#ss_df_pd = pd.DataFrame(outlist[3].AsNumpy(columns=cols))
#ud_df_pd = pd.DataFrame(outlist[4].AsNumpy(columns=cols))

sg_df_pd = pd.DataFrame(outlist[0].AsNumpy(columns=plotcols))
bb_df_pd = pd.DataFrame(outlist[1].AsNumpy(columns=plotcols))
cc_df_pd = pd.DataFrame(outlist[2].AsNumpy(columns=plotcols))
ss_df_pd = pd.DataFrame(outlist[3].AsNumpy(columns=plotcols))
ud_df_pd = pd.DataFrame(outlist[4].AsNumpy(columns=plotcols))

print("Dataframes copied to pandas\n\n")
print(f"{'-'*50}")

######################################################
#
# PREPROCESSING
#
######################################################
#sg_df_pd['category'] = np.ones(sg_df_pd.shape[0])
#bb_df_pd['category'] = np.zeros(bb_df_pd.shape[0])
#cc_df_pd['category'] = np.zeros(cc_df_pd.shape[0])
#ss_df_pd['category'] = np.zeros(ss_df_pd.shape[0])
#ud_df_pd['category'] = np.zeros(ud_df_pd.shape[0])
sg_df_pd['category'] = 1
bb_df_pd['category'] = 0
cc_df_pd['category'] = 0
ss_df_pd['category'] = 0
ud_df_pd['category'] = 0

br_frac_bb = 0.1512
br_frac_cc = 0.1203
br_frac_ss = 0.1560
br_frac_ud = 0.1560 + 0.1160

totnum = np.mean([bb_df_pd.shape[0], cc_df_pd.shape[0], ss_df_pd.shape[0], ud_df_pd.shape[0]])

bb_df_pd = bb_df_pd[:round(totnum*br_frac_bb)]
cc_df_pd = cc_df_pd[:round(totnum*br_frac_cc)]
ss_df_pd = ss_df_pd[:round(totnum*br_frac_ss)]
ud_df_pd = ud_df_pd[:round(totnum*br_frac_ud)]

tot_pd = pd.concat([bb_df_pd, cc_df_pd, ss_df_pd, ud_df_pd], copy=True, ignore_index=True)
tot_pd = pd.concat([tot_pd, sg_df_pd[:round(0.1*totnum)]], ignore_index=True)

sc = StandardScaler()
sc.set_output(transform = 'pandas')
sc.fit(tot_pd[cols])
sc.transform(tot_pd[cols])

for df in [sg_df_pd, bb_df_pd, cc_df_pd, ss_df_pd, ud_df_pd]:
    df[cols] = sc.transform(df[cols])


################################################################
#
# Load BDT
#
################################################################
bdt = xgb.XGBClassifier()
bdt.load_model('/r01/lhcb/rrm42/fcc/bdt1.json')

importance = pd.DataFrame(bdt.feature_importances_, index=cols, columns=['importance'])
importance.to_csv(os.path.join(outpath, 'bdt1test-importance.csv'))
print(importance)
print(f'CSV of importances saved to {os.path.join(outpath, "bdt1test-importance.csv")}')
print(f"{'-'*50}\n")

dfdict = ['Signal', 'bb background', 'cc background', 'ss background', 'ud background', 'total background with 10% signal']
#precut = [0, 0, 0, 0, 0]
for idx, df in enumerate([sg_df_pd, bb_df_pd, cc_df_pd, ss_df_pd, ud_df_pd, tot_pd]):
    precut = df.shape[0]
    df['XGB'] = bdt.predict_proba(df[cols])[:,1]
    df['predcategory'] = np.logical_not(np.logical_xor(df['category'], df['XGB']>0.9))
    
    postcut = df[df['XGB'] > 0.9].shape[0]

    print(f"{dfdict[idx]} pre cut length = {precut}")
    print(f"Number of mis-id'ed events = {df[df['predcategory'] == False].shape[0]}")
    print(f"Number of passed events = {postcut}")
    print(f"Efficiency = {postcut/precut}\n")

print(f"{'-'*50}")
sg_cut = sg_df_pd.query('XGB>0.9')
bb_cut = bb_df_pd.query('XGB>0.9')
cc_cut = cc_df_pd.query('XGB>0.9')
ss_cut = ss_df_pd.query('XGB>0.9')
ud_cut = ud_df_pd.query('XGB>0.9')

##################################
# PLOTTING
#
#################################

# roc curve and significance
#val = tot_pd['category']
#score = bdt.predict_proba(tot_pd[cols])[:, 1]
#fpr, tpr, thresholds = roc_curve(val, score)
#area = auc(fpr, tpr)
#
#fig, ax = plt.subplots()
#ax.plot([0, 1], [0, 1], color='gray', ls='--')
#ax.plot(fpr, tpr, label=f'ROC curve (AUC = {area:.4f})')
#ax.set_xlim((0, 1))
#ax.set_ylim((0, 1))
#ax.set_xlabel("False positive rate")
#ax.set_ylabel("True positive rate")
#ax.legend(loc='lower right')
#ax.set_aspect('equal', adjustable='box')
#ax.set_title('ROC curve for BDT1 applied to stage0')
#fig.tight_layout()
#plt.savefig(os.path.join(outpath, 'bdt1test-roc.pdf'))
#print(f'ROC curve saved to {os.path.join(outpath, "bdt1test-roc.pdf")}')
#
## significance
#S = sg_df_pd.shape[0]*tpr
#B = (tot_pd.shape[0])*fpr
#epsilon = 1e-10
#metric = S/np.sqrt(S + B + epsilon)
#optimum = thresholds[np.argmax(metric)]
#print(f"Highest FoM = {np.max(metric):.4f}, at XGB value {optimum:.4f}")
#
#fig, ax = plt.subplots()
#ax.plot(thresholds, metric, label='XGB')
#ax.axvline(optimum, color='black', ls='--', label=f'Optimal cut ({optimum:.3f})')
#ax.set_xlim((0, 1))
#ax.set_xlabel(r'$P_{XGB}$ cut value')
#ax.set_ylabel(r'FoM, $\frac{S}{\sqrt{S+B}}$')
#ax.set_title('Significance plot of BDT1 applied to stage0')
#fig.tight_layout()
#plt.savefig(os.path.join(outpath, 'bdt1test-significance.pdf'))
#print(f'Significance plot saved to {os.path.join(outpath, "bdt1test-significance.pdf")}')
#
## bdt response
#fig, ax = plt.subplots()
#ax.set_yscale('log')
#_, bins, _ = ax.hist(sg_df_pd['XGB'], bins=100, density=True, histtype='stepfilled', color = 'gold', label=r'$B_s^0 \to \nu\bar{\nu}$')
#ax.hist(bb_df_pd['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to b\bar{b}$')
#ax.hist(cc_df_pd['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to c\bar{c}$')
#ax.hist(ss_df_pd['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to s\bar{s}$')
#ax.hist(ud_df_pd['XGB'], bins=bins, density=True, histtype='step', label=r'$Z \to ud$')
#
#ax.set_xlabel("BDT Response")
#ax.set_ylabel("Normalised counts")
#ax.set_xlim((bins[0], bins[-1]))
#ax.legend(loc='best')
#ax.set_title('BDT1 response when applied to stage0')
#fig.tight_layout()
#plt.savefig(os.path.join(outpath, 'bdt1test-response.pdf'))
#print(f'BDT1 response curve saved to {os.path.join(outpath, "bdt1test-response.pdf")}')

##################################
# COMPARE PRE AND POST BDT VAR
#
#################################
plotlist = ['Signal', 'bb', 'cc', 'ss', 'ud']
plotdict = {}
for i, df in enumerate([sg_cut, bb_cut, cc_cut, ss_cut, ud_cut]):
    df.reset_index()
    lEmin = np.array([])
    lEmin = np.array([])
    lEmax = np.array([])
    kEmin = np.array([])
    kEmax = np.array([])
    pEmin = np.array([])
    pEmax = np.array([])

    for index, event in df.iterrows():
        lep_inmin = np.where((event['Rec_cos'] > 0) & ((event['Rec_type'] == 11) | (event['Rec_type'] == 13))).shape[0]
        lEmin = np.append(lEmin, lep_inmin)
        lep_inmax = np.where((event['Rec_cos'] < 0) & ((event['Rec_type'] == 11) | (event['Rec_type'] == 13))).shape[0]
        lEmax = np.append(lEmax, lep_inmax)
        
        k_inmin = np.where((event['Rec_cos'] > 0) & (event['Rec_type'] == 321)).shape[0]
        kEmin = np.append(kEmin, k_inmin)
        k_inmax = np.where((event['Rec_cos'] < 0) & (event['Rec_type'] == 321)).shape[0]
        kEmax = np.append(kEmax, k_inmax)

        p_inmin = np.where((event['Rec_cos'] > 0) & (event['Rec_type'] == 211)).shape[0]
        p_inmax = np.where((event['Rec_cos'] < 0) & (event['Rec_type'] == 211)).shape[0]
        pEmin = np.append(pEmin, p_inmin)
        pEmax = np.append(pEmax, p_inmax)

    plotdict[plotlist[i]]['lEmin'] = lEmin
    plotdict[plotlist[i]]['lEmax'] = lEmax
    plotdict[plotlist[i]]['kEmin'] = kEmin
    plotdict[plotlist[i]]['kEmax'] = kEmax
    plotdict[plotlist[i]]['pEmin'] = pEmin
    plotdict[plotlist[i]]['pEmax'] = pEmax

min_histopts = {
        'density':True,
        'histtype':'step',
        'lw':2,
        'color':'red'
        }

min_histopts = {
        'density':True,
        'histtype':'step',
        'lw':2,
        'ls':'--',
        'color':'cornflowerblue'
        }

for title in plotlist:
    for i in ['l', 'k', 'p']:
        fig, ax = plt.subplots()
        
        ax.hist(x = plotdict[title][i+'Emin'], **min_histopts)
        ax.hist(x = plotdict[title][i+'Emax'], **max_histopts)
        ax.set_title(f"{title}")
        fig.tight_layout()
        plt.savefig(f"/r01/lhcb/rrm42/fcc/bdttest{title}.pdf")
        print(f"{title} saved")
