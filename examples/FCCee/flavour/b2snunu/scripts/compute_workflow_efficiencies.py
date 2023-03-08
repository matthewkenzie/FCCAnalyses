import os
import json
from glob import glob
import ROOT as r

import config as cfg

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-c','--channel', required=True, type=str, help='Decay channel')
parser.add_argument('-e','--evtype', required=True, type=str, help='Event type (e.g. p8_ee_Zbb_ecm91)')
parser.add_argument('-d','--dec'   , required=True, type=str, help='Decay type (e.g. signal / inclusive)')
parser.add_argument('-o','--output', required=True, type=str, help='Output eff file path')
args = parser.parse_args()

####################################
## Load the eos cache which we need
## to look up how many input files
## are used to produce each output
####################################
with open("eos_cache.json") as f:
    fcache = json.load(f)

####################################
## Generated Events
####################################
gen_evs_per_file = cfg.events_per_file[args.channel][args.evtype][args.dec]

####################################
## stage1 and stage 2 efficiencies
####################################
st1_path = f"{cfg.outputs}root/mva_cut/{args.channel}/{args.evtype}/{args.dec}"
st2_path = f"{cfg.outputs}root/mva_st2/{args.channel}/{args.evtype}/{args.dec}"
n_gen_tot = 0
n_proc_st1_tot = 0
n_intree_st1_tot = 0
n_proc_st2_tot = 0
n_intree_st2_tot = 0
# search for stage 1 paths
for fname in glob(f"{st1_path}/*.root"):
    index = os.path.basename(fname).replace('.root','')
    try:
        ind = int(index)
        nfiles = len(fcache[args.channel][args.evtype][args.dec]['samples'][ind])
    except:
        print(f'Error on index {index}')
        continue
    ngen = gen_evs_per_file * nfiles
    tf_st1 = r.TFile(fname)
    evsproc_st1 = tf_st1.Get("eventsProcessed").GetVal()
    evsintree_st1 = tf_st1.Get("events").GetEntries()
    #print(ind, nfiles, evsproc, evsintree)
    n_gen_tot += ngen
    n_proc_st1_tot += evsproc_st1
    n_intree_st1_tot += evsintree_st1
    # look for corresponding stage 2 path
    st2fname = f'{st2_path}/{ind}.root'
    tf_st2 = r.TFile(st2fname)
    evsproc_st2 = tf_st2.Get("eventsProcessed").GetVal()
    evsintree_st2 = tf_st2.Get("events").GetEntries()
    n_proc_st2_tot += evsproc_st2
    n_intree_st2_tot += evsintree_st2
    if evsproc_st2 != evsintree_st1:
        print(f'WARNING: inconsistency in events number for index {ind}')

print('nGenerated: ', n_gen_tot)
print('nProc (st1):', n_proc_st1_tot)
print('nAcc  (st1):', n_intree_st1_tot)
print('nProc (st2):', n_proc_st2_tot)
print('nAcc  (st2):', n_intree_st2_tot)
# this is efficiency up to the files in mva_st2
eff = n_intree_st2_tot / n_gen_tot
print('eff (to st2):', eff )

out_dic = { 'nGen': n_gen_tot,
            'nProc_st1': n_proc_st1_tot,
            'nAcc_st1' : n_intree_st1_tot,
            'nProc_st2': n_proc_st2_tot,
            'nAcc_st2' : n_intree_st2_tot,
            'eff'      : eff
          }

with open(args.output,'w') as f:
    json.dump(out_dic, f, indent=4)
