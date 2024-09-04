import os
import sys
from glob import glob
from argparse import ArgumentParser

import uproot
import awkward as ak
import pandas as pd

import config as cfg
from time import time

parser = ArgumentParser()
parser.add_argument("--cut", type=str, required=True, help='Cut expression to pass to uproot')
parser.add_argument("--input", required=True, choices = ["stage1_training", "stage1", "stage2_training", "stage2", "custom"], help='Sample collection to use, if custom needs CUSTOMPATH')
parser.add_argument("--nchunks",   nargs='*', default=None, help='Number of chunks to run over')
parser.add_argument("--raw",  default=False, action="store_const", const=True, help='Use `eventsProcessed` instead of `eventsSelected` to calculate efficiency')
parser.add_argument("--custompath", type=str, required=False, default=None, help='Path used if --input is set to custom, default=None')
parser.add_argument("--save", type=str, required=False, default=None, help='Save efficiencies to a csv file with the given path')
args = parser.parse_args()

start = time()
print(f"\n{30*'-'}")
print(f"EFFICIENCY CALCULATOR")
print(f"{30*'-'}\n")
print("Initialising...")
if (args.input == 'custom') and not(os.path.exists(args.custompath)):
    raise ValueError(f'{custompath} does not exist')
if args.input != 'custom':
    inputpath = cfg.fccana_opts['outputDir'][args.input]
    print(f'Using files from {inputpath} with cut {args.cut}')
else:
    inputpath = args.custompath
    print(f'Using files from {inputpath} with cut {args.cut}')
if args.raw:
    print('Showing TOTAL efficiency (including preselection cuts)')
else:
    print(f'Showing efficiency post tupling in {inputpath}')
print(f"{30*'-'}")

if args.nchunks is not None:
    if len(args.nchunks) == 1:
        chunks = {sample: int(args.nchunks[0]) for sample in cfg.samples}
    elif len(args.nchunks) == len(cfg.samples):
        chunks = {sample: int(args.nchunks[i]) for i, sample in enumerate(cfg.samples)}
else:
    print(f"args.nchunks = {args.nchunks} is either null or invalid, using all files")

if args.save is not None:
    data = {}
for sample in cfg.samples:
    path = os.path.join(inputpath, sample, '*.root')
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

            arr = f['events'].arrays('Rec_n', cut=args.cut) # Placeholder column to find the efficiency
            after += len(arr)

    if args.save is not None:
        data[sample] = after/before

    print(f'{sample}:')
    print(f'        n_events before cut = {before}')
    print(f'        n_events after  cut = {after}')
    print(f'        Cut efficiency      = {after/before:.4e}\n')

if args.save is not None:
    pd.DataFrame(data, index=[f'{args.cut}'], columns=cfg.samples).to_csv(args.save, columns=cfg.samples)
    print(f'Efficiencies saved to {args.save}')
end = time()
exec_time = end - start
hours, rem = divmod(exec_time, 3600)
minutes, sec = divmod(exec_time, 60)
print(f"{30*'-'}")
print(f"Execution time in H:M:S = {int(hours):02}:{int(minutes):02}:{sec:.3f}")
print(f"{30*'-'}")
