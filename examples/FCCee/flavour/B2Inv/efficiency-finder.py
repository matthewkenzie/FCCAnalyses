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
parser.add_argument("--raw",  default=False, action="store_const", const=True, help='Use `eventsProcessed` instead of `eventsSelected` to calculate efficiency')
args = parser.parse_args()

print('Initialising...')
print(f'Using {args.inputpath} with cut {args.cut}')
if args.raw:
    print('Showing TOTAL efficiency (including preselection cuts etc.)')
else:
    print(f'Showing efficiency post tupling in {args.inputpath}')
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
            if args.raw:
                before += int(f['eventsProcessed'])
            else:
                before += int(f['eventsSelected'])

            arr = f['events'].arrays('Rec_n', cut=args.cut)
            after += len(arr)

    print(f'{sample}:')
    print(f'        n_events before cut = {before}')
    print(f'        n_events after  cut = {after}')
    print(f'        Cut efficiency      = {after/before:.4e}')
    print('\n\n')
