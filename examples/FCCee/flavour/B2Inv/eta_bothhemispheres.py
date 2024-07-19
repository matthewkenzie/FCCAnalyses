import os
import uproot
import numpy as np
import awkward as ak
import matplotlib as mpl
import matplotlib.pyplot as plt
import config as cfg

plt.style.use('fcc.mplstyle')

filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'

keys = ['MC_eta']

# Cut for Emin and kaon in min hemisphere
cut_min = '(EVT_Thrust_Emax_e - EVT_Thrust_Emin_e > 25) & ((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) > 0)'

# Without cut
nocut_min = '((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) > 0)'

# With cut
cut_max = '(EVT_Thrust_Emax_e - EVT_Thrust_Emin_e > 25) & ((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) < 0)'

# Without cut
nocut_max = '((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) < 0)'

sigfile = os.path.join(filepath, cfg.samples[0], 'chunk_0.root')
bbfile = os.path.join(filepath, cfg.samples[1], 'chunk_0.root')

with uproot.open(sigfile+':events') as tree:
    
    sigeta_min_cut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut = cut_min)['MC_eta'])
    sigeta_min_nocut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut=nocut_min)['MC_eta'])
    sigeta_max_cut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut = cut_max)['MC_eta'])
    sigeta_max_nocut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut = nocut_max)['MC_eta'])

with uproot.open(bbfile+':events') as tree:

    bbeta_min_cut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut = cut_min)['MC_eta'])
    bbeta_min_nocut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut=nocut_min)['MC_eta'])
    bbeta_max_cut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut = cut_max)['MC_eta'])
    bbeta_max_nocut = ak.ravel(uproot.concatenate(tree, expressions=keys, cut = nocut_max)['MC_eta'])

min_histopts = {
        'stacked': False,
        'histtype': 'stepfilled',
        'lw': 1,
        'color': 'orange',
        'alpha': 0.4,
        'fill': True}

max_histopts = {
        'stacked': False,
        'histtype': 'step',
        'lw': 1,
        'color': 'green',
        'hatch': '/'}

total_histopts = {
        'stacked': False,
        'histtype': 'step',
        'lw': 2,
        'color': 'black'}

fig, ax = plt.subplots(1, 2, figsize=(12,6))

ax[0].hist(
        x = sigeta_min_cut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Emin hemisphere',
        **min_histopts)

ax[0].hist(
        x = sigeta_max_cut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emax hemisphere',
        **max_histopts)

ax[0].hist(
        x = ak.concatenate((sigeta_min_cut, sigeta_max_cut)),
        density=True,
        bins=100,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Total',
        **total_histopts)

ax[0].set_xlabel('MC_eta')
ax[0].set_ylabel('Density')
ax[0].set_title(r'$\eta$ in signal file, after $\Delta E$ cut')
ax[0].legend(fontsize=10)

ax[1].hist(
        x = sigeta_min_nocut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Emin hemisphere',
        **min_histopts)

ax[1].hist(
        x = sigeta_max_nocut,
        density=True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emax hemisphere',
        **max_histopts)

ax[1].hist(
        x = ak.concatenate((sigeta_min_nocut, sigeta_max_nocut)),
        density=True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Total',
        **total_histopts)

ax[1].set_xlabel('MC_eta')
ax[1].set_ylabel('Density')
ax[1].set_title(r'$\eta$ in signal file, without $\Delta E$ cut')
ax[1].legend(fontsize=10)

plt.savefig('/usera/rrm42/private/fcc-figures/sigeta.png')

fig, ax = plt.subplots(1, 2, figsize=(12,6))

ax[0].hist(
        x = bbeta_min_cut,
        density = True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Emin hemisphere',
        **min_histopts)

ax[0].hist(
        x = bbeta_max_cut,
        density=True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emax hemisphere',
        **max_histopts)

ax[0].hist(
        x = ak.concatenate((bbeta_min_cut, bbeta_max_cut)),
        density=True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Total',
        **total_histopts)

ax[0].set_xlabel('MC_eta')
ax[0].set_ylabel('Density')
ax[0].set_title(r'$\eta$ in bb file, after $\Delta E$ cut')
ax[0].legend(fontsize=10)

ax[1].hist(
        x = bbeta_min_nocut,
        density = True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Emin hemisphere',
        **min_histopts)

ax[1].hist(
        x = bbeta_max_nocut,
        density=True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emax hemisphere',
        **max_histopts)

ax[1].hist(
        x = ak.concatenate((bbeta_min_nocut, bbeta_max_nocut)),
        density=True,
        bins=200,
        range=(-6,6),
        label = r'$B_s^0 \to \nu\bar{\nu}$ : Total',
        **total_histopts)

ax[1].set_xlabel('MC_eta')
ax[1].set_ylabel('Density')
ax[1].set_title(r'$\eta$ in bb file, without $\Delta E$ cut')
ax[1].legend(fontsize=10)

plt.savefig('/usera/rrm42/private/fcc-figures/bbeta.png')
