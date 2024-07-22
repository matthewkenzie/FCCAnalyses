import os
import uproot
import numpy as np
import awkward as ak
import matplotlib as mpl
import matplotlib.pyplot as plt
import config as cfg

plt.style.use('fcc.mplstyle')

filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'

keys = ['MC_PDG']

# Cut for Emin and particles in min hemisphere
#cut_min = '(EVT_Thrust_Emin_e < 20) & ((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) > 0)'

# Without cut
cut_min = '(MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) > 0'

# With cut
#cut_max = '(EVT_Thrust_Emin_e < 20) & ((MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) < 0)'

# Without cut
cut_max = '(MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5) < 0'
file = os.path.join(filepath, cfg.samples[4], 'chunk_0.root')

with uproot.open(file+':events') as tree:
    
    data_min = uproot.concatenate(tree, expressions=keys, cut = cut_min)
    min_ka_count = ak.count(data_min['MC_PDG'][(abs(data_min['MC_PDG']) == 311) | (abs(data_min['MC_PDG']) == 321)], axis=-1, mask_identity=True)
    min_pi_count = ak.count(data_min['MC_PDG'][(abs(data_min['MC_PDG']) == 111) | (abs(data_min['MC_PDG']) == 211)], axis=-1, mask_identity=True)
    min_ep_count = ak.count(data_min['MC_PDG'][abs(data_min['MC_PDG']) == 11], axis=-1, mask_identity=True)
    min_mu_count = ak.count(data_min['MC_PDG'][abs(data_min['MC_PDG']) == 13], axis=-1, mask_identity=True)
    min_ta_count = ak.count(data_min['MC_PDG'][abs(data_min['MC_PDG']) == 15], axis=-1, mask_identity=True)
    
    data_max = uproot.concatenate(tree, expressions=keys, cut = cut_max)
    max_ka_count = ak.count(data_max['MC_PDG'][(abs(data_max['MC_PDG']) == 311) | (abs(data_max['MC_PDG']) == 321)], axis=-1, mask_identity=True)
    max_pi_count = ak.count(data_max['MC_PDG'][(abs(data_max['MC_PDG']) == 111) | (abs(data_max['MC_PDG']) == 211)], axis=-1, mask_identity=True)
    max_ep_count = ak.count(data_max['MC_PDG'][abs(data_max['MC_PDG']) == 11], axis=-1, mask_identity=True)
    max_mu_count = ak.count(data_max['MC_PDG'][abs(data_max['MC_PDG']) == 13], axis=-1, mask_identity=True)
    max_ta_count = ak.count(data_max['MC_PDG'][abs(data_max['MC_PDG']) == 15], axis=-1, mask_identity=True)

#min_ka_count = ak.to_numpy(min_ka_count, allow_missing=True)
#min_pi_count = ak.to_numpy(min_pi_count, allow_missing=True)
#min_ep_count = ak.to_numpy(min_ep_count, allow_missing=True)
#min_mu_count = ak.to_numpy(min_mu_count, allow_missing=True)
#min_ta_count = ak.to_numpy(min_ta_count, allow_missing=True)
#max_ka_count = ak.to_numpy(max_ka_count, allow_missing=True)
#max_pi_count = ak.to_numpy(max_pi_count, allow_missing=True)
#max_ep_count = ak.to_numpy(max_ep_count, allow_missing=True)
#max_mu_count = ak.to_numpy(max_mu_count, allow_missing=True)
#max_ta_count = ak.to_numpy(max_ta_count, allow_missing=True)

min_tot_lp_count = min_ep_count + min_mu_count + min_ta_count
max_tot_lp_count = max_ep_count + max_mu_count + max_ta_count

min_ka_count = ak.flatten(min_ka_count, axis=0)
min_pi_count = ak.flatten(min_pi_count, axis=0)
min_ep_count = ak.flatten(min_ep_count, axis=0)
min_mu_count = ak.flatten(min_mu_count, axis=0)
min_ta_count = ak.flatten(min_ta_count, axis=0)
max_ka_count = ak.flatten(max_ka_count, axis=0)
max_pi_count = ak.flatten(max_pi_count, axis=0)
max_ep_count = ak.flatten(max_ep_count, axis=0)
max_mu_count = ak.flatten(max_mu_count, axis=0)
max_ta_count = ak.flatten(max_ta_count, axis=0)

min_tot_lp_count = ak.flatten(min_tot_lp_count, axis=0)
max_tot_lp_count = ak.flatten(max_tot_lp_count, axis=0)

min_histopts = {
        'histtype': 'step',
        'lw': 1.5,
        'color': 'blue',
        'hatch': '////'}

max_histopts = {
        'histtype': 'step',
        'lw': 1.5,
        'color': 'red',
        'hatch': '\\'}

fig, ax = plt.subplots()

ax.hist(
        x = min_ka_count,
        bins=range(min(min_ka_count), max(min_ka_count) + 1, 1),
        density = False,
        label = r'Emin hemisphere',
        **min_histopts)

ax.hist(
        x = max_ka_count,
        bins=range(min(max_ka_count), max(max_ka_count) + 1, 1),
        density = False,
        label = r'Emax hemisphere',
        **max_histopts)

ax.set_xlabel('Number of particles')
ax.set_xlim((0, 20))
ax.set_ylabel('Occurrences')
ax.set_title('Kaon count in both hemispheres')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/signal_k.png')

fig, ax = plt.subplots()

ax.hist(
        x = min_pi_count,
        bins=range(min(min_pi_count), max(min_pi_count) + 1, 1),
        density = False,
        label = r'Emin hemisphere',
        **min_histopts)

ax.hist(
        x = max_pi_count,
        bins=range(min(max_pi_count), max(max_pi_count) + 1, 1),
        density = False,
        label = r'Emax hemisphere',
        **max_histopts)

ax.set_xlabel('Number of particles')
ax.set_xlim((0, 40))
ax.set_ylabel('Occurrences')
ax.set_title('Pion count in both hemispheres')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/signal_pi.png')

fig, ax = plt.subplots()

ax.hist(
        x = min_ep_count,
        bins=range(min(min_ep_count), max(min_ep_count) + 1, 1),
        density = False,
        label = r'Emin hemisphere',
        **min_histopts)

ax.hist(
        x = max_ep_count,
        bins=range(min(max_pi_count), max(max_ep_count) + 1, 1),
        density = False,
        label = r'Emax hemisphere',
        **max_histopts)

ax.set_xlabel('Number of particles')
ax.set_xlim((0, 10))
ax.set_ylabel('Occurrences')
ax.set_title(r'$e^+e^-$ count in both hemispheres')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/signal_ep.png')

fig, ax = plt.subplots()

ax.hist(
        x = min_mu_count,
        bins=range(min(min_mu_count), max(min_mu_count) + 1, 1),
        density = False,
        label = r'Emin hemisphere',
        **min_histopts)

ax.hist(
        x = max_mu_count,
        bins=range(min(max_mu_count), max(max_mu_count) + 1, 1),
        density = False,
        label = r'Emax hemisphere',
        **max_histopts)

ax.set_xlabel('Number of particles')
ax.set_xlim((0, 5))
ax.set_ylabel('Occurrences')
ax.set_title(r'$\mu^+\mu^-$ count in both hemispheres')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/signal_mu.png')

fig, ax = plt.subplots()

ax.hist(
        x = min_ta_count,
        bins=range(min(min_ta_count), max(min_ta_count) + 1, 1),
        density = False,
        label = r'Emin hemisphere',
        **min_histopts)

ax.hist(
        x = max_ta_count,
        bins=range(min(max_ta_count), max(max_ta_count) + 1, 1),
        density = False,
        label = r'Emax hemisphere',
        **max_histopts)

ax.set_xlabel('Number of particles')
ax.set_xlim((0, 5))
ax.set_ylabel('Occurrences')
ax.set_title(r'$\tau^+\tau^-$ count in both hemispheres')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/signal_ta.png')

fig, ax = plt.subplots()

ax.hist(
        x = min_tot_lp_count,
        bins=range(min(min_tot_lp_count), max(min_tot_lp_count) + 1, 1),
        density = False,
        label = r'Emin hemisphere',
        **min_histopts)

ax.hist(
        x = max_tot_lp_count,
        bins=range(min(max_tot_lp_count), max(max_tot_lp_count) + 1, 1),
        density = False,
        label = r'Emax hemisphere',
        **max_histopts)

ax.set_xlabel('Number of particles')
ax.set_xlim((0, 10))
ax.set_ylabel('Occurrences')
ax.set_title('Total lepton count in both hemispheres')
ax.legend()

plt.savefig('/usera/rrm42/private/fcc-figures/part-count/signal_lepton.png')

