import os
from glob import glob
import numpy as np
import uproot
import matplotlib as mpl
import matplotlib.pyplot as plt
import awkward as ak  # Needed if using awkward arrays
plt.style.use('fcc.mplstyle')

# go configure 
import config as cfg

# I'd like to have an argument please
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-i","--inputpath", default="/r01/lhcb/mkenzie/fcc/B2Inv/stage0/", help="Path to look for files in")
parser.add_argument("-e","--efficiencies", default=None, help="Name of efficiency dictionary key")
args = parser.parse_args()

def get_list_of_files(folder):
    
    path = os.path.join( args.inputpath, folder )
    if not os.path.exists( path ):
        raise RuntimeError( f"No such path {path}" )
    
    files = glob( os.path.join(args.inputpath, folder, "*.root") )
    if len(files)==0:
        raise RuntimeError( f"No root files found in {path}" )

    return files

def get_list_of_branches(folder):
    f0 = get_list_of_files(folder)[0]
    try:
        tr = uproot.open( f0+":events" )
        return [ br.name for br in tr.branches ]
    except:
        raise RuntimeError( f"No tree called events found in file {f0}" )

def check_var(folder, varname):
    branches = get_list_of_branches(folder)
    if varname not in branches:
        print( f"Branches found in files at path {folder}:" )
        for br in branches:
            print('  ', br)
        raise RuntimeError( f"No branch {varname} found in files at path {folder}. Try one from the list above." )
    return True

def as_array(folder, varname, cut):
    path = os.path.join( args.inputpath, folder, "*.root" )
    try: 
        # awkward array instead of numpy -> allows variable length elements
        #arr = uproot.concatenate( path+":events", expressions=varname, library="np")[varname]
        arr = uproot.concatenate( path+":events", expressions=varname, cut=cut)[varname]
    except:
        branches = get_list_of_branches(folder)
        print( f"Branches found in files at path {folder}:" )
        for br in branches:
            print('  ', br)
        raise RuntimeError( f"Cannot process expression {varname} in files at path {folder}. Try combinations of branches from the list above." )
    # Numpy option
    #return arr
    # Return awkward array as a flattened ndarray
    return ak.to_numpy(ak.ravel(arr))

# Should work as-is after flattening awkward array `values`
def outlier_removal(values, threshold=7):
    mean = np.mean(values)
    sdev = np.std(values)
    pull = (values - mean)/sdev
    values = values[ np.abs(pull)<=threshold ]

    return values

def histogram_settings():
    
    hist_settings = { sample: {} for sample in cfg.samples }

    for sample in cfg.samples:

        if sample in cfg.sample_allocations["signal"]:
            hist_settings[sample]["histtype"] = "bar"

        elif sample in cfg.sample_allocations["background"]:
            hist_settings[sample]["histtype"] = "step"

    return hist_settings

def get_efficiencies():
    if args.efficiencies is None:
        return { sample : 1 for sample in cfg.samples }
    else:
        if args.efficiencies not in cfg.efficiencies:
            raise RuntimeError( f"Tried passed efficiency dictionary key {args.efficiencies} which does not exist in config" )
        return cfg.efficiencies[args.efficiencies]

def get_weights():
    
    hist_weights = {}
    effs = get_efficiencies()
    for sample in cfg.samples:
        hist_weights[sample] = effs[sample] * cfg.branching_fractions[sample][0]
    
    return hist_weights

def plot(varname, stacked=True, weight=True, density=True, remove_outliers=True, interactive=False, save=None, bins=50, range=None, total=["background"], components=["signal", "background"], cut=None):
    
    """ 
    plot( varname, **opts ) will plot a variable

    Parameters
    ----------
    varname : str
        The variable to plot (must be branchname in tree). 
        If not available those that are will be listed.
    stacked : bool, optional
        Stack histograms by their "allocation". Default: true
    weight : bool, optional
        Weight histograms by their expected branching fraction 
        multiplied by efficiency. Default: true
    density : bool, optional
        Normalise histograms so that they reresent a probability
        density. Default: true
    remove_outliers : bool, optional
        Remove severe outliers from the distribution. Default: true
    interactive : bool, optional
        Show the plot interactively after its made. Default: false
    save : str, optional
        Save file for the plot. If None then no plot is saved. Default: none 
    cuts : str, optional
        Cut branch varname according to a (valid) ROOT expression. Default: none
    """

    if remove_outliers:
        values = { sample: outlier_removal(as_array(sample, varname, cut)) for sample in cfg.samples }
    else:
        values = { sample: as_array(sample, varname, cut) for sample in cfg.samples }

    if range is None:
        xmin = min( [ min(values[sample]) for sample in values ] )
        xmax = max( [ max(values[sample]) for sample in values ] )
    else:
        xmin = range[0]
        xmax = range[1]
    
    hist_settings = histogram_settings()
    hist_weights = get_weights()

    fig, ax = plt.subplots()

    for allocation in cfg.sample_allocations:
        if allocation not in components:
            continue
        samples = cfg.sample_allocations[allocation]
        hist_x = [ values[sample] for sample in samples ]
        hist_w = [ np.ones_like( values[sample] ) * hist_weights[sample] for sample in samples ]
        hist_l = [ cfg.titles[sample] for sample in samples ]
        if not weight:
            hist_w = None

        if stacked:
            hist_opts = dict( stacked=True, histtype='stepfilled', alpha=1 )
        else:
            hist_opts = dict( stacked=False, histtype='step', lw=2 )

        if allocation=='signal':
            hist_opts['histtype'] = 'step'
            hist_opts['lw'] = 2
            hist_opts['color'] = 'cornflowerblue'
            hist_opts['hatch'] = '////'
        elif allocation=='background':
            reds = mpl.colormaps['Reds_r']
            hist_opts['color'] = reds( np.linspace(0, 1, len(samples)+2)[1:-1] ) 
        
        ax.hist( 
            x = hist_x,
            bins = bins,
            range = (xmin,xmax),
            density = density,
            label = hist_l,
            weights = hist_w,
            **hist_opts
        )

        if allocation in total and stacked:
            ax.hist( 
                np.concatenate( hist_x), 
                bins = bins,
                range = (xmin,xmax),
                density = density,
                label = f'Total {allocation}',
                weights = np.concatenate( hist_w ),
                histtype = 'step',
                color = 'k',
                lw = 2,
            )

    ax.legend(reverse=True)
    if varname in cfg.variable_plot_titles:
        ax.set_xlabel( cfg.variable_plot_titles[varname] )
    else:
        ax.set_xlabel(f'{varname} (cut={cut})')
    ax.set_ylabel('Density')

    if interactive:
        plt.show()

    if save is not None:
        fig.savefig(save)

def make_plots():

    outpath = f"{args.inputpath}/plots"
    if not os.path.exists( outpath ):
        os.system( f"mkdir -p {outpath}" )
    
    for stacked in [True, False]:
        suffix = "_stacked" if stacked else ""
        plot( "EVT_Thrust_Emin_e", bins=100, range=(0,50), stacked=stacked, save=f"{outpath}/EVT_Thrust_Emin_e{suffix}.pdf" ) 
        plot( "EVT_Thrust_Emax_e", bins=100, range=(0,50), stacked=stacked, save=f"{outpath}/EVT_Thrust_Emin_e{suffix}.pdf" )
        plot( "MC_Z_pz", stacked=stacked, save=f"{outpath}/MC_Z_pz{suffix}.pdf")

if __name__=="__main__":

    #make_plots()

    print( plot.__doc__ )

