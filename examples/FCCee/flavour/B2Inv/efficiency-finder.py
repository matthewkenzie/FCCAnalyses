import os
import sys
from glob import glob
from argparse import ArgumentParser

import uproot
import awkward as ak
import numpy as np

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
    chunks = {sample: int(args.nchunks[i]) for i, sample in enumerate(cfg.samples)}

for sample in cfg.samples:
    path = os.path.join(args.inputpath, sample, '*.root')
    files = glob(path)
    before = 0
    after = 0

    if args.nchunks is not None:
        files = files[:chunks[sample]]

    for file in files:
        with uproot.open(file) as f:
            before += int(f['eventsSelected'])

            arr = f['events'].arrays('Rec_n', cut=args.cut)
            after += len(arr)

    print(f'{sample}:')
    print(f'        n_events before cut = {before}')
    print(f'        n_events after  cut = {after}')
    print(f'        Cut efficiency      = {100*after/before:.3f}%')
    print('\n\n')
