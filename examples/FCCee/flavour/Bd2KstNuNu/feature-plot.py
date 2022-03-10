import uproot
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd

basepath = '/eos/experiment/fcc/ee/analyses/case-studies/flavour/Bd2KstNuNu/flatNtuples/spring2022/prod_01/Batch_Training_4stage1'

channel = 'Bd2KstNuNu'
os.system(f'mkdir -p plots/{channel}')

files = { 'signal'  : f'p8_ee_Zbb_ecm91_EvtGen_Bd2KstNuNu',
          'bb_inc'  : f'p8_ee_Zbb_ecm91',
          'cc_inc'  : f'p8_ee_Zcc_ecm91',
          'uds_inc' : f'p8_ee_Zuds_ecm91'
        }
titles = { 'signal'  : r'$B^0 \rightarrow K^{*0} \nu\bar{\nu}$',
           'bb_inc'  : r'Inclusive $Z^0 \to b\bar{b}$',
           'cc_inc'  : r'Inclusive $Z^0 \to c\bar{c}$',
           'uds_inc' : r'Inclusive $Z^0 \to q\bar{q}$'
         }

plot_vars = {
            'EVT_ThrustEdiff_E'         : [r'$E^{\rm{diff}}$ [GeV]', 50, (0, 40)],
            'EVT_ThrustEmax_E'          : [r'$E^{\rm{max}}$ [GeV]', 50, (20, 60)],
            'EVT_ThrustEmin_E'          : [r'$E^{\rm{min}}$ [GeV]', 50, (0, 50)],
            'EVT_ThrustEdiff_Echarged'  : [r'$E^{\rm{diff}}_{c}$ [GeV]',50, (-40, 40),],
            'EVT_ThrustEmax_Echarged'   : [r'$E^{\rm{max}}_{c}$ [GeV]', 50, (0, 60)],
            'EVT_ThrustEmin_Echarged'   : [r'$E^{\rm{min}}_{c}$ [GeV]', 50, (0, 50)],
            'EVT_ThrustEdiff_Eneutral'  : [r'$E^{\rm{diff}}_{n}$ [GeV]', 50, (-40, 40)],
            'EVT_ThrustEmax_Eneutral'   : [r'$E^{\rm{max}}_{n}$ [GeV]', 50, (0, 50)],
            'EVT_ThrustEmin_Eneutral'   : [r'$E^{\rm{min}}_{n}$ [GeV]', 50, (0, 40)],
            'EVT_ThrustEmax_N'          : [r'$M^{\rm{max}}$', 40, (0, 40)],
            'EVT_ThrustEmin_N'          : [r'$M^{\rm{min}}$', 35, (0, 35)],
            'EVT_ThrustEmax_Ncharged'   : [r'$M^{\rm{max}}_{c}$', 25, (0, 25)],
            'EVT_ThrustEmin_Ncharged'   : [r'$M^{\rm{min}}_{c}$', 25, (0, 25)],
            'EVT_ThrustEmax_Nneutral'   : [r'$M^{\rm{max}}_{n}$', 20, (0, 20)],
            'EVT_ThrustEmin_Nneutral'   : [r'$M^{\rm{min}}_{n}$', 20, (0, 20)],
            'KPiCandidates_mass'        : [r'$m(K^+\pi^-)$ [GeV]', 50, (0.5, 1.8)],
            'KPiCandidates_B'           : [r'$\sum E$ [GeV]', 50, (0, 100)]
            }

dfs = {}

for key, fname in files.items():
    path = os.path.join(basepath,fname+'/*.root')
    matched = os.path.join(basepath,fname+'/*_matched.pkl')
    rfiles = glob.glob(path)
    mfiles = glob.glob(matched)
    files = mfiles[:4] if len(mfiles)>0 else rfiles
    for file in files[:1]:
        df = None
        if '_matched.pkl' in file:
            df = pd.read_pickle(file)
        else:
            tr = uproot.open(file+':events')
            branches = tr.keys()
            keep_brs = [ br for br in branches if ( br.startswith('EVT') or br.startswith('KPi') ) ]
            df = tr.arrays(keep_brs, library='pd',entry_stop=None)
        if df is None:
            continue
        if key in dfs.keys():
            dfs[key].append( df, ignore_index=True )
        else:
            dfs[key] = df
    print(dfs[key])
    dfs[key]['EVT_ThrustEdiff_E'] = dfs[key]['EVT_ThrustEmax_E'] - dfs[key]['EVT_ThrustEmin_E']
    dfs[key]['EVT_ThrustEdiff_Echarged'] = dfs[key]['EVT_ThrustEmax_Echarged'] - dfs[key]['EVT_ThrustEmin_Echarged']
    dfs[key]['EVT_ThrustEdiff_Eneutral'] = dfs[key]['EVT_ThrustEmax_Eneutral'] - dfs[key]['EVT_ThrustEmin_Eneutral']
    dfs[key]['EVT_ThrustEdiff_N'] = dfs[key]['EVT_ThrustEmax_N'] - dfs[key]['EVT_ThrustEmin_N']

  #tr = uproot.open(fname+':events')
  #dfs[key] = tr.arrays(filter_name='EVT_*', library='pd')

for var, cfg in plot_vars.items():
    fig, ax = plt.subplots(figsize=(6,4))
    range = None
    bins = 50
    xlabel = var
    if len(cfg)>0: xlabel = cfg[0]
    if len(cfg)>1: bins = cfg[1]
    if len(cfg)>2: range = cfg[2]
    for i, (key, df) in enumerate(dfs.items()):
        ax.hist( df[var], bins=bins, range=range, ec=f'C{i}', histtype='step', label=titles[key], density=True )
    ax.legend()
    ax.set_xlabel(xlabel)
    fig.tight_layout()
    fig.savefig(f'plots/{channel}/{var}.pdf')

#for var in dfs['signal'].columns:
  #plt.clf()
  #for i, (key, df) in enumerate(dfs.items()):
    #plt.hist( df[var], bins=100, ec=f'C{i}', fc=f'C{i}', alpha=0.2, label=key, density=True )

  #plt.legend()
  #plt.xlabel(var)
  #plt.savefig(f'plots/{channel}/{var}.png')


# get the badgers nearest 892
#df.loc[abs(df['KPiCandidates_mass']-0.89167).groupby(level='entry').idxmin()]

# add vertex distance
#for ev, subev in zip(evs,subevs):
     #vind = int(kpdf.loc[ev,subev]['KPiCandidates_vertex'])
     #vtx = vdf.loc[ev,vind]['Vertex_d2PV']
     #vtxs.append(vtx)
