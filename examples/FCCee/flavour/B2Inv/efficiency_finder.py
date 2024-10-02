# efficiency_finder.py - must be in the same directory as config.py
# Contains functions to get efficiences with errors
# Functions:
#     - efficiency_calc  : Calculate efficiency and error
#     - get_efficiencies : Get efficiencies for samples with various options
# Run `python efficiency_finder.py --help` for more information
import os

import uproot
import numpy as np
import pandas as pd

from glob import glob
from time import time
from datetime import timedelta

import config as cfg


def efficiency_calc(before, after):
    '''
    Function that calculates the efficiency and error given the number of events before and after the selection

    Parameters
    ----------
    before: int or ndarray, required
        The number (or an array of numbers) of events before the selection.
    after: int or ndarray, required
        The number (or an array of numbers) of events that pass the selection.
        Must have the same dimensions as `before`

    Returns
    -------
    mode: int or ndarray
        The selection efficiency, after/before
    error: int or ndarray
        The error in the efficiency, assuming a binomial distribution of acceptance/rejection.
        See <https://indico.cern.ch/event/66256/contributions/2071577/attachments/1017176/1447814/EfficiencyErrors.pdf>
    '''
    mode = after/before
    # Variance in an efficiency k/n is (k+1)(k+2)/(n+2)(n+3) - (k+1)^2/(n+2)^2
    var = ((after+1)*(after+2))/((before+2)*(before+3)) - ((after+1)/(before+2))**2
    error = np.sqrt(var)

    return mode, error

def get_efficiencies(inputtype, 
                     further_analysis=True,
                     samples=None,
                     cut=None,
                     nchunks=None,
                     raw=False,
                     custompath=None,
                     save=None,
                     verbose=True):
    '''
    Function to print, save or return efficiencies of given samples with a given cut string.

    Parameters
    ----------
    inputtype: str, required
        Choose one of `stage1_training`, `stage1`, `stage2_training` or `stage2` to use from config. To use a custom path pass `custom` with a valid `custompath`.
    further_analysis: bool, optional
        If True, a dictionary of type {sample: (efficiency, error)} is returned, where sample belongs to the specified samples (or default config.samples). Default = True.
    samples: list of str, optional
        Samples for which the efficiencies are calculated, must be a subset of config.samples. Default = None (all config.samples used).
    cut: str, optional
        Valid ROOT expression to pass to uproot as an additional cut. Default = None.
    nchunks: int or list of ints, optional
        The number of files to use for each sample. Either a single int used for all or a list with corresponding values.
        If the length of this list is longer than the length of samples, the first elements are used. Default = None (all files used)
    raw: bool, optional
        If True and cut is provided, use the eventsProcessed TParameter, otherwise use eventsSelected. Default = False.
    custompath: str, optional
        Path to the samples. Required if inputtype is set to 'custom'. Default = None.
    save: str, optional
        Path to a csv file to store the efficiencies. Default = None.
    verbose: bool, optional
        Print messages in stdout as the function is running. Default = True.
    shorthand: bool, optional
        Use shorthands defined in config.sample_shorthand instead of the full name from config.samples.
        ONLY RENAMES THE COLUMNS IN THE OUTPUT CSV

    Returns
    -------
    If further_analysis is True,
    data: dict
        Dictionary with efficiencies and their Bayesian errors for each sample.
        data[sample][0] : efficiency for sample
        data[sample][1] : Bayesian error in the efficiency
    '''

    ##############################
    ## INITIALISATION
    ##############################
    if verbose:
        start = time()
        print(f"\n{30*'-'}")
        print(f"EFFICIENCY CALCULATOR")
        print(f"{30*'-'}\n")
        print("Initialising...")

    # Set inputpath
    if (inputtype == 'custom') and (custompath is None):
        raise ValueError(f"{custompath} custompath incompatible with `inputtype` == {inputtype}")
    elif (inputtype == 'custom') and not os.path.exists(custompath):
        raise ValueError(f"{custompath} invalid or does not exist")
    elif inputtype not in ['stage1_training', 'stage1', 'stage2_training', 'stage2', 'custom']:
        raise ValueError(f"`inputtype` must be one of ['stage1_training', 'stage1', 'stage2_training', 'stage2', 'custom']")

    inputpath = cfg.fccana_opts['outputDir'][inputtype] if inputtype != 'custom' else custompath

    if verbose:
        print(f"----> INFO: Using files from:")
        print(f"{15*' '}{inputpath}")
        print(f"----> INFO: With cut {cut}")

        if (cut is not None) and raw:
            print(f"----> INFO: Calculating TOTAL efficiency (from eventsProcessed)")
        elif (cut is not None):
            print(f"----> INFO: Calculating post tupling efficiency (from eventsSelected)")
        else:
            print(f"----> INFO: Cut is not set, calculating tupling efficiency")
        print(f"\n{30*'-'}\n")

    # Define the samples from inputpath for which efficiency is calculated
    try:
        filepaths = {sample: os.path.join(inputpath, sample) for sample in samples}
        if verbose:
            print(f"----> INFO: Finding efficiency for")
            print(f"{15*' '}{samples}")
    except:
        filepaths = {sample: os.path.join(inputpath, sample) for sample in cfg.samples}
        samples = cfg.samples
        if verbose:
            print(f"----> INFO: `samples` either 'all' or invalid, using all config.samples")

    # Define the number of files for each sample from which the efficiency is calculated
    try:
        # Length of samples is correct
        files = {sample: glob(os.path.join(filepaths[sample], '*.root'))[:nchunks[i]] for i, sample in enumerate(filepaths)}
        if verbose:
            print(f"----> INFO: Using {nchunks} files from each sample respectively")
    except:
        try:
            # nchunks has a single element
            files = {sample: glob(os.path.join(filepaths[sample], '*.root'))[:nchunks[0]] for sample in samples}
            if verbose:
                print(f"----> INFO: Using {nchunks[0]} files from each sample")
        except:
            try:
                # nchunks is not a list but a single int
                files = {sample: glob(os.path.join(filepaths[sample], '*.root'))[:nchunks] for sample in samples}
                if verbose:
                    print(f"----> INFO: Using {nchunks} files from each sample")
            except:
                # None of these methods worked
                files = {sample: glob(os.path.join(filepaths[sample], '*.root')) for sample in samples}
                if verbose:
                    print(f"----> INFO: `nchunks` None or invalid, using all files")
    
    # Make a dict of the results if `save` or `further_analysis` options provided
    if (save is not None) or (further_analysis):
        data = {}
    
    ### END of initialisation, namespace contains
    # `samples`: list of sample names to use
    # `files`: dict of list of files for each sample
    # `cut`: Additional cut value
    # `raw`: Whether to use eventsProcessed or eventsSelected in the denominator
    # Optionally, `data`: An empty dictionary that will be filled with the values

    ##############################
    ## CALCULATION
    ##############################
    if verbose:
        print(f"\n{30*'-'}\n")

    for sample in samples:

        if (cut is None) or (isinstance(cut, str)):
            before = 0
            after = 0
        elif isinstance(cut, list):
            before = np.zeros(len(cut))
            after = np.zeros(len(cut))

        for file in files[sample]:
            with uproot.open(file) as f:
                if cut is None:
                    before += int(f['eventsProcessed'])
                    after  += int(f['eventsSelected'])
                else:
                    if raw:
                        before += int(f['eventsProcessed'])
                    else:
                        before += int(f['eventsSelected'])

                    # If cut is a single string
                    if isinstance(cut, str):
                        after += len(f['events'].arrays('Rec_n', cut = cut))  # Placeholder column

                    # If cut is a list of strings, pass each one
                    elif isinstance(cut, list):
                        for i, cut_expr in enumerate(cut):
                            after[i] += len(f['events'].arrays('Rec_n', cut=cut_expr))

        mode, error = efficiency_calc(before, after)

        if (save is not None) or (further_analysis):
            data[sample+'_eff'] = mode
            data[sample+'_err'] = error

        if verbose:
            if (cut is None) or isinstance(cut, str):
                # Try to print by extracting the exponent
                common_div = np.floor(np.log10(mode))
                print(f"{sample} with cut {cut}:")
                print(f"{15*' '}n_events processed = {before}")
                print(f"{15*' '}n_events selected  = {after}")
                print(f"{15*' '}Efficiency         = ({mode/10**common_div:.3f} +/- {error/10**common_div:.3f}) x 10^{int(common_div)}\n")
            elif isinstance(cut, list):
                for i, cut_expr in enumerate(cut):
                    common_div = np.floor(np.log10(mode[i]))
                    print(f"{sample} with cut {cut_expr}:")
                    print(f"{15*' '}n_events before selection = {before[i]}")
                    print(f"{15*' '}n_events after  selection = {after[i]}")
                    print(f"{15*' '}Efficiency         = ({mode[i]/10**common_div:.3f} +/- {error[i]/10**common_div:.3f}) x 10^{int(common_div)}\n")

    ##############################
    ## OUTPUT
    ##############################
    if verbose:
        print(f"\n{30*'-'}\n")
    if save is not None:
        pd.DataFrame(data, index=cut, columns=list(data.keys())).to_csv(save, columns=list(data.keys()))
        if verbose:
            print(f"----> INFO: Efficiencies saved to")
            print(f"{15*' '}{save}")
    elif verbose:
        print(f"----> INFO: `save` is set to None, skipping...")

    if verbose:
        end = time()
        print(f"\n{30*'-'}")
        print(f"Execution time = {timedelta(seconds=end-start)}")
        print(f"{30*'-'}")

    if further_analysis:
        return data


if __name__ == "__main__":
    # If this script is run, i.e. not imported, pass arguments
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Calculates efficiencies of samples based on given cuts')

    inpt = parser.add_argument("--inputtype",  required=True, choices = ["stage1_training", "stage1", "stage2_training", "stage2", "custom"])
    smpl = parser.add_argument("--samples",    default=None,  nargs='*', type=str)
    cutv = parser.add_argument("--cut",        default=None,  type=str)
    ncnk = parser.add_argument("--nchunks",    default=None,  nargs='*', type=int)
    rawv = parser.add_argument("--raw",        default=False, action="store_true")
    cstp = parser.add_argument("--custompath", default=None,  type=str)
    save = parser.add_argument("--save",       default=None,  type=str)

    inpt.help = 'Sample collection to use, if custom needs CUSTOMPATH'
    smpl.help = 'List of samples to use from config.samples, default is None (all config.samples used)'
    cutv.help = 'Cut expression used by uproot, default is None (calculates efficiency of selection cuts when files were generated)'
    ncnk.help = 'Number of chunks to run over, default is None (all files used)'
    rawv.help = 'If `cut` is set, use `eventsProcessed` instead of `eventsSelected`, default is False'
    cstp.help = 'Path to samples if INPUTTYPE is `custom`, default is None'
    save.help = 'Save efficiencies to this csv file, default is None (csv file is not saved)'

    args = parser.parse_args()

    get_efficiencies(args.inputtype, further_analysis=False, samples=args.samples,
                     cut=args.cut, nchunks=args.nchunks, raw=args.raw,
                     custompath=args.custompath, save=args.save, verbose=True)
