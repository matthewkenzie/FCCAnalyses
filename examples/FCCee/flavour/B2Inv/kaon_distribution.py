import uproot
import matplotlib.pyplot as plt
import awkward as ak
import os
import numpy as np
import config as cfg
plt.style.use('fcc.mplstyle')

filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'
keys = ['MC_PDG', 'MC_px', 'MC_py', 'MC_pz', 'EVT_Thrust_x', 'EVT_Thrust_y', 'EVT_Thrust_z']
cut = 'EVT_Thrust_Emin_e < 20'
bins = 200

# Test with one signal and one background file
#signal_file = os.path.join(filepath, cfg.samples[0], "chunk_0.root")
#bb_file = os.path.join(filepath, cfg.samples[1], "chunk_0.root")
signal_file = os.path.join(filepath, 'p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu/chunk_0.root')
bb_file = os.path.join(filepath, 'p8_ee_Zbb_ecm91/chunk_0.root')
signal_tree = uproot.open(signal_file+':events')
background_tree = uproot.open(bb_file+':events')

# Run over signal file
#with uproot.open(signal_file+':events') as signal_tree:
signal_cut = uproot.concatenate(signal_tree, expressions = keys, cut=cut)
print('Created signal cuts')

num_events = len(signal_cut[keys[0]])
hist_Bs = np.array([])
#hist_kp = np.array([])
# Iterate over each row
for event in range(num_events):
    Thrust_x = signal_cut['EVT_Thrust_x'][event]
    Thrust_y = signal_cut['EVT_Thrust_y'][event]
    Thrust_z = signal_cut['EVT_Thrust_z'][event]
    Thrust_mag = (Thrust_x**2 + Thrust_y**2 + Thrust_z**2)**0.5
    # Find kaons and their momenta
    pids = signal_cut['MC_PDG'][event]
    for j in range(len(pids)):
        if abs(pids[j]) == 531:
            k_x = signal_cut['MC_px'][event][j]
            k_y = signal_cut['MC_py'][event][j]
            k_z = signal_cut['MC_pz'][event][j]
            k_mag = (k_x**2 + k_y**2 + k_z**2)**0.5
            if k_mag and Thrust_mag:
                cosTheta = (Thrust_x*k_x + Thrust_y*k_y + Thrust_z*k_z) / (k_mag * Thrust_mag)
            elif k_mag == 0:
                cosTheta = -2
            else:
                cosTheta = -3
            
            hist_Bs = np.append(hist_Bs, cosTheta)
        #elif abs(pids[j]) == 321:
        #    k_x = signal_cut['MC_px'][event][j]
        #    k_y = signal_cut['MC_py'][event][j]
        #    k_z = signal_cut['MC_pz'][event][j]
        #    k_mag = (k_x**2 + k_y**2 + k_z**2)**0.5
        #    if k_mag and Thrust_mag:
        #        cosTheta = (Thrust_x*k_x + Thrust_y*k_y + Thrust_z*k_z) / (k_mag * Thrust_mag)
        #    elif k_mag == 0:
        #        cosTheta = -2
        #    else:
        #        cos_Theta = -3
        #    
        #    hist_kp = np.append(hist_kp, cosTheta)

print('Finished signal events')

#with uproot.open(bb_file+':events') as background_tree:
back_cut = uproot.concatenate(background_tree, expressions = keys, cut=cut)
print('Created background cuts')

num_events = len(back_cut[keys[0]])
back_hist_Bs = np.array([])
#back_hist_kp = np.array([])
# Iterate over each row
for event in range(num_events):
    Thrust_x = back_cut['EVT_Thrust_x'][event]
    Thrust_y = back_cut['EVT_Thrust_y'][event]
    Thrust_z = back_cut['EVT_Thrust_z'][event]
    Thrust_mag = (Thrust_x**2 + Thrust_y**2 + Thrust_z**2)**0.5
    # Find kaons and their momenta
    pids = back_cut['MC_PDG'][event]
    for j in range(len(pids)):
        if abs(pids[j]) == 531:
            k_x = back_cut['MC_px'][event][j]
            k_y = back_cut['MC_py'][event][j]
            k_z = back_cut['MC_pz'][event][j]
            k_mag = (k_x**2 + k_y**2 + k_z**2)**0.5
            if k_mag and Thrust_mag:
                cosTheta = (Thrust_x*k_x + Thrust_y*k_y + Thrust_z*k_z) / (k_mag * Thrust_mag)
            elif k_mag == 0:
                cosTheta = -2
            else:
                cosTheta = -3
            
            back_hist_Bs = np.append(back_hist_Bs, cosTheta)
        #elif abs(pids[j]) == 321:
        #    k_x = back_cut['MC_px'][event][j]
        #    k_y = back_cut['MC_py'][event][j]
        #    k_z = back_cut['MC_pz'][event][j]
        #    k_mag = (k_x**2 + k_y**2 + k_z**2)**0.5
        #    if k_mag and Thrust_mag:
        #        cosTheta = (Thrust_x*k_x + Thrust_y*k_y + Thrust_z*k_z) / (k_mag * Thrust_mag)
        #    elif k_mag == 0:
        #        cosTheta = -2
        #    else:
        #        cos_Theta = -3
        #    
        #    back_hist_kp = np.append(back_hist_kp, cosTheta)

print('Finished background events')

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


#fig, ax = plt.subplots(figsize=(6,6))
fig, ax = plt.subplots(1, 2, figsize=(12,6))

ax[0].hist(
        x = hist_Bs,
        bins = bins,
        density = True,
        label = r'$B^0_s \to \nu\bar{\nu}$',
#        range=(0.75, 1.1),
        **signal_histopts)

ax[0].hist(
        x = back_hist_Bs,
        bins = bins,
        density = True,
#        range=(0.75, 1.1),
        label = r'$ Z \to b\bar{b} $',
        **back_histopts)

#ax[0].set_title(r'$K^0 / \bar{K}^0 $ relative to forward thrust')
ax[0].set_title(r'$ B_s^0 / \bar{B}_s^0 $ relative to forward thrust, with cut')
ax[0].set_xlim((0.75, 1.05))
ax[0].set_xlabel('cosTheta')
ax[0].set_ylabel('Density')
ax[0].legend()

ax[1].hist(
        x = hist_Bs,
        bins = bins,
        density = True,
        label = r'$B^0_s \to \nu\bar{\nu}$',
#        range=(-1.1, -0.75),
        **signal_histopts)

ax[1].hist(
        x = back_hist_Bs,
        bins = bins,
        density = True,
#        range=(-1.1, -0.75),
        label = r'$ Z \to b\bar{b} $',
        **back_histopts)

ax[1].set_title(r'$B_s^0 / \bar{B}_s^0 $ relative to reverse thrust, with cut')
ax[1].set_xlabel('cosTheta')
ax[1].set_ylabel('Density')
ax[1].set_xlim((-1.05, -0.75))
ax[1].legend()
plt.savefig('/usera/rrm42/private/fcc-figures/Bsdist/Bs_cut.png')

print('K0 plot saved')

#fig, ax = plt.subplots(1, 2, figsize=(12,6))
#ax[0].hist(
#        x = hist_kp,
#        bins = bins,
#        density = True,
#        range=(0.75, 1.1),
#        label = r'$B^0_s \to \nu\bar{\nu}$',
#        **signal_histopts)
#
#ax[0].hist(
#        x = back_hist_kp,
#        bins = bins,
#        density = True,
#        range=(0.75, 1.1),
#        label = r'$ Z \to b\bar{b} $',
#        **back_histopts)
#
#ax[0].set_title(r'$K^\pm $ relative to forward thrust')
#ax[0].set_xlabel('cosTheta')
#ax[0].set_ylabel('Density')
#ax[0].legend()
#
#ax[1].hist(
#        x = hist_kp,
#        bins = bins,
#        density = True,
#        range=(-1.1, -0.75),
#        label = r'$B^0_s \to \nu\bar{\nu}$',
#        **signal_histopts)
#
#ax[1].hist(
#        x = back_hist_kp,
#        bins = bins,
#        density = True,
#        range=(-1.1, -0.75),
#        label = r'$ Z \to b\bar{b} $',
#        **back_histopts)
#
#ax[1].set_title(r'$K^\pm $ relative to reverse thrust')
#ax[1].set_xlabel('cosTheta')
#ax[1].set_ylabel('Density')
#ax[1].legend()
#plt.savefig('/usera/rrm42/private/fcc-figures/kdist/kp.png')

print('K+ plot saved')
