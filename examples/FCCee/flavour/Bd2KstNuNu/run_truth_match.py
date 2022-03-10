import ROOT as r
from tqdm import tqdm
import array

import uproot
import numpy as np

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-i','--input',required=True,type=str)
parser.add_argument('-o','--output',required=True,type=str)
parser.add_argument('-n','--nevents',default=-1,type=int)
args = parser.parse_args()

tf = r.TFile(args.input)
tree = tf.Get("events")
#tree.SetBranchStatus("*",0)
#tree.SetBranchStatus("EVT*",1)
#tree.SetBranchStatus("KPiCandidates*",1)

#print('Setup')
#newf = r.TFile('match-test.root','RECREATE')
#newt = tree.CloneTree(0)

#tree.SetBranchStatus("*",1)

#matched = array.array('b',[0])
#h1_e = array.array('f',[0])
#h2_e = array.array('f',[0])
#h1true_e = array.array('f',[0])
#h2true_e = array.array('f',[0])
#h1true_pdg = array.array('i',[0])
#h2true_pdg = array.array('i',[0])

#newt.Branch("matched", matched, "matched/O")
#newt.Branch("KPiCandidates_h1e", h1_e, "KPiCandidates_h1e/F")
#newt.Branch("KPiCandidates_h2e", h2_e, "KPiCandidates_h2e/F")
#newt.Branch("KPiCandidates_h1true_e", h1true_e, "KPiCandidates_h1true_e/F")
#newt.Branch("KPiCandidates_h2true_e", h2true_e, "KPiCandidates_h2true_e/F")
#newt.Branch("KPiCandidates_h1true_pdg", h1true_pdg, "KPiCandidates_h1true_pdg/I")
#newt.Branch("KPiCandidates_h2true_pdg", h2true_pdg, "KPiCandidates_h2true_pdg/I")

evs = tree.GetEntries() if args.nevents<0 else args.nevents

#evs = 10000

truth_gd1_ind = []
truth_gd2_ind = []
truth_gd1_pdg = []
truth_gd2_pdg = []
truth_gd1_e = []
truth_gd2_e = []

print('Truth matching tree', tf.GetName())

for ev in tqdm(range(evs)):
    tree.GetEntry(ev)

    #matched[0] = False
    
    gd1_pdg = 0
    gd2_pdg = 0
    gd1_ind = -1
    gd2_ind = -1

    for i in range( tree.MC_n ):
        if abs(int(tree.MC_PDG[i]))!=511:
            continue

        m_ind = i
        m_pdg = int(tree.MC_PDG[i])

        d1_ind = tree.MC_D1[i]
        d2_ind = tree.MC_D2[i]
        d1_pdg = int(tree.MC_PDG[d1_ind])
        d2_pdg = int(tree.MC_PDG[d2_ind])

        if abs(d1_pdg)!=313 and abs(d2_pdg)!=313:
            continue
        
        if abs(d1_pdg)==313:
            gd1_ind = int(tree.MC_D1[d1_ind])
            gd2_ind = int(tree.MC_D2[d1_ind])
            gd1_pdg = int(tree.MC_PDG[gd1_ind])
            gd2_pdg = int(tree.MC_PDG[gd2_ind])
            gd1_e = tree.MC_e[gd1_ind]
            gd2_e = tree.MC_e[gd2_ind]

        elif abs(d2_pdg)==313:
            gd1_ind = int(tree.MC_D1[d2_ind])
            gd2_ind = int(tree.MC_D2[d2_ind])
            gd1_pdg = int(tree.MC_PDG[gd1_ind])
            gd2_pdg = int(tree.MC_PDG[gd2_ind])
            gd1_e = tree.MC_e[gd1_ind]
            gd2_e = tree.MC_e[gd2_ind]

    truth_gd1_ind.append( gd1_ind )
    truth_gd2_ind.append( gd2_ind )
    truth_gd1_e.append( gd1_e )
    truth_gd2_e.append( gd2_e )
    truth_gd1_pdg.append( gd1_pdg )
    truth_gd2_pdg.append( gd2_pdg )

    #h1_pdg = int(tree.KPiCandidates_h1type[0]) * int(tree.KPiCandidates_h1q[0])
    #h2_pdg = int(tree.KPiCandidates_h2type[0]) * int(tree.KPiCandidates_h2q[0])
    
    #h1true_ind = gd1_ind #if (gd1_pdg*h1_pdg)>0 else gd2_ind
    #h2true_ind = gd2_ind #if (gd2_pdg*h2_pdg)>0 else gd1_ind

    #if h1_pdg*int(tree.MC_PDG[h1true_ind])<0: 
        #h1true_ind = gd2_ind
        #h2true_ind = gd1_ind

    #h1_e[0] = ( tree.KPiCandidates_h1p[0]**2 + tree.KPiCandidates_h1m[0]**2 ) ** 0.5
    #h2_e[0] = ( tree.KPiCandidates_h2p[0]**2 + tree.KPiCandidates_h2m[0]**2 ) ** 0.5

    #h1true_e[0] = tree.MC_e[h1true_ind]
    #h2true_e[0] = tree.MC_e[h2true_ind]

    #h1true_pdg[0] = int(tree.MC_PDG[h1true_ind])
    #h2true_pdg[0] = int(tree.MC_PDG[h2true_ind])


    #if (h1_pdg==h1true_pdg[0]) and (h2_pdg==h2true_pdg[0]) and abs(1-h1_e[0]/h1true_e[0])<0.1 and abs(1-h2_e[0]/h2true_e[0])<0.1:
        #matched[0] = True
        ##print( ev, tree.KPiCandidates_mass[0], h1_pdg, h2_pdg, h1true_pdg[0], h2true_pdg[0], h1_e[0], h2_e[0], h1true_e[0], h2true_e[0] )
        #newt.Fill()

    #if (ev%100==0):
        #input()



tf.Close()
#newt.Write()
#newf.Close()

print('Read/write match tree')
tree = uproot.open(args.input+":events")

keys = tree.keys()
save = []
for key in keys:
    if key.startswith('EVT_') or key.startswith('KPiCandidates'):
        save.append(key)

##simps = ['KPiCandidates_mass', 'KPiCandidates_h1q','KPiCandidates_h2q','KPiCandidates_h1type','KPiCandidates_h2type','KPiCandidates_h1p','KPiCandidates_h2p','KPiCandidates_h1m','KPiCandidates_h2m']

df = tree.arrays(save, library='pd', entry_stop=evs)

df['KPiCandidates_h1type'] = df['KPiCandidates_h1q'] * df['KPiCandidates_h1type']
df['KPiCandidates_h2type'] = df['KPiCandidates_h2q'] * df['KPiCandidates_h2type']
df['KPiCandidates_h1e'] = ( df['KPiCandidates_h1p']**2 + df['KPiCandidates_h1m']**2 ) **0.5
df['KPiCandidates_h2e'] = ( df['KPiCandidates_h2p']**2 + df['KPiCandidates_h2m']**2 ) **0.5

h1true_pdg = np.array( [ truth_gd1_pdg[i] for i in list(df.index.get_level_values('entry')) ] )
h2true_pdg = np.array( [ truth_gd2_pdg[i] for i in list(df.index.get_level_values('entry')) ] )
h1true_e = np.array( [ truth_gd1_e[i] for i in list(df.index.get_level_values('entry')) ] )
h2true_e = np.array( [ truth_gd2_e[i] for i in list(df.index.get_level_values('entry')) ] )
h1true_ind = np.array( [ truth_gd1_ind[i] for i in list(df.index.get_level_values('entry')) ] )
h2true_ind = np.array( [ truth_gd2_ind[i] for i in list(df.index.get_level_values('entry')) ] )

pos = np.where( h1true_pdg>0, h1true_pdg, h2true_pdg )
neg = np.where( h1true_pdg<0, h1true_pdg, h2true_pdg )

pos_e = np.where( h1true_pdg>0, h1true_e, h2true_e )
neg_e = np.where( h1true_pdg<0, h1true_e, h2true_e )

pos_ind = np.where( h1true_pdg>0, h1true_ind, h2true_ind )
neg_ind = np.where( h1true_pdg<0, h1true_ind, h2true_ind )

df['KPiCandidates_h1true_pdg'] = np.where( df['KPiCandidates_h1type']>0,pos,neg )
df['KPiCandidates_h2true_pdg'] = np.where( df['KPiCandidates_h2type']>0,pos,neg )
df['KPiCandidates_h1true_e'] = np.where( df['KPiCandidates_h1type']>0,pos_e,neg_e )
df['KPiCandidates_h2true_e'] = np.where( df['KPiCandidates_h2type']>0,pos_e,neg_e )
df['KPiCandidates_h1true_ind'] = np.where( df['KPiCandidates_h1type']>0,pos_ind,neg_ind )
df['KPiCandidates_h2true_ind'] = np.where( df['KPiCandidates_h2type']>0,pos_ind,neg_ind )

matched = df[ (df['KPiCandidates_h1true_pdg']==df['KPiCandidates_h1type']) & (df['KPiCandidates_h2true_pdg']==df['KPiCandidates_h2type']) ]
matched = matched[(abs(matched['KPiCandidates_h1e']/matched['KPiCandidates_h1true_e']-1)<0.1)]

matched.to_pickle(args.output)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6,4))
ax.hist( df['KPiCandidates_mass'], bins=100, range=(0.5,2), density=True, histtype='step', label='Nominal' )
ax.hist( matched['KPiCandidates_mass'], bins=100, range=(0.5,2), density=True, histtype='step', label='Truth Matched' )
ax.set_xlabel('$m(K^+\pi^-) [GeV]$')
ax.legend()
fig.tight_layout()
fig.savefig('test.pdf')

#print(df)
#print(matched)
#plt.show()

#tree = uproot.open("/eos/experiment/fcc/ee/analyses/case-studies/flavour/Bd2KstNuNu/flatNtuples/spring2022/prod_01/Batch_Training_4stage1/p8_ee_Zbb_ecm91_EvtGen_Bd2KstNuNu/p8_ee_Zbb_ecm91_EvtGen_Bd2KstNuNu_chunk1.root:events")
