# bdt1_apply.py
# Apply a trained BDT1 model to custom files
import os, sys
sys.path.append('/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv')
import config as cfg

import xgboost as xgb
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Apply an existing BDT1 model to specified files, assumes the model is stored at bdt1out of config and named `tmva1.root`")
    inpt = parser.add_argument("--inputpath",    required=True, type=str)
    ncnk = parser.add_argument("--nchunks",      default=None,  type=int,  nargs='*')
    pltr = parser.add_argument("--plot-results", default=False, action="store_true")
    pltp = parser.add_argument("--plot-outpath", default=None,  type=str)
    bdtc = parser.add_argument("--bdt-cut",      default=None,  type=float)
    othc = parser.add_argument("--other-cut",    default=None,  type=str)

    inpt.help = "Path to the sample ROOT files, must contain directories for each config.samples"
    ncnk.help = "Number of files to use for each sample. If a single value is passed uses this for all samples"]
    pltr.help = "Save plots of the results. `--plot-outpath` is required if this argument is set"
    pltp.help = "Path where the plots are saved, if `--plot-results` is set"
    bdtc.help = "Specify a cut on BDT1 after it is applied. Default = None"
    othc.help = "Specify other cuts to apply AFTER the `--bdt-cut` is applied. Must be a valid ROOT expression. Default = None"


