import sys
import os
import subprocess
import time
import uproot

from glob import glob

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import awkward as ak


# Requires config file in the working directory
import config as cfg
plt.style.use('fcc.mplstyle')

##################################################################
#               PLANNED FEATURES
# Analysis
#   Saving from all/selected background files
#   Save EVT level and Particle level data
#   Cut using EVT level and Particle level cuts
#   Aliases for complicated expressions
#   Easy handling of expressions involving EVT and Particle level expressions
#       For example angle between particle momentum and thrust axis
#
#
# Plotting
#   Plot data from analysis
#   Plot data directly from file
#   Save/show plots
#   Custom range for binning
#   Custom x and y limits
#   Automatic title
#   Distinguish signal from background when plotting
##################################################################
class TupleHandler():
    """
    Class that handles stage0 data, including cutting and plotting
    """
    def __init__(self,
                 inputpath=None,
                 outputpath=None,
                 init_status=True):
        
        # Check if inputpath is a valid directory, if None use default stage0 directory
        self.set_inputpath(inputpath)

        # Save outputs in self.outputpath, if directory does not exist try to create it
        self.set_outputpath(outputpath)

        self.config_essential_attributes = ['samples',
                                            'sample_allocations',
                                            'titles',
                                            'prod_frac',
                                            'branching_fractions',
                                            'efficiencies',
                                            'PIDs']

        # Instantiating methods
        self.configure()
        
        if init_status:
            self.print_status()
        

    def set_inputpath(self, inputpath):
        ''' Define directory in which config.samples are located. If None use default'''
        if inputpath is None:
            self.inputpath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'
        else:
            if not os.path.exists(inputpath):
                raise RuntimeError(f"No such path: {inputpath}")
            self.inputpath = inputpath

    def set_outputpath(self, outputpath):
        ''' Define directory to save files to. If None use default.'''
        if outputpath is None:
            self.outputpath = '/r01/lhcb/rrm42/fcc/stage_post0/'
        else:
            if not os.path.exists(outputpath):
                try:
                    subprocess.run(["mkdir", outputpath], check=True)
                except subprocess.CalledProcessError:
                    print(f"Cannot create directory {outputpath}")

            self.outputpath = outputpath

    def configure(self):
        """ 
        Import config file

        Parameters
        ----------
        config_file : str, optional
            Full path to the config_file.py to import
        """
        if not set(self.config_essential_attributes).issubset(cfg.__dict__.keys()):
            raise AttributeError(f"Config file does not have all essential attributes: {self.config_essential_attributes}")

        self.update_file_dict(cfg.samples)
        self.clear_hist_data()

    def update_file_dict(self, samples):
        """
        Return a dictionary with filepaths as a list and as glob syntax
        path_dict for functions such as uproot.iterate, file_dict for functions such as uproot.concatenate
        """
        self.file_dict = {}
        self.path_dict = {}
        for sample in samples:
            self.path_dict[sample], self.file_dict[sample] = self.get_files(sample)

    def get_files(self, folder):
        """
        Search for .root files in self.inputpath/folder

        Parameters
        ----------
        folder : str, required
            Name of the folder(s) in which to search for the .root files

        Returns
        -------
        path : str
            Path to .root files in `glob` syntax (i.e. as self.inputpath/folder/*.root)
        files : list
            List of .root filenames inside `folder`
        """
        path = os.path.join(self.inputpath, folder)
        if not os.path.exists( path ):
            raise RuntimeError(f"No such path: {path}")
        path = os.path.join(path, "*.root")
        files = glob( path )
        if len(files) == 0:
            raise RuntimeError(f"No root files in {path}")
        return path, files

    def print_status(self):
        ''' Print values of class attributes required for start-up'''
        time.sleep(2)
        print("-------------------------------------------------")
        print("               TUPLE HANDLER CLASS               ")
        print("-------------------------------------------------")
        time.sleep(1)
        print(f"\n\nUsing {os.path.abspath(cfg.__file__)} as config...\n")
        print(f"Samples from {self.inputpath}...\n")
        print(f"Saving to {self.outputpath}...\n\n")
        print("-------------------------------------------------")
        time.sleep(1)
        if self.file_dict is not None: 
            print(f"File paths saved")
        if self.hist_data is not None:
            print(f"Current histogram data: {self.hist_data}")

    def clear_hist_data(self):
        self.hist_data = { }
    
    def get_branch_data(self,
                    branches,
                    branchtype,
                    hemisphere,
                    aliases=None,
                    cut_EVTlevel=None,
                    cut_MClevel=None,
                    cut_REClevel=None,
                    sample_select=None,
                    output_type='rt',
                    show_status=False,
                    custom_tree_name=None,
                    custom_out_name=None):
        """
        Store data from .root files to analyse or plot
        
        Parameters
        ----------
        branches : str
            Branches or equivalent expression to store
        branchtype : str
            The type of branches. Acceptable entries are 'per-event' or 'per-particle'
        hemisphere : str, optional
            Selection of min/max energy hemisphere. Applies only if branchtype is 'per-particle'
            Options are 'both', 'max' or 'min'. Default = 'both'
        cut_EVTlevel : str, optional
            Cut branches at event level (row). Must be acceptable to uproot's `cut` parameter.
            Applies to both 'per-event' and 'per-particle' branch types. Default = None
        cut_PARTlevel : str, optional
            Cut branches at particle level (column). Must be acceptable to uproot's `cut` parameter.
            Applies only to the 'per-particle' branch types. Default = None
        sample_select : list, optional
            List of indices of cfg.samples to use.  If None uses all of cfg.samples.
            Preferred behaviour is to use an appropriate config and keep this None. Default = None
        output_type : str, optional
            'hist' : flattens data into 1d ndarray for plotting. Needs a single entry in branches
            ---EVENTUALLY---
            'ak'   : returns data as a highlevel awkard Array
            'pd'   : returns data as a pandas DataFrame
            'rt'   : saves cut branches as a .root file in the current directory
        """

        #################################################
        #
        # EXCEPTION HANDLING
        #
        #################################################
        if ( not (branches or branchtype) ) or ( branchtype not in ['per-event', 'per-mc', 'per-rec'] ):
            raise ValueError('One of branch or branchtype was empty, or branchtype invalid.')

        if hemisphere[0:4] not in ['both', 'max ', 'min ']:
            raise ValueError('`hemisphere` must be both, max or min followed by variable to use for angle')
        
        if ( not branchtype ) and ( cut_EVTlevel or cut_MClevel or cut_REClevel):
            raise ValueError(f'branchtype {branchtype} incompatible with non-trivial cuts')
        elif branchtype == 'per-event' and ((cut_MClevel is not None) or (cut_REClevel is not None)):
            raise ValueError('event level branches but particle level cuts provided')
        elif branchtype == 'per-mc' and cut_REClevel is not None:
            raise ValueError('MC variable branches but Reconstructed type cuts provided')
        elif branchtype == 'per-rec' and cut_MClevel is not None:
            raise ValueError('Reconstructed variable branches but MC type cuts provided')

        if sample_select is not None:
            samples = [ cfg.samples[i] for i in sample_select ]
        else:
            samples = cfg.samples

        if (len(branches) > 1) and (output_type == 'hist'):
            raise ValueError('Cannot create a histogram with more than one branch')
        
        if (custom_out_name is not None) and (len(custom_out_name) != len(samples)):
            raise ValueError(f'{custom_out_name} cannot be broadcast to {samples}: incorrect length')
        #################################################
        # END OF EXCEPTION HANDLING
        #################################################


        #################################################
        #
        # UPDATE NAMES OF FILES TO USE
        #
        #################################################
        self.update_file_dict(samples)

        #################################################
        #
        # GENERATE STRING TO PASS TO `CUT`
        #
        #################################################
        # Basic expression without direction information
        cut_expr = None
        if (cut_EVTlevel is not None) and (cut_MClevel is not None):
            cut_expr = f"({cut_EVTlevel}) & ({cut_MClevel})"
        elif (cut_EVTlevel is not None) and (cut_REClevel is not None):
            cut_expr = f"({cut_EVTlevel}) & ({cut_REClevel})"
        elif cut_EVTlevel is not None:
            cut_expr = cut_EVTlevel
        elif cut_MClevel is not None:
            cut_expr = cut_MClevel
        elif cut_REClevel is not None:
            cut_expr = cut_REClevel
        
        # Append hemisphere condition
        if (hemisphere != 'both') and (branchtype not in ['per-mc', 'per-rec']):
            raise ValueError(f"Hemisphere value {hemisphere} needs `per-particle` branchtype")
        elif hemisphere[0:4] == 'min ':
            var4theta = hemisphere[4:-1]
            poscosTheta = f"(EVT_Thrust_x*{var4theta}x + EVT_Thrust_y*{var4theta}y + EVT_Thrust_z*{var4theta}z) / ((EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5 * ({var4theta}x**2 + {var4theta}y**2+{var4theta}z**2)) > 0"
            
            cut_expr = f"({cut_expr}) & ({poscosTheta})"
        elif hemisphere[0:4] == 'max ':
            var4theta = hemisphere[4:-1]
            negcosTheta = f"(EVT_Thrust_x*{var4theta}x + EVT_Thrust_y*{var4theta}y + EVT_Thrust_z*{var4theta}z) / ((EVT_Thrust_x**2 + EVT_Thrust_y**2 + EVT_Thrust_z**2)**0.5 * ({var4theta}x**2 + {var4theta}y**2+{var4theta}z**2)) < 0"
            
            cut_expr = f"({cut_expr}) & ({negcosTheta})"
        elif hemisphere == 'both':
            pass
        else:
            raise ValueError("Incompatible options for `hemisphere` and `branchtype`")
        #################################################
        # END OF CUT EXPRESSION GENERATION              
        #################################################

        #################################################
        #
        # SAVE TO ROOT FILE AT GIVEN OUTPUTPATH
        # Issues -------> Remove [] from dataset instead of empty entry in tree
        #################################################
        if output_type == 'rt':
            tree_name = custom_tree_name if custom_tree_name is not None else 'tree'

            if show_status:
                time.sleep(0.5)
                print("----------------------------\n")
                print("Preliminary checks passed...")
                print(f"Using name {tree_name} for root TTree...")
                print("\n----------------------------")
            
            for sample in samples:
                with uproot.recreate(os.path.join(self.outputpath, sample+".root")) as outfile:
                    df = ak.Array([])
                    for file in uproot.iterate(self.path_dict[sample]+':events', expressions=branches, aliases=aliases, cut=cut_expr):
                        df = ak.concatenate([df, file])

                    outfile['tree'] = ak.zip({branch: df[branch] for branch in branches})
                    if show_status:
                        print(f"Branches from {sample} stored in {outfile}")


        #################################################
        #
        # WIP ----> SAVE TO SELF.HIST_DATA FOR PLOTTING
        #
        #################################################
        if output_type == 'hist':

            if show_status:
                time.sleep(0.5)
                print("----------------------------\n")
                print("Preliminary checks passed...")
                print(f"Saving {branches} for plotting...")
                print("\n----------------------------")

            for sample in samples:
                self.hist_data[sample] = np.array([])
                with uproot.iterate(self.file_dict[sample]+':events', expressions=branches, cut=cut_expr, aliases=aliases) as tree:
                    self.hist_data[sample] = np.append(self.hist_data[sample], 
                                                       ak.ravel(tree[branches]).to_numpy())

    def plot_histogram(self,
                       external_data=None,
                       style='all-backgrounds',
                       stacked=True, 
                       density=True, 
                       remove_outliers=True,
                       interactive=False,
                       save=None,
                       total=['background'],
                       components=['signal', 'background'],
                       range=None,
                       clear_saved_data=False):
        """
        Plot histogram using self.hist_data generated by self.get_branch_data

        Parameters
        ----------

        
        """
        if total is None:
            total = self.total

        if components is None:
            components = self.components
        if remove_outliers:
            self.hist_data = { sample: self.remove_outliers(self.hist_data[sample]) for sample in self.hist_data }

        if range is None:
            xmin = min( [ min(self.hist_data[sample]) for sample in self.hist_data ] )
            xmax = max( [ max(self.hist_data[sample]) for sample in self.hist_data ] )
        else:
            xmin = range[0]
            xmax = range[1]
        
        #
        # PLOTTING HERE
        #

        if interactive:
            plt.show()

        if save is not None:
            plt.savefig(save)

        if clear_saved_data:
            self.clear_hist_data()
