import os
import uproot
import numpy as np
import awkward as ak
import matplotlib as mpl
import matplotlib.pyplot as plt
import config as cfg

plt.style.use('fcc.mplstyle')

filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'

keys = ['MC_e', 'MC_p', 'MC_PDG']

# Cut for Emin and kaon in min hemisphere
#cut_min = '(EVT_Thrust_Emin_e < 20) & ((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) > 0) & ((abs(MC_PDG) == 321) | (abs(MC_PDG) == 311))'

# Without cut
cut_min = '((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) > 0) & ((abs(MC_PDG) == 321) | (abs(MC_PDG) == 311))'

# With cut
#cut_max = '(EVT_Thrust_Emin_e < 20) & ((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) < 0) & ((abs(MC_PDG) == 321) | (abs(MC_PDG) == 311))'

# Without cut
cut_max = '((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) < 0) & ((abs(MC_PDG) == 321) | (abs(MC_PDG) == 311))'

sigfile = os.path.join(filepath, cfg.samples[0], 'chunk_0.root')
bbfile = os.path.join(filepath, cfg.samples[1], 'chunk_0.root')

with uproot.open(sigfile+':events') as tree:
    
    data_min = uproot.concatenate(tree, expressions=keys, cut = cut_min)
    min_p = ak.max(data_min['MC_p'], axis=-1)
    min_e = ak.max(data_min['MC_e'], axis=-1)
    data_max = uproot.concatenate(tree, expressions=keys, cut = cut_max)
    max_p = ak.max(data_max['MC_p'], axis=-1)
    max_e = ak.max(data_max['MC_e'], axis=-1)

with uproot.open(bbfile+':events') as tree:
    data_min = uproot.concatenate(tree, expressions=keys, cut = cut_min)
    back_min_p = ak.max(data_min['MC_p'], axis=-1)
    back_min_e = ak.max(data_min['MC_e'], axis=-1)
    data_max = uproot.concatenate(tree, expressions=keys, cut = cut_max)
    back_max_p = ak.max(data_max['MC_p'], axis=-1)
    back_max_e = ak.max(data_max['MC_e'], axis=-1)

min_histopts = {
        'histtype': 'step',
        'lw': 1.5,
        'color': 'blue',
        'hatch': '////'}

max_histopts = {
        'histtype': 'step',
        'lw': 1.1,
        'color': 'red',
        'hatch': '////'}

back_min_histopts = {
        'histtype': 'step',
        'lw': 1,
        'color': 'orange',
        'alpha': 0.2,
        'fill': True}

back_max_histopts = {
        'histtype': 'step',
        'lw': 1,
        'color': 'green',
        'alpha': 0.2,
        'fill': True}

fig, ax = plt.subplots()

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

ax.hist(
        x = back_min_p,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emin',
        **back_min_histopts)

ax.hist(
        x = back_max_p,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emax',
        **back_max_histopts)

ax.set_xlim((0, 25))
ax.set_xlabel('MC_p')
ax.set_ylabel('Density')
ax.set_title('Most energetic kaon, before Emin cut')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/k_p.png')

fig, ax = plt.subplots()

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

ax.hist(
        x = back_min_e,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emin',
        **back_min_histopts)

ax.hist(
        x = back_max_e,
        bins=100,
        density = True,
        label = r'$Z \to b\bar{b}$ : Emax',
        **back_max_histopts)

ax.set_xlim((0, 25))
ax.set_xlabel('MC_e')
ax.set_ylabel('Density')
ax.set_title('Most energetic kaon, before Emin cut')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/k_e.png')
