import os
import uproot
import numpy as np
import awkward as ak
import matplotlib as mpl
import matplotlib.pyplot as plt
import config as cfg

plt.style.use('fcc.mplstyle')

def particle_counter(file, cosexpr, cut):
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
    
    cut_min_k = np.array([])
    cut_min_p = np.array([])
    cut_min_e = np.array([])
    cut_min_m = np.array([])
    cut_min_t = np.array([])
    cut_max_k = np.array([])
    cut_max_p = np.array([])
    cut_max_e = np.array([])
    cut_max_m = np.array([])
    cut_max_t = np.array([])
    cut_min_lep = np.array([])
    cut_max_lep = np.array([])
    
    if cut:

        for data in uproot.iterate(file+':events', expressions=['cos', 'pid', 'Emin'], aliases={'cos':cosexpr, 'Emin':'EVT_Thrust_Emin_e', 'pid':'abs(MC_PDG)'}):
            
            # Particle count with Emin cut
            #min_k = np.append( min_k , ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] > 0) & ((data['pid'] == 311) | (data['pid']) == 321)], axis=-1).to_numpy() )
            #max_k = np.append( max_k , ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] < 0) & ((data['pid'] == 311) | (data['pid']) == 321)], axis=-1).to_numpy() )
            #min_p = np.append( min_p , ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] > 0) & ((data['pid'] == 111) | (data['pid']) == 211)], axis=-1).to_numpy() )
            #max_p = np.append( max_p , ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] < 0) & ((data['pid'] == 111) | (data['pid']) == 121)], axis=-1).to_numpy() )
            min_k = np.append( min_k , 
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] > 0) & (data['pid'] == 311)], axis=-1).to_numpy() + 
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] > 0) & (data['pid'] == 321)], axis=-1).to_numpy() )
            max_k = np.append( max_k , 
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] < 0) & (data['pid'] == 311)], axis=-1).to_numpy() + 
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] < 0) & (data['pid'] == 321)], axis=-1).to_numpy() )
            min_p = np.append( min_p , 
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] > 0) & (data['pid'] == 111)], axis=-1).to_numpy() +
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] > 0) & (data['pid'] == 211)], axis=-1).to_numpy() )
            max_p = np.append( max_p , 
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] < 0) & (data['pid'] == 111)], axis=-1).to_numpy() +
                    ak.count(data['pid'][(data['Emin'] < 20) & (data['cos'] < 0) & (data['pid'] == 211)], axis=-1).to_numpy() )


            min_e = np.append( min_e , ak.count(data['pid'][(data['Emin']  < 20) & (data['cos'] > 0) & (data['pid'] == 11)], axis=-1).to_numpy() )
            max_e = np.append( max_e , ak.count(data['pid'][(data['Emin']  < 20) & (data['cos'] < 0) & (data['pid'] == 11)], axis=-1).to_numpy() )
            min_m = np.append( min_m , ak.count(data['pid'][(data['Emin']  < 20) & (data['cos'] > 0) & (data['pid'] == 13)], axis=-1).to_numpy() )
            max_m = np.append( max_m , ak.count(data['pid'][(data['Emin']  < 20) & (data['cos'] < 0) & (data['pid'] == 13)], axis=-1).to_numpy() ) 
            min_t = np.append( min_t , ak.count(data['pid'][(data['Emin']  < 20) & (data['cos'] > 0) & (data['pid'] == 15)], axis=-1).to_numpy() )
            max_t = np.append( max_t , ak.count(data['pid'][(data['Emin']  < 20) & (data['cos'] < 0) & (data['pid'] == 15)], axis=-1).to_numpy() )
        
            min_lep = np.append( min_lep , min_e + min_m + min_t )
            max_lep = np.append( max_lep , max_e + max_m + max_t )

    else:
        for data in uproot.iterate(file+':events', expressions=['cos', 'pid'], aliases={'cos':cosexpr, 'pid':'abs(MC_PDG)'}):
        
            # Particle count without Emin cut
            #min_k = np.append( min_k , ak.count(data['pid'][(data['cos'] > 0) & ((data['pid'] == 311) | (data['pid']) == 321)], axis=-1).to_numpy() )
            #max_k = np.append( max_k , ak.count(data['pid'][(data['cos'] < 0) & ((data['pid'] == 311) | (data['pid']) == 321)], axis=-1).to_numpy() )
            #min_p = np.append( min_p , ak.count(data['pid'][(data['cos'] > 0) & ((data['pid'] == 111) | (data['pid']) == 211)], axis=-1).to_numpy() )
            #max_p = np.append( max_p , ak.count(data['pid'][(data['cos'] < 0) & ((data['pid'] == 111) | (data['pid']) == 121)], axis=-1).to_numpy() )
            min_k = np.append( min_k , 
                    ak.count(data['pid'][(data['cos'] > 0) & (data['pid'] == 311)], axis=-1).to_numpy() + 
                    ak.count(data['pid'][(data['cos'] > 0) & (data['pid'] == 321)], axis=-1).to_numpy() )
            max_k = np.append( max_k , 
                    ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 311)], axis=-1).to_numpy() + 
                    ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 321)], axis=-1).to_numpy() )
            min_p = np.append( min_p , 
                    ak.count(data['pid'][(data['cos'] > 0) & (data['pid'] == 111)], axis=-1).to_numpy() + 
                    ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 121)], axis=-1).to_numpy() )
            max_p = np.append( max_p , 
                    ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 111)], axis=-1).to_numpy() + 
                    ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 211)], axis=-1).to_numpy() )

            min_e = np.append( min_e , ak.count(data['pid'][(data['cos'] > 0) & (data['pid'] == 11)], axis=-1).to_numpy() )
            max_e = np.append( max_e , ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 11)], axis=-1).to_numpy() )
            min_m = np.append( min_m , ak.count(data['pid'][(data['cos'] > 0) & (data['pid'] == 13)], axis=-1).to_numpy() )
            max_m = np.append( max_m , ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 13)], axis=-1).to_numpy() ) 
            min_t = np.append( min_t , ak.count(data['pid'][(data['cos'] > 0) & (data['pid'] == 15)], axis=-1).to_numpy() )
            max_t = np.append( max_t , ak.count(data['pid'][(data['cos'] < 0) & (data['pid'] == 15)], axis=-1).to_numpy() )
        
            min_lep = np.append( min_lep , min_e + min_m + min_t )
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
filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'
cosexpr = '(MC_px*EVT_Thrust_x + MC_py*EVT_Thrust_y + MC_pz*EVT_Thrust_z)/(MC_p*(EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5)'

sigfile = os.path.join(filepath, cfg.samples[0], '*.root')
sigdict_nocut = particle_counter(sigfile, cosexpr, False)
print("Signal files without cut done")
sigdict_Emcut = particle_counter(sigfile, cosexpr, True)
print("Signal files with cut done")

bbfile = os.path.join(filepath, cfg.samples[1], '*.root')
bbdict_nocut = particle_counter(bbfile, cosexpr, False)
print("Background files without cut done")
bbdict_Emcut = particle_counter(bbfile, cosexpr, True)
print("Background files with cut done")


###################### Plotting #############################

titledict = {'k': r"Number of Kaons ($K^0/\bar{K}^0$ or $K^\pm$)",
             'p': r"Number of Pions ($\pi^0$ or $\pi^\pm$)",
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

    ax[0].hist(
            x = bbdict_nocut['min_'+i],
            bins=np.arange(min(bbdict_nocut['min_'+i]), max(bbdict_nocut['min_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emin",
            **bbmin_histopts)

    ax[0].hist(
            x = bbdict_nocut['max_'+i],
            bins=np.arange(min(bbdict_nocut['max_'+i]), max(bbdict_nocut['max_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emax",
            **bbmax_histopts)

    ax[0].set_ylabel('Total occurrences')
    ax[0].set_xlabel('Count')
    ax[0].set_title('Without cut')
    ax[0].tick_params(labelsize=8)
    ax[0].legend()

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

    ax[1].hist(
            x = bbdict_Emcut['min_'+i],
            bins=np.arange(min(bbdict_Emcut['min_'+i]), max(bbdict_Emcut['min_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emin",
            **bbmin_histopts)

    ax[1].hist(
            x = bbdict_Emcut['max_'+i],
            bins=np.arange(min(bbdict_Emcut['max_'+i]), max(bbdict_Emcut['max_'+i]) + 1, 1),
            density = False,
            label = r"$Z \to b\bar{b}$: Emax",
            **bbmax_histopts)

    ax[1].set_ylabel('Total occurrences')
    ax[1].set_xlabel('Count')
    ax[1].set_title('With Emin cut')
    ax[1].tick_params(labelsize=8)
    ax[1].legend()

    fig.suptitle(titledict[i])
    fig.tight_layout()
    plt.savefig('/r01/lhcb/rrm42/fcc/'+i+'.png', dpi=300)
