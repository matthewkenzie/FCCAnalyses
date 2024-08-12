########################################################
# Particle counter but only for background (properly weighted)
########################################################
import os
import uproot
import numpy as np
import awkward as ak
import matplotlib as mpl
import matplotlib.pyplot as plt
import config as cfg

plt.style.use('fcc.mplstyle')

###################### Preliminaries #############################
filepath = '/r01/lhcb/rrm42/fcc/post_stage0/'
files = {'bb' : os.path.join(filepath, 'bb_fromrecp.root'),
         'cc' : os.path.join(filepath, 'cc_fromrecp.root'),
         'ss' : os.path.join(filepath, 'ss_fromrecp.root'),
         'ud' : os.path.join(filepath, 'ud_fromrecp.root')}

expressions = ['pid', 'emin', 'cosTheta']
aliases = {'pid'  : 'Rec_type',
           'cosTheta' : 'Rec_cosrel2thrust',
           'emin' : 'Thrust_Emin'}

bb_frac = 0.1512
cc_frac = 0.1203
ss_frac = 0.1560
ud_frac = 0.1560 + 0.1160

totnum = 500000
nums = {'bb' : round(totnum*bb_frac),
        'cc' : round(totnum*cc_frac),
        'ss' : round(totnum*ss_frac),
        'ud' : round(totnum*ud_frac)}

out = {}

for file in files:
    with uproot.open(files[file]+':events') as tree:
        arrays = uproot.concatenate(tree, expressions=expressions, aliases=aliases)
        out[file] = arrays[:nums[file]]
        print(f"{files[file]} saved")

total = ak.concatenate([out[i] for i in out])
print("Arrays concatenated with correct weight")

###################### Function #############################
def particle_counter(arrays, cut, prefix):
    k = np.array([])
    p = np.array([])
    e = np.array([])
    m = np.array([])
    lep = np.array([])
    
    if cut: 
        # Remove empty events
        temp = arrays[arrays['emin'] < 20]
        if prefix == 'min_':
            nonempty = temp['pid'][(ak.num(temp['pid']) > 0) & (temp['cosTheta'] > 0)]
        elif prefix == 'max_':
            nonempty = temp['pid'][(ak.num(temp['pid']) > 0) & (temp['cosTheta'] < 0)]

        # Particle count with Emin cut
        k = np.append( k , ak.count(nonempty[(nonempty == 321) | (nonempty == 130)], axis=-1).to_numpy() )
        p = np.append( p , ak.count(nonempty[(nonempty == 111) | (nonempty == 211)], axis=-1).to_numpy() )

        e = np.append( e , ak.count(nonempty[nonempty  == 11], axis=-1).to_numpy() )
        m = np.append( m , ak.count(nonempty[nonempty  == 13], axis=-1).to_numpy() )
        
        lep = np.append( lep , e + m )

    else:
        if prefix == 'min_':
            nonempty = arrays['pid'][arrays['cosTheta'] > 0]
        elif prefix == 'max_':
            nonempty = arrays['pid'][arrays['cosTheta'] < 0]

        # Particle count without Emin cut
        k = np.append( k , ak.count(nonempty[(nonempty == 321) | (nonempty == 130)], axis=-1).to_numpy() )
        p = np.append( p , ak.count(nonempty[(nonempty == 111) | (nonempty == 211)], axis=-1).to_numpy() )

        e = np.append( e , ak.count(nonempty[nonempty  == 11], axis=-1).to_numpy() )
        m = np.append( m , ak.count(nonempty[nonempty  == 13], axis=-1).to_numpy() )
        
        lep = np.append( lep , e + m )

    return {prefix+'k' : k, 
            prefix+'p' : p,
            prefix+'e' : e,
            prefix+'m' : m,
            prefix+'lep' : lep}


###################### Usage of function ####################
nocut_min = particle_counter(total, False, 'min_')
print("Minimum hemisphere without cut done")
nocut_max = particle_counter(total, False, 'max_')
print("Maximum hemisphere without cut done")
Emcut_min = particle_counter(total, True,  'min_')
print("Minimum hemisphere with cut done")
Emcut_max = particle_counter(total, True,  'max_')
print("Maximum hemisphere with cut done")


###################### Plotting #############################
titledict = {'k': r"Kaons ($K^0_L$ or $K^\pm$)",
             'p': r"Pions ($\pi^\pm$)",
             'e': r"$e^\pm$",
             'm': r"$\mu^\pm$",
             'lep': r"leptons ($e/\mu$)"}

#min_histopts = {
#        'histtype': 'step',
#        'lw': 2,
#        'color': 'blue'}
#
#max_histopts = {
#        'histtype': 'step',
#        'lw': 1.5,
#        'color': 'red'}
#

bkmin_histopts = {
        'histtype': 'step',
        'lw': 2,
        'color': 'orange'}

bkmax_histopts = {
        'histtype': 'step',
        'lw': 2,
        'ls': '--',
        'color': 'green'}

min_histopts = {
        'histtype': 'step',
        'lw': 2,
        'color': 'red'}

max_histopts = {
        'histtype': 'step',
        'lw': 2,
        'ls': '--',
        'color': 'cornflowerblue'}

for i in titledict:

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    _, bins, _ = ax1.hist(x = nocut_max['max_'+i],
                          bins = np.arange(min(nocut_max['max_'+i]), max(nocut_max['max_'+i]) +1, 1),
                          density = False,
                          label='Emax hemisphere',
                          **max_histopts)

    ax1.hist(x = nocut_min['min_'+i],
             bins = bins,
             density = False,
             label='Emin hemisphere',
             **min_histopts)

    ax1.set_xlabel("Count")
    ax1.set_ylabel("Occurrences")
    ax1.set_title("No cut")
    ax1.tick_params(axis='both', labelsize=10)
    ax1.legend(loc = 'best')

    ax2.hist(x = Emcut_max['max_'+i],
             bins = bins,
             density = False,
             label='Emax hemisphere',
             **max_histopts)

    ax2.hist(x = Emcut_min['min_'+i],
             bins = bins,
             density = False,
             label='Emin hemisphere',
             **min_histopts)

    ax2.set_xlabel("Count")
    ax2.set_ylabel("Occurrences")
    ax2.set_title(r"With Emin cut")
    ax2.tick_params(axis='both', labelsize=10)
    ax2.legend(loc='best')

    fig.suptitle(f"Correctly weighted background, {titledict[i]}", fontsize=14)

    plt.savefig(f'/usera/rrm42/private/{i}.pdf')
    print(f"/usera/rrm42/private/{i}.pdf saved")
