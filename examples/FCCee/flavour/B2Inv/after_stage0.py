import os
import numpy as np
import uproot
import matplotlib as mpl
import matplotlib.pyplot as plt
import awkward as ak
import pandas as pd
plt.style.use('fcc.mplstyle')

import config as cfg

filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'
#keys = ['MC_p', 'MC_e']
#keys = ['MC_eta', 'MC_phi']
#keys = ['EVT_Thrust_Emin_n', 'EVT_Thrust_Emax_n']
#keys = ['MC_eta']
keys = ['(MC_q2_px*EVT_Thrust_x + MC_q2_py*EVT_Thrust_y + MC_q2_pz*EVT_Thrust_z)/((MC_q2_px**2 + MC_q2_py**2 + MC_q2_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5)']

cut = 'EVT_Thrust_Emin_e < 20'
bins = 100

# Test with one signal and one background file
signal_file = os.path.join(filepath, cfg.samples[0], "chunk_0.root")
bb_file = os.path.join(filepath, cfg.samples[1], "chunk_0.root")
signal_tree = uproot.open(signal_file+':events')
background_tree = uproot.open(bb_file+':events')
print('Opened files')

Emin_cut = uproot.concatenate(signal_tree, expressions = keys, cut=None)
#signal_pid = uproot.concatenate(signal_tree, expressions='MC_PDG', cut = cut)
print('Created signal cuts')

Emin_cut_back = uproot.concatenate(background_tree, expressions = keys, cut=None)
#background_pid = uproot.concatenate(background_tree, expressions='MC_PDG', cut = cut)
print('Created background cuts')
signal_histopts = {
        'histtype': 'step',
        'lw': 1.5,
        'color': 'blue',
        'hatch': '////'}

back_histopts = {
        'histtype': 'step',
        'lw': 1,
        'facecolor': 'red',
        'alpha': 0.5,
        'edgecolor': 'k',
        'fill': True}

# For per particle variables 
#for key in keys:
#    outpath = '/usera/rrm42/private/fcc-figures/cut/'
#    fig, ax = plt.subplots(2, 1, figsize=(6,10))
#    
#    ax[0].hist(
#        x = ak.ravel(Emin_cut[key]),
#        bins = bins,
#        range = [-6, 6],
#        density = True,
#        label = r'$ B^0_s \to \nu\bar{\nu} $',
#        **signal_histopts)
#
#    ax[0].hist(
#        x = ak.ravel(Emin_cut_back[key]),
#        bins = bins,
#        range = [-6, 6],
#        density = True,
#        label = r'$ Z \to b \bar{b} $',
#        **back_histopts)
#    
#    ax[0].set_title('Emin cut')
#    ax[0].set_xlabel(f'{key}')
#    ax[0].set_ylabel('Density')
#    #ax[0].set_xlim([0, 20])     # xlim for MC_p and MC_e
#    #ax[0].set_ylim([0, 0.5])    # ylim for MC_p and MC_e 
#    ax[0].set_xlim([-6, 6])     # xlim for MC_eta
#    ax[0].legend()
#
#    ax[1].hist(
#        x = ak.ravel(Emin_cut[key][abs(signal_pid['MC_PDG']) == 311]),
#        bins = bins,
#        range= [-6, 6],
#        density = True,
#        label = r'$ B^0_s \to \nu\bar{\nu} $',
#        **signal_histopts)
#
#    ax[1].hist(
#        x = ak.ravel(Emin_cut_back[key][abs(background_pid['MC_PDG']) == 311]),
#        bins = bins,
#        range = [-6, 6],
#        density = True,
#        label = r'$ Z \to b \bar{b} $',
#        **back_histopts)
#
#    ax[1].set_title(r'$ K^0/\bar{K}^0 $ and ' + 'Emin cut')
#    ax[1].set_xlabel(f'{key}')
#    ax[1].set_ylabel('Density')
#    #ax[1].set_xlim([0, 20])     # xlim for MC_p and MC_e
#    #ax[1].set_ylim([0, 0.5])    # ylim for MC_p and MC_e
#    ax[1].set_xlim([-6, 6])     # xlim for MC_eta
#    ax[1].legend()
#    plt.savefig(os.path.join(outpath, f'{key}.png'))

# For per event variables ie cannot cut using PID or per particle variable
for key in keys:
    outpath = '/usera/rrm42/private/fcc-figures/cut/'
    fig, ax = plt.subplots(1, 2, figsize=(12,6))
    
    ax[0].hist(
        x = ak.ravel(Emin_cut[key]),
        bins = bins,
        density = True,
        range = (0.7, 1.05),
        label = r'$ B^0_s \to \nu\bar{\nu} $',
        **signal_histopts)

    ax[0].hist(
        x = ak.ravel(Emin_cut_back[key]),
        bins = bins,
        density = True,
        range = (0.7, 1.05),
        label = r'$ Z \to b \bar{b} $',
        **back_histopts)
    
    ax[0].set_title(r'MC_q2 ($\bar{b}$) relative to forward thrust')
    ax[0].set_xlabel('cosTheta')
    ax[0].set_xlim((0.9, 1.05))
    ax[0].set_ylabel('Density')
    ax[0].legend()
    
    ax[1].hist(
        x = ak.ravel(Emin_cut[key]),
        bins = bins,
        density = True,
        range = (-1.05, -0.7),
        label = r'$ B^0_s \to \nu\bar{\nu} $',
        **signal_histopts)

    ax[1].hist(
        x = ak.ravel(Emin_cut_back[key]),
        bins = bins,
        density = True,
        range = (-1.05, -0.7),
        label = r'$ Z \to b \bar{b} $',
        **back_histopts)
    
    ax[1].set_title(r'MC_q2 ($\bar{b}$) relative to reverse thrust')
    ax[1].set_xlabel('cosTheta')
    ax[1].set_ylabel('Density')
    ax[1].set_xlim((-1.05,-0.9))
    ax[1].legend()
    plt.savefig(os.path.join(outpath, 'q2_bb.png'))
print('Saved files')
