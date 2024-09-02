import os
import sys
from glob import glob
from argparse import ArgumentParser

import uproot
import awkward as ak
import numpy as np

import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = True

import config as cfg

parser = ArgumentParser()
parser.add_argument("--cut",       type=str, required=True, help='Cut expression to pass to uproot')
parser.add_argument("--inputpath", type=str, default='/r01/lhcb/rrm42/fcc/stage1_postBDT', help='Path to files containing cfg.samples')
parser.add_argument("--nchunks",   nargs='*', default=None, help='Number of chunks to run over')
args = parser.parse_args()

print('Initialising...')
print(f'Using {args.inputpath} with cut {args.cut}')
print(f"{30*'-'}")

if args.nchunks is not None:
    if len(args.nchunks) == 1:
        chunks = {sample: int(args.nchunks) for sample in cfg.samples}
    else:
        chunks = {sample: int(args.nchunks[i]) for i, sample in enumerate(cfg.samples)}

data = {sample: np.array([]) for sample in cfg.samples}
eff = {sample: 0 for sample in cfg.samples}

for sample in cfg.samples:
    path = os.path.join(args.inputpath, sample, '*.root')
    files = glob(path)
    proc = 0
    sel  = 0

    if args.nchunks is not None:
        files = files[:chunks[sample]]

    for file in files:
        with uproot.open(file) as f:
            temp = f['events'].arrays('45.5 - EVT_hemisEmin_e', cut=args.cut, library='np')['45.5 - EVT_hemisEmin_e']
            proc += int(f['eventsSelected'])
            sel += len(temp)
            data[sample] = np.append(data[sample], temp)

    eff[sample] = sel/proc

N_Z = 6e12
weights = {sample: 0 for sample in cfg.samples}
N_tot = 0
for sample in cfg.samples:
    if sample in cfg.sample_allocations['signal']:
        weights[sample] = N_Z*cfg.branching_fractions['p8_ee_Zbb_ecm91'][0]*2*cfg.prod_frac['Bs']*1e-6*cfg.efficiencies['presel+bdt1>0.9+oneCharged'][sample]*eff[sample]
        N_tot += weights[sample]
    else:
        weights[sample] = N_Z*cfg.branching_fractions[sample][0]*cfg.efficiencies['presel+bdt1>0.9+oneCharged'][sample]*eff[sample]
        N_tot += weights[sample]

print(weights)
#weights = {sample: weights[sample]/N_tot for sample in cfg.samples}
#print("Signal events surviving = ", weights['p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu']*N_tot)

fig, ax = plt.subplots()
ax.set_yscale('log')
bins = 100
for sample in cfg.samples:
    ax.hist(data[sample], bins=bins, weights=weights[sample]*np.ones_like(data[sample])/len(data[sample]), histtype='step', label=cfg.titles[sample])

ax.legend()
plt.savefig('/usera/rrm42/private/test.png')
plt.show()
