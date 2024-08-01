import os
import uproot
import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import config as cfg

plt.style.use('fcc.mplstyle')

filepath = '/r01/lhcb/rrm42/fcc/post_stage0/'

sigfile = os.path.join(filepath, cfg.samples_poststage0[0]+'.root')
bbfile = os.path.join(filepath, cfg.samples_poststage0[1]+'.root')

with uproot.open(sigfile+':events') as tree:
    
    data_min = uproot.concatenate(tree, expressions=['Rec_e', 'Rec_p'], cut = '(Thrust_delE > 35) & (Rec_cosrel2thrust > 0) & (abs(MC_PDG) == 211)')
    min_p = ak.max(data_min['Rec_p'], axis=-1)
    min_e = ak.max(data_min['Rec_e'], axis=-1)
    data_max = uproot.concatenate(tree, expressions=['Rec_e', 'Rec_p'], cut = '(Thrust_delE > 35) & (Rec_cosrel2thrust < 0) & (abs(MC_PDG) == 211)')
    max_p = ak.max(data_max['Rec_p'], axis=-1)
    max_e = ak.max(data_max['Rec_e'], axis=-1)

print("Signal files done")

with uproot.open(bbfile+':events') as tree:
    data_min = uproot.concatenate(tree, expressions=['Rec_e', 'Rec_p'], cut = '(Thrust_delE > 35) & (Rec_cosrel2thrust > 0) & (abs(MC_PDG) == 211)')
    back_min_p = ak.max(data_min['Rec_p'], axis=-1)
    back_min_e = ak.max(data_min['Rec_e'], axis=-1)
    data_max = uproot.concatenate(tree, expressions=['Rec_e', 'Rec_p'], cut = '(Thrust_delE > 35) & (Rec_cosrel2thrust < 0) & (abs(MC_PDG) == 211)')
    back_max_p = ak.max(data_max['Rec_p'], axis=-1)
    back_max_e = ak.max(data_max['Rec_e'], axis=-1)

print("Background files done")

min_histopts = {
        'histtype': 'step',
        'lw': 2,
        'color': 'blue'}

max_histopts = {
        'histtype': 'step',
        'lw': 2,
        'color': 'red'}

back_min_histopts = {
        'histtype': 'step',
        'lw': 1,
        'color': 'orange',
        'alpha': 0.5,
        'fill': True}

back_max_histopts = {
        'histtype': 'step',
        'lw': 1,
        'color': 'green',
        'alpha': 0.5,
        'fill': True}

fig, ax = plt.subplots()

ax.hist(
        x = back_max_p,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emax',
        **back_max_histopts)

ax.hist(
        x = back_min_p,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emin',
        **back_min_histopts)

ax.hist(
        x = min_p,
        density = True,
        bins=200,
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emin',
        **min_histopts)

ax.hist(
        x = max_p,
        bins=200,
        density = True,
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emax',
        **max_histopts)

ax.set_xlim((0, 45))
ax.set_xlabel('Rec_p')
ax.set_ylabel('Density')
ax.set_title(r'$|\vec{p}|$ of most energetic pion, with $\Delta E$ cut')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/k_p.png')

fig, ax = plt.subplots()

ax.hist(
        x = back_max_e,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emax',
        **back_max_histopts)

ax.hist(
        x = back_min_e,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emin',
        **back_min_histopts)

ax.hist(
        x = min_e,
        density = True,
        bins=200,
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emin',
        **min_histopts)

ax.hist(
        x = max_e,
        bins=200,
        density = True,
        label = r'$B_s^0 \to \nu \bar{\nu}$ : Emax',
        **max_histopts)

ax.set_xlim((0, 45))
ax.set_xlabel('Rec_e')
ax.set_ylabel('Density')
ax.set_title(r'$E$ of most energetic pion, with $\Delta E$ cut')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/k_e.png')

