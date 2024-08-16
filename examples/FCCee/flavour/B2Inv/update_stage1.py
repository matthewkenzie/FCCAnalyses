############################################
# Add 'BDT1' branch to stage1 files
############################################
import sys
import os
import ROOT

from yaml import YAMLError, safe_load

#print ("Load cxx analyzers ... ",)
#ROOT.gSystem.Load("libedm4hep")
#ROOT.gSystem.Load("libpodio")
#ROOT.gSystem.Load("libawkward")
#ROOT.gSystem.Load("libawkward-cpu-kernels")
#ROOT.gSystem.Load("libFCCAnalyses")

ROOT.gErrorIgnoreLevel = ROOT.kFatal
#_edm  = ROOT.edm4hep.ReconstructedParticleData()
#_pod  = ROOT.podio.ObjectID()
#_fcc  = ROOT.dummyLoader

#print ('edm4hep  ',_edm)
#print ('podio    ',_pod)
#print ('fccana   ',_fcc)

class analysis():

    #__________________________________________________________
    def __init__(self, inputlist, outname, ncpu):
        self.outname = outname
        if ".root" not in outname:
            self.outname+=".root"
        self.ncpu = ncpu

        if ncpu>1: # MT and self.df.Range() is not allowed but MT must be enabled before constructing a df
            ROOT.ROOT.EnableImplicitMT(ncpu)
        ROOT.EnableThreadSafety()
        self.df = ROOT.RDataFrame("events", inputlist)
        print ("Input dataframe initialised!")
    #__________________________________________________________
    def run(self, n_events, MVA_cut, training, bdt1_training_vars, stage1_vars):
        print("Running...")
        MVAFilter=f"EVT_MVA1>{MVA_cut}"
    
        if self.ncpu==1:
            df2 = self.df.Range(0, n_events)
        else:
            df2 = self.df

        if not training:
            df3 = (
                df2
                .Define("MVAVec", ROOT.computeModel, bdt1_training_vars)
                .Define("EVT_MVA1", "MVAVec.at(0)")
                .Filter(MVAFilter)
            )
        else:
            df3 = df2
        
        branchList = ROOT.vector('string')()
        branchout = stage1_vars
        if not training:
            branchout.append("EVT_MVA1")
        for br in branchout:
            branchList.push_back(br)

        df3.Snapshot("events", self.outname, branchList)


# Return list of variables to use in the bdt as a python list
def vars_fromyaml(path, bdtlist):
    with open(path) as stream:
        try:
            file = safe_load(stream)
            outvars = file[bdtlist]
        except YAMLError as exc:
            print(exc)

    return outvars

if __name__ == "__main__":
    print("Initialising...")

    import argparse
    parser = argparse.ArgumentParser(description="Saves EVT_MVA1 branch", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input',nargs="+", required=True, help='Select the input file(s).')
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('--config', type=str, required=True, help='Select the config YAML file.')
    parser.add_argument('--branchnames', type=str, default='stage1-vars', help='Choose the key pointing to stage1 variables in the YAML file')
    parser.add_argument('--bdtnames', type=str, default='bdt1-training-vars', help='Choose the key pointing to bdt training variables in the YAML file')
    parser.add_argument('--MVA_cut', default = None, type=float, help='Choose the MVA cut.')
    parser.add_argument('--n_events', default = -1, type=int, help='Choose the number of events to process.')
    parser.add_argument('--n_cpus', default = 8, type=int, help='Choose the number of cpus to use.')
    parser.add_argument('--mva', default="", type=str, help='Path to the trained MVA ROOT file.')
    parser.add_argument('--training', default=False, action="store_const", const=True, help="prepare tuples for BDT training.")
    args = parser.parse_args()
    
    if not os.path.exists( args.config ):
        raise RuntimeError(f"Looking for a config file that doesn't exist {args.config}")

    bdt1_training_vars = list(vars_fromyaml(args.config, str(args.bdtnames)))
    stage1_vars        = list(vars_fromyaml(args.config, str(args.branchnames)))

    if not args.training:
        if not os.path.exists( args.mva ):
            raise RuntimeError(f"Looking for an MVA file that doesn't exist {args.mva}")
        # TODO make the above take the BDT name according to the decay
        ROOT.gInterpreter.ProcessLine(f'''
        TMVA::Experimental::RBDT bdt("bdt", "{args.mva}");
        computeModel = TMVA::Experimental::Compute<{len(bdt1_training_vars)}, float>(bdt);
        ''')

    input_files = ROOT.vector('string')()
    if "*" in args.input:
        import glob
        file_list = glob.glob(args.input)
        for file_name in file_list:
            input_files.push_back(file_name)
    else:
        for inf in args.input:
            input_files.push_back(inf)
    n_events=args.n_events
    if n_events==-1:
        n_events = 0
        for f in input_files:
            tf=ROOT.TFile.Open(str(f),"READ")
            tt=tf.Get("eventsSelected")
            n_events+=tt.GetVal()
        n_cpus=args.n_cpus
    else:
        print(f"WARNING: Cannot use multi-threading when running over a finite set of events. Setting n_cpus to 1.")
        n_cpus=1

    print("===============================STARTUP SUMMARY===============================")
    print(f"Training Mode     : {args.training}")
    print(f"Input File(s)     : {args.input}")
    print(f"Output File       : {args.output}")
    print(f"Config File       : {args.config}")
    print(f"Events to process : {n_events}")
    if not args.training:
        print(f"MVA Cut           : {args.MVA_cut}")
        print(f"MVA File          : {args.mva}")
    print(f"Number of CPUs    : {n_cpus}")
    print("=============================================================================")
    
    import time
    start_time = time.time()
    analysis = analysis(input_files, args.output, n_cpus)
    analysis.run(n_events, args.MVA_cut, args.training, bdt1_training_vars, stage1_vars)

    
    outf = ROOT.TFile( args.output, "update" )
    #meta = ROOT.TTree( "metadata", "metadata informations" )
    #n  = array( "i", [ 0 ] )
    #meta.Branch( "eventsProcessed", n, "eventsProcessed/I" )
    #n[0]=n_events
    #meta.Fill()
    p = ROOT.TParameter(int)( "eventsProcessed", n_events)
    p.Write()
    tree = outf.Get("events")
    n_selected = tree.GetEntries()
    s = ROOT.TParameter(int)( "eventsSelected", n_selected)
    s.Write()
    outf.Write()
    outf.Close()            

    elapsed_time = time.time() - start_time
    print  ("==============================COMPLETION SUMMARY=============================")
    print  ("Elapsed time (H:M:S)     :  ",time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print  ("Events Processed/Second  :  ",int(n_events/elapsed_time))
    print  ("Total Events Processed   :  ",int(n_events))
    print  ("Total Events Selected    :  ",int(n_selected))
    print  ("Preliminary efficiency   :  ",n_selected/n_events)
    print  ("=============================================================================")
