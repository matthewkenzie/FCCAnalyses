import os
import uproot
import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import pandas as pd
plt.style.use('/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv/fcc.mplstyle')

def get_costheta(eta):
    #if eta > 1e9:
    #    return 1
    #elif eta < -1e9:
    #    return -1
    #return np.cos(2*np.arctan(np.exp(-eta)))
    #return np.where(np.abs(eta) < 1e3, np.cos(2*np.arctan(np.exp(-eta))), np.sign(eta))
    return np.cos(2*np.arctan(np.exp(-eta)))

#vectorized_get_costheta = np.vectorize(get_costheta)

filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'

thrust_expr = '(MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/((MC_px**2 + MC_py**2 + MC_pz**2)**0.5*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5)'

sigfile = os.path.join(filepath, 'p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu/', '*.root')
bbfile = os.path.join(filepath, 'p8_ee_Zbb_ecm91/', '*.root')

eta_minhemi_nocut = ak.Array([])
eta_maxhemi_nocut = ak.Array([])
eta_totvalu_nocut = ak.Array([])
eta_minhemi_Emcut = ak.Array([])
eta_maxhemi_Emcut = ak.Array([])
eta_totvalu_Emcut = ak.Array([])
eta_minhemi_dEcut = ak.Array([])
eta_maxhemi_dEcut = ak.Array([])
eta_totvalu_dEcut = ak.Array([])

bbeta_minhemi_nocut = np.array([])
bbeta_maxhemi_nocut = np.array([])
bbeta_totvalu_nocut = np.array([])
bbeta_minhemi_Emcut = np.array([])
bbeta_maxhemi_Emcut = np.array([])
bbeta_totvalu_Emcut = np.array([])
bbeta_minhemi_dEcut = np.array([])
bbeta_maxhemi_dEcut = np.array([])
bbeta_totvalu_dEcut = np.array([])

print('Init')
for tree in uproot.iterate(sigfile+':events', 
        expressions=['costheta', 'MC_eta', 'Emin', 'deltaE'],
        aliases={'costheta':thrust_expr, 'Emin':'EVT_Thrust_Emin_e', 'deltaE':'EVT_Thrust_Emax_e - EVT_Thrust_Emin_e'}):
    Emcut = tree[tree['Emin'] < 20]
    dEcut = tree[tree['deltaE'] > 35]

    eta_minhemi_nocut = np.append(eta_minhemi_nocut, ak.ravel(tree['MC_eta'][tree['costheta'] > 0]).to_numpy())
    eta_maxhemi_nocut = np.append(eta_maxhemi_nocut, ak.ravel(tree['MC_eta'][tree['costheta'] < 0]).to_numpy())
    eta_minhemi_Emcut = np.append(eta_minhemi_Emcut, ak.ravel(Emcut['MC_eta'][Emcut['costheta'] > 0]).to_numpy())
    eta_maxhemi_Emcut = np.append(eta_maxhemi_Emcut, ak.ravel(Emcut['MC_eta'][Emcut['costheta'] < 0]).to_numpy())
    eta_minhemi_dEcut = np.append(eta_minhemi_dEcut, ak.ravel(dEcut['MC_eta'][dEcut['costheta'] > 0]).to_numpy())
    eta_maxhemi_dEcut = np.append(eta_maxhemi_dEcut, ak.ravel(dEcut['MC_eta'][dEcut['costheta'] < 0]).to_numpy())

    eta_totvalu_nocut = np.append(eta_totvalu_nocut, ak.ravel(tree['MC_eta']).to_numpy())
    eta_totvalu_Emcut = np.append(eta_totvalu_Emcut, ak.ravel(Emcut['MC_eta']).to_numpy())
    eta_totvalu_dEcut = np.append(eta_totvalu_dEcut, ak.ravel(dEcut['MC_eta']).to_numpy())
    
    print(f'{tree} done')

with uproot.recreate('/r01/lhcb/rrm42/fcc/signal_eta_data.root') as outfile:
    outfile['tree'] = ak.zip({'eta_minhemi_nocut': eta_minhemi_nocut[np.newaxis],
        'eta_maxhemi_nocut': eta_maxhemi_nocut[np.newaxis],
        'eta_minhemi_Emcut': eta_minhemi_Emcut[np.newaxis],
        'eta_maxhemi_Emcut': eta_maxhemi_Emcut[np.newaxis],
        'eta_minhemi_dEcut': eta_minhemi_dEcut[np.newaxis],
        'eta_maxhemi_dEcut': eta_maxhemi_dEcut[np.newaxis],
        'eta_totvalu_nocut': eta_totvalu_nocut[np.newaxis],
        'eta_totvalu_Emcut': eta_totvalu_Emcut[np.newaxis],
        'eta_totvalu_dEcut': eta_totvalu_dEcut[np.newaxis],
        'cos_minhemi_nocut': get_costheta(eta_minhemi_nocut)[np.newaxis],
        'cos_maxhemi_nocut': get_costheta(eta_maxhemi_nocut)[np.newaxis],
        'cos_minhemi_Emcut': get_costheta(eta_minhemi_Emcut)[np.newaxis],
        'cos_maxhemi_Emcut': get_costheta(eta_maxhemi_Emcut)[np.newaxis],
        'cos_minhemi_dEcut': get_costheta(eta_minhemi_dEcut)[np.newaxis],
        'cos_maxhemi_dEcut': get_costheta(eta_maxhemi_dEcut)[np.newaxis],
        'cos_totvalu_nocut': get_costheta(eta_totvalu_nocut)[np.newaxis],
        'cos_totvalu_Emcut': get_costheta(eta_totvalu_Emcut)[np.newaxis],
        'cos_totvalu_dEcut': get_costheta(eta_totvalu_dEcut)[np.newaxis]})

    print(f"{outfile} saved")

for tree in uproot.iterate(bbfile+':events', 
        expressions=['costheta', 'MC_eta', 'Emin', 'deltaE'],
        aliases={'costheta':thrust_expr, 'Emin':'EVT_Thrust_Emin_e', 'deltaE':'EVT_Thrust_Emax_e - EVT_Thrust_Emin_e'}):
    
    Emcut = tree[tree['Emin'] < 20]
    dEcut = tree[tree['deltaE'] > 35]

    bbeta_minhemi_nocut = np.append(bbeta_minhemi_nocut, ak.ravel(tree['MC_eta'][tree['costheta'] > 0]).to_numpy())
    bbeta_maxhemi_nocut = np.append(bbeta_maxhemi_nocut, ak.ravel(tree['MC_eta'][tree['costheta'] < 0]).to_numpy())
    bbeta_minhemi_Emcut = np.append(bbeta_minhemi_Emcut, ak.ravel(Emcut['MC_eta'][Emcut['costheta'] > 0]).to_numpy())
    bbeta_maxhemi_Emcut = np.append(bbeta_maxhemi_Emcut, ak.ravel(Emcut['MC_eta'][Emcut['costheta'] < 0]).to_numpy())
    bbeta_minhemi_dEcut = np.append(bbeta_minhemi_dEcut, ak.ravel(dEcut['MC_eta'][dEcut['costheta'] > 0]).to_numpy())
    bbeta_maxhemi_dEcut = np.append(bbeta_maxhemi_dEcut, ak.ravel(dEcut['MC_eta'][dEcut['costheta'] < 0]).to_numpy())

    bbeta_totvalu_nocut = np.append(bbeta_totvalu_nocut, ak.ravel(tree['MC_eta']).to_numpy())
    bbeta_totvalu_Emcut = np.append(bbeta_totvalu_Emcut, ak.ravel(Emcut['MC_eta']).to_numpy())
    bbeta_totvalu_dEcut = np.append(bbeta_totvalu_dEcut, ak.ravel(dEcut['MC_eta']).to_numpy())
    print(f"{tree} done")

with uproot.recreate('/r01/lhcb/rrm42/fcc/bb_eta_data.root') as outfile:
    outfile['tree'] = ak.zip({'eta_minhemi_nocut': bbeta_minhemi_nocut,
        'eta_maxhemi_nocut': bbeta_maxhemi_nocut,
        'eta_minhemi_Emcut': bbeta_minhemi_Emcut,
        'eta_maxhemi_Emcut': bbeta_maxhemi_Emcut,
        'eta_minhemi_dEcut': bbeta_minhemi_dEcut,
        'eta_maxhemi_dEcut': bbeta_maxhemi_dEcut,
        'eta_totvalu_nocut': bbeta_totvalu_nocut,
        'eta_totvalu_Emcut': bbeta_totvalu_Emcut,
        'eta_totvalu_dEcut': bbeta_totvalu_dEcut,
        'cos_minhemi_nocut': [get_costheta(i) for i in bbeta_minhemi_nocut],
        'cos_maxhemi_nocut': [get_costheta(i) for i in bbeta_maxhemi_nocut],
        'cos_minhemi_Emcut': [get_costheta(i) for i in bbeta_minhemi_Emcut],
        'cos_maxhemi_Emcut': [get_costheta(i) for i in bbeta_maxhemi_Emcut],
        'cos_minhemi_dEcut': [get_costheta(i) for i in bbeta_minhemi_dEcut],
        'cos_maxhemi_dEcut': [get_costheta(i) for i in bbeta_maxhemi_dEcut],
        'cos_totvalu_nocut': [get_costheta(i) for i in bbeta_totvalu_nocut],
        'cos_totvalu_Emcut': [get_costheta(i) for i in bbeta_totvalu_Emcut],
        'cos_totvalu_dEcut': [get_costheta(i) for i in bbeta_totvalu_dEcut]})
    
    print(f"{outfile} saved")

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
        'lw': 3,
        'color': 'green',
        'hatch': '////'}

total_histopts = {
        'stacked': False,
        'histtype': 'step',
        'lw': 2,
        'color': 'red'}

############### Plot without cut
fig, ax = plt.subplots(2, 2, figsize=(12,12))

ax[0, 0].hist(
        x = eta_minhemi_nocut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'Emin hemisphere',
        **min_histopts)

ax[0, 0].hist(
        x = eta_maxhemi_nocut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Emax hemisphere',
        **max_histopts)

ax[0, 0].hist(
        x = eta_totvalu_nocut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Total',
        **total_histopts)

ax[0, 0].set_title(r'Signal $\eta$', fontsize=12)
ax[0, 0].set_xlabel(r'MC\_eta')
ax[0, 0].set_ylabel('Density')
ax[0, 0].legend()
ax[0, 0].tick_params(labelsize=8)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_minhemi_nocut],
        density = True,
        bins=100,
        range=(-1,1),
        label = r'Emin hemisphere',
        **min_histopts)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_maxhemi_nocut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Emax hemisphere',
        **max_histopts)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_totvalu_nocut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Total',
        **total_histopts)

ax[0, 1].set_title(r'Signal $\cos{\theta}$', fontsize=10)
ax[0, 1].set_ylabel('Density')
ax[0, 1].set_xlabel(r'$\cos{\theta}$')
ax[0, 1].tick_params(labelsize=8)
ax[0, 1].legend()

ax[1, 0].hist(
        x = bbeta_minhemi_nocut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'Emin hemisphere',
        **min_histopts)

ax[1, 0].hist(
        x = bbeta_maxhemi_nocut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Emax hemisphere',
        **max_histopts)

ax[1, 0].hist(
        x = bbeta_totvalu_nocut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Total',
        **total_histopts)

ax[1, 0].set_title(r'Background $\eta$', fontsize=10)
ax[1, 0].set_ylabel('Density')
ax[1, 0].set_xlabel('MC\_eta')
ax[1, 0].tick_params(labelsize=8)
ax[1, 0].legend()

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_minhemi_nocut],
        density = True,
        bins=100,
        range=(-1,1),
        label = r'Emin hemisphere',
        **min_histopts)

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_maxhemi_nocut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Emax hemisphere',
        **max_histopts)

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_totvalu_nocut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Total',
        **total_histopts)

ax[1, 1].set_title(r'Background $\cos{\theta}$', fontsize=10)
ax[1, 1].set_ylabel('Density')
ax[1, 1].set_xlabel(r'$\cos{\theta}$')
ax[1, 1].tick_params(labelsize=8)
ax[1, 1].legend()

fig.suptitle(r'Without cut', fontsize=12)
fig.tight_layout()
plt.savefig('/r01/lhcb/rrm42/fcc/eta-theta-nocut.png', dpi=300)
plt.clear()

############### Plot with Emincut
fig, ax = plt.subplots(2, 2, figsize=(12,12))

ax[0, 0].hist(
        x = eta_minhemi_Emcut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'Emin hemisphere',
        **min_histopts)

ax[0, 0].hist(
        x = eta_maxhemi_Emcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Emax hemisphere',
        **max_histopts)

ax[0, 0].hist(
        x = eta_totvalu_Emcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Total',
        **total_histopts)

ax[0, 0].set_title(r'Signal $\eta$', fontsize=12)
ax[0, 0].set_xlabel(r'MC\_eta')
ax[0, 0].set_ylabel('Density')
ax[0, 0].legend()
ax[0, 0].tick_params(labelsize=8)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_minhemi_Emcut],
        density = True,
        bins=100,
        range=(-1,1),
        label = r'Emin hemisphere',
        **min_histopts)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_maxhemi_Emcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Emax hemisphere',
        **max_histopts)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_totvalu_Emcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Total',
        **total_histopts)

ax[0, 1].set_title(r'Signal $\cos{\theta}$', fontsize=10)
ax[0, 1].set_ylabel('Density')
ax[0, 1].set_xlabel(r'$\cos{\theta}$')
ax[0, 1].tick_params(labelsize=8)
ax[0, 1].legend()

ax[1, 0].hist(
        x = bbeta_minhemi_Emcut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'Emin hemisphere',
        **min_histopts)

ax[1, 0].hist(
        x = bbeta_maxhemi_Emcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Emax hemisphere',
        **max_histopts)

ax[1, 0].hist(
        x = bbeta_totvalu_Emcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Total',
        **total_histopts)

ax[1, 0].set_title(r'Background $\eta$', fontsize=10)
ax[1, 0].set_ylabel('Density')
ax[1, 0].set_xlabel('MC\_eta')
ax[1, 0].tick_params(labelsize=8)
ax[1, 0].legend()

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_minhemi_Emcut],
        density = True,
        bins=100,
        range=(-1,1),
        label = r'Emin hemisphere',
        **min_histopts)

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_maxhemi_Emcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Emax hemisphere',
        **max_histopts)

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_totvalu_Emcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Total',
        **total_histopts)

ax[1, 1].set_title(r'Background $\cos{\theta}$', fontsize=10)
ax[1, 1].set_ylabel('Density')
ax[1, 1].set_xlabel(r'$\cos{\theta}$')
ax[1, 1].tick_params(labelsize=8)
ax[1, 1].legend()

fig.suptitle(r'With Emin cut', fontsize=12)
fig.tight_layout()
plt.savefig('/r01/lhcb/rrm42/fcc/eta-theta-Emcut.png', dpi=300)
plt.clear()

############### Plot with deltaE cut
fig, ax = plt.subplots(2, 2, figsize=(12,12))

ax[0, 0].hist(
        x = eta_minhemi_dEcut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'Emin hemisphere',
        **min_histopts)

ax[0, 0].hist(
        x = eta_maxhemi_dEcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Emax hemisphere',
        **max_histopts)

ax[0, 0].hist(
        x = eta_totvalu_dEcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Total',
        **total_histopts)

ax[0, 0].set_title(r'Signal $\eta$', fontsize=12)
ax[0, 0].set_xlabel(r'MC\_eta')
ax[0, 0].set_ylabel('Density')
ax[0, 0].legend()
ax[0, 0].tick_params(labelsize=8)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_minhemi_dEcut],
        density = True,
        bins=100,
        range=(-1,1),
        label = r'Emin hemisphere',
        **min_histopts)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_maxhemi_dEcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Emax hemisphere',
        **max_histopts)

ax[0, 1].hist(
        x = [get_costheta(i) for i in eta_totvalu_dEcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Total',
        **total_histopts)

ax[0, 1].set_title(r'Signal $\cos{\theta}$', fontsize=10)
ax[0, 1].set_ylabel('Density')
ax[0, 1].set_xlabel(r'$\cos{\theta}$')
ax[0, 1].tick_params(labelsize=8)
ax[0, 1].legend()

ax[1, 0].hist(
        x = bbeta_minhemi_dEcut,
        density = True,
        bins=100,
        range=(-6,6),
        label = r'Emin hemisphere',
        **min_histopts)

ax[1, 0].hist(
        x = bbeta_maxhemi_dEcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Emax hemisphere',
        **max_histopts)

ax[1, 0].hist(
        x = bbeta_totvalu_dEcut,
        density=True,
        bins=100,
        range=(-6,6),
        label = r'Total',
        **total_histopts)

ax[1, 0].set_title(r'Background $\eta$', fontsize=10)
ax[1, 0].set_ylabel('Density')
ax[1, 0].set_xlabel('MC\_eta')
ax[1, 0].tick_params(labelsize=8)
ax[1, 0].legend()

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_minhemi_dEcut],
        density = True,
        bins=100,
        range=(-1,1),
        label = r'Emin hemisphere',
        **min_histopts)

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_maxhemi_dEcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Emax hemisphere',
        **max_histopts)

ax[1, 1].hist(
        x = [get_costheta(i) for i in bbeta_totvalu_dEcut],
        density=True,
        bins=100,
        range=(-1,1),
        label = r'Total',
        **total_histopts)

ax[1, 1].set_title(r'Background $\cos{\theta}$', fontsize=10)
ax[1, 1].set_ylabel('Density')
ax[1, 1].set_xlabel(r'$\cos{\theta}$')
ax[1, 1].tick_params(labelsize=8)
ax[1, 1].legend()

fig.suptitle(r'With $\Delta E$ cut', fontsize=12)
fig.tight_layout()
plt.savefig('/r01/lhcb/rrm42/fcc/eta-theta-dEcut.png', dpi=300)

print("Plots saved")
