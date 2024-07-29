########################################################
# Plots histograms of particle num per event using 'datafromrecp' files
# Produces a plot of: e, mu, tau, kaon, pion count
# As it uses MC PIDs of reconstructed particles, only those are plotted
# For e.g. no K0, only K0L, no pi0, only pi+/-
########################################################
import os
import uproot
import numpy as np
import awkward as ak
import matplotlib as mpl
import matplotlib.pyplot as plt
import config as cfg

plt.style.use('fcc.mplstyle')

def particle_counter(file, Ecut, cosexpr, cut):
    min_k = np.array([])
    min_p = np.array([])
    min_e = np.array([])
    min_m = np.array([])
    min_t = np.array([])
    max_k = np.array([])
    max_p = np.array([])
    max_e = np.array([])
    max_m = np.array([])
    max_t = np.array([])
    min_lep = np.array([])
    max_lep = np.array([])
    
    if cut:

        for datamin in uproot.iterate(file+':events', expressions=['pid'], aliases={'pid':'abs(MC_PDG)'}, cut=f"({Ecut}) & ({cosexpr} > 0)"):
            
            # Remove empty events i.e. [] from data
            nonempty = datamin['pid'][ak.num(datamin['pid']) > 0]

            # Particle count in Emin hemisphere with Emin cut
            min_k = np.append( min_k , ak.count(nonempty[(nonempty == 321) | (nonempty == 130)], axis=-1).to_numpy() )
            min_p = np.append( min_p , ak.count(nonempty[(nonempty == 111) | (nonempty == 211)], axis=-1).to_numpy() )

            min_e = np.append( min_e , ak.count(nonempty[nonempty  == 11], axis=-1).to_numpy() )
            min_m = np.append( min_m , ak.count(nonempty[nonempty  == 13], axis=-1).to_numpy() )
            min_t = np.append( min_t , ak.count(nonempty[nonempty  == 15], axis=-1).to_numpy() )
        
            min_lep = np.append( min_lep , min_e + min_m + min_t )

        for datamax in uproot.iterate(file+':events', expressions=['pid'], aliases={'pid':'abs(MC_PDG)'}, cut=f"({Ecut}) & ({cosexpr} < 0)"):
            
            # Remove empty events i.e. [] from data
            nonempty = datamax['pid'][ak.num(datamax['pid']) > 0]

            # Particle count in Emin hemisphere with Emin cut
            max_k = np.append( max_k , ak.count(nonempty[(nonempty == 321) | (nonempty == 130)], axis=-1).to_numpy() )
            max_p = np.append( max_p , ak.count(nonempty[(nonempty == 111) | (nonempty == 211)], axis=-1).to_numpy() )

            max_e = np.append( max_e , ak.count(nonempty[nonempty  == 11], axis=-1).to_numpy() )
            max_m = np.append( max_m , ak.count(nonempty[nonempty  == 13], axis=-1).to_numpy() )
            max_t = np.append( max_t , ak.count(nonempty[nonempty  == 15], axis=-1).to_numpy() )
        
            max_lep = np.append( max_lep , max_e + max_m + max_t )

    else:
        for datamin in uproot.iterate(file+':events', expressions=['pid'], aliases={'pid':'abs(MC_PDG)'}, cut=f"{cosexpr} > 0"):
            
            # Remove empty events i.e. [] from data
            nonempty = datamin['pid'][ak.num(datamin['pid']) > 0]

            # Particle count in Emin hemisphere with Emin cut
            min_k = np.append( min_k , ak.count(nonempty[(nonempty == 321) | (nonempty == 130)], axis=-1).to_numpy() )
            min_p = np.append( min_p , ak.count(nonempty[(nonempty == 111) | (nonempty == 211)], axis=-1).to_numpy() )

            min_e = np.append( min_e , ak.count(nonempty[nonempty  == 11], axis=-1).to_numpy() )
            min_m = np.append( min_m , ak.count(nonempty[nonempty  == 13], axis=-1).to_numpy() )
            min_t = np.append( min_t , ak.count(nonempty[nonempty  == 15], axis=-1).to_numpy() )
        
            min_lep = np.append( min_lep , min_e + min_m + min_t )

        for datamax in uproot.iterate(file+':events', expressions=['pid'], aliases={'pid':'abs(MC_PDG)'}, cut=f"{cosexpr} < 0"):
            
            # Remove empty events i.e. [] from data
            nonempty = datamax['pid'][ak.num(datamax['pid']) > 0]

            # Particle count in Emin hemisphere with Emin cut
            max_k = np.append( max_k , ak.count(nonempty[(nonempty == 321) | (nonempty == 130)], axis=-1).to_numpy() )
            max_p = np.append( max_p , ak.count(nonempty[(nonempty == 111) | (nonempty == 211)], axis=-1).to_numpy() )

            max_e = np.append( max_e , ak.count(nonempty[nonempty  == 11], axis=-1).to_numpy() )
            max_m = np.append( max_m , ak.count(nonempty[nonempty  == 13], axis=-1).to_numpy() )
            max_t = np.append( max_t , ak.count(nonempty[nonempty  == 15], axis=-1).to_numpy() )
        
            max_lep = np.append( max_lep , max_e + max_m + max_t )

    return {'min_k': min_k, 
            'max_k': max_k, 
            'min_p': min_p, 
            'max_p': max_p, 
            'min_e': min_e, 
            'max_e': max_e, 
            'min_m': min_m, 
            'max_m': max_m, 
            'min_t': min_t, 
            'max_t': max_t, 
            'min_lep': min_lep, 
            'max_lep': max_lep}

# Signal arrays
#filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'
#cosexpr = '(MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/(MC_p*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5)'

filepath = '/r01/lhcb/rrm42/fcc/post_stage0/'
cosexpr = 'MC_cosrel2thrust'
Ecut = 'Thrust_Emin < 20'

sigfile = os.path.join(filepath, 'Bs2NuNu_datafromrecp.root')
sigdict_nocut = particle_counter(sigfile, Ecut, cosexpr, False)
print("Signal files without cut done")
sigdict_Emcut = particle_counter(sigfile, Ecut, cosexpr, True)
print("Signal files with cut done")

bbfile = os.path.join(filepath, 'bb_datafromrecp.root')
bbdict_nocut = particle_counter(bbfile, Ecut, cosexpr, False)
print("Background files without cut done")
bbdict_Emcut = particle_counter(bbfile, Ecut, cosexpr, True)
print("Background files with cut done")


###################### Plotting #############################

titledict = {'k': r"Number of Kaons ($K^0_L$ or $K^\pm$)",
             'p': r"Number of Pions ($\pi^\pm$, no rec $\pi^0$)",
             'e': r"Number of $e^\pm$",
             'm': r"Number of $\mu^\pm$",
             't': r"Number of $\tau^\pm$",
             'lep': r"Total number of charged leptons"}

min_histopts = {
        'histtype': 'step',
        'lw': 2,
        'color': 'blue',
        'hatch': '////'}

max_histopts = {
        'histtype': 'step',
        'lw': 2,
        'color': 'red',
        'hatch': '\\'}

bbmin_histopts = {
        'histtype': 'stepfilled',
        'lw': 1,
        'fill': True,
        'color': 'orange',
        'alpha': 0.4}

bbmax_histopts = {
        'histtype': 'stepfilled',
        'lw': 1,
        'fill': True,
        'color': 'green',
        'alpha': 0.4}

for i in titledict:

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    
    ax[0].hist(
            x = sigdict_nocut['min_'+i],
            bins=np.arange(min(sigdict_nocut['min_'+i]), max(sigdict_nocut['min_'+i]) + 1, 1),
            density = False,
            label = r"$B_s^0 \to \nu\bar{\nu}$: Emin",
            **min_histopts)
    
    ax[0].hist(
            x = sigdict_nocut['max_'+i],
            bins=np.arange(min(sigdict_nocut['max_'+i]), max(sigdict_nocut['max_'+i]) + 1, 1),
            density = False,
            label = r"$B_s^0 \to \nu\bar{\nu}$: Emax",
            **max_histopts)
    
    ax001 = ax[0].twinx()
    ax001.hist(
            x = bbdict_nocut['min_'+i],
            bins=np.arange(min(bbdict_nocut['min_'+i]), max(bbdict_nocut['min_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emin",
            **bbmin_histopts)

    ax001.hist(
            x = bbdict_nocut['max_'+i],
            bins=np.arange(min(bbdict_nocut['max_'+i]), max(bbdict_nocut['max_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emax",
            **bbmax_histopts)

    ax[0].set_ylabel('Signal occurrences')
    ax[0].set_xlabel('Count')
    ax[0].set_title('Without cut')
    ax[0].tick_params(labelsize=8)
    ax[0].legend(loc='upper right')
    ax001.set_ylabel(r'$b\bar{b}$ occurences', color='tab:blue')
    ax001.tick_params(labelsize=8, labelcolor='tab:blue')
    ax001.legend(loc='center right')

    ax[1].hist(
            x = sigdict_Emcut['min_'+i],
            bins=np.arange(min(sigdict_Emcut['min_'+i]), max(sigdict_Emcut['min_'+i]) + 1, 1),
            density = False,
            label = r"$B_s^0 \to \nu\bar{\nu}$: Emin",
            **min_histopts)
    
    ax[1].hist(
            x = sigdict_Emcut['max_'+i],
            bins=np.arange(min(sigdict_Emcut['max_'+i]), max(sigdict_Emcut['max_'+i]) + 1, 1),
            density = False,
            label = r"$B_s^0 \to \nu\bar{\nu}$: Emax",
            **max_histopts)
    
    ax002 = ax[1].twinx()
    ax002.hist(
            x = bbdict_Emcut['min_'+i],
            bins=np.arange(min(bbdict_Emcut['min_'+i]), max(bbdict_Emcut['min_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emin",
            **bbmin_histopts)

    ax002.hist(
            x = bbdict_Emcut['max_'+i],
            bins=np.arange(min(bbdict_Emcut['max_'+i]), max(bbdict_Emcut['max_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emax",
            **bbmax_histopts)

    ax[1].set_ylabel('Signal occurrences')
    ax[1].set_xlabel('Count')
    ax[1].set_title('With Emin cut')
    ax[1].tick_params(labelsize=8)
    ax[1].legend(loc='upper right')
    ax002.set_ylabel(r'$b\bar{b}$ occurrences', color='tab:blue')
    ax002.tick_params(labelsize=8, labelcolor='tab:blue')
    ax002.legend(loc='center right')

    fig.suptitle(titledict[i])
    fig.tight_layout()
    plt.savefig('/r01/lhcb/rrm42/fcc/'+i+'.png', dpi=300)
    print(f"/r01/lhcb/rrm42/fcc/{i}.png plot saved")
