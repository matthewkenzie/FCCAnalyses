import sys
import ROOT
from array import array

print ("Load cxx analyzers ... ",)
ROOT.gSystem.Load("libedm4hep")
ROOT.gSystem.Load("libpodio")
ROOT.gSystem.Load("libawkward")
ROOT.gSystem.Load("libawkward-cpu-kernels")
ROOT.gSystem.Load("libFCCAnalyses")

ROOT.gErrorIgnoreLevel = ROOT.kFatal
_edm  = ROOT.edm4hep.ReconstructedParticleData()
_pod  = ROOT.podio.ObjectID()
_fcc  = ROOT.dummyLoader

print ('edm4hep  ',_edm)
print ('podio    ',_pod)
print ('fccana   ',_fcc)

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
    def run(self, n_events, MVA_cut, decay, candidates, child_pdgid, parent_pdgid, training):
        print("Running...")
        MVAFilter=f"EVT_MVA1>{MVA_cut}"

        if self.ncpu==1:
            df2 = self.df.Range(0, n_events)
        else:
            df2 = self.df

        df3 = (df2
               #############################################
               ##          find a candidate               ##
               #############################################
               .Define("CUT_CandInd",  f"FCCAnalyses::myFinalSel::selB2SCand( {candidates}Candidates_mass, {candidates}Candidates_vertex, Vertex_chi2)")
               .Filter("CUT_CandInd>-1")
               .Define("CUT_CandTruth",f"FCCAnalyses::myFinalSel::selB2SCandTM( {candidates}Candidates_mcvertex, True{candidates}_vertex, CUT_CandInd)")
               #.Define( # other cuts? )
               .Define("EVT_CandMass", f"{candidates}Candidates_mass.at(CUT_CandInd)")
               .Filter(f"EVT_CandMass<1.2") #FIXME
               .Define("CUT_VtxInd", f"{candidates}Candidates_vertex.at(CUT_CandInd)")
               .Define("CUT_CandVtxThrustEmin", "Vertex_thrusthemis_emin.at(CUT_VtxInd)")
               .Filter("CUT_CandVtxThrustEmin>0")

               .Define("EVT_CandN",  f"float({candidates}Candidates_vertex.size())")
               .Define("EVT_CandPx", f"{candidates}Candidates_px.at(CUT_CandInd)")
               .Define("EVT_CandPy", f"{candidates}Candidates_py.at(CUT_CandInd)")
               .Define("EVT_CandPz", f"{candidates}Candidates_pz.at(CUT_CandInd)")
               .Define("EVT_CandP",  f"{candidates}Candidates_p.at(CUT_CandInd)")
               .Define("EVT_CandD0", f"{candidates}Candidates_d0.at(CUT_CandInd)")
               .Define("EVT_CandZ0", f"{candidates}Candidates_z0.at(CUT_CandInd)")

               .Define("EVT_CandAngleThrust", f"{candidates}Candidates_anglethrust.at(CUT_CandInd)")
               .Define("EVT_CandVtxFD",    "Vertex_d2PV.at(CUT_VtxInd)")
               .Define("EVT_CandVtxFDErr", "Vertex_d2PVErr.at(CUT_VtxInd)")
               .Define("EVT_CandVtxChi2",  "Vertex_chi2.at(CUT_VtxInd)")

               .Define("EVT_Candh1P",  f"{candidates}Candidates_h1p.at(CUT_CandInd)")
               .Define("EVT_Candh2P",  f"{candidates}Candidates_h2p.at(CUT_CandInd)")
               .Define("EVT_Candh1D0", f"{candidates}Candidates_h1d0.at(CUT_CandInd)")
               .Define("EVT_Candh2D0", f"{candidates}Candidates_h2d0.at(CUT_CandInd)")
               .Define("EVT_Candh1Z0", f"{candidates}Candidates_h1z0.at(CUT_CandInd)")
               .Define("EVT_Candh2Z0", f"{candidates}Candidates_h2z0.at(CUT_CandInd)")

               .Define("EVT_Nominal_B_E", "float(91.1876 - EVT_ThrustEmin_E - EVT_ThrustEmax_E + sqrt(EVT_CandP*EVT_CandP + EVT_CandMass*EVT_CandMass))")

               .Define("EVT_DVd0_min", "FCCAnalyses::myFinalSel::get_min(DV_d0, EVT_CandD0)")
               .Define("EVT_DVd0_max", "FCCAnalyses::myFinalSel::get_max(DV_d0, EVT_CandD0)")
               .Define("EVT_DVd0_ave", "FCCAnalyses::myFinalSel::get_ave(DV_d0, EVT_CandD0)")

               .Define("EVT_DVz0_min", "FCCAnalyses::myFinalSel::get_min(DV_z0, EVT_CandZ0)")
               .Define("EVT_DVz0_max", "FCCAnalyses::myFinalSel::get_max(DV_z0, EVT_CandZ0)")
               .Define("EVT_DVz0_ave", "FCCAnalyses::myFinalSel::get_ave(DV_z0, EVT_CandZ0)")

               .Define("EVT_DVmass_min", "FCCAnalyses::myFinalSel::get_min(Vertex_mass, Vertex_isPV, CUT_VtxInd)")
               .Define("EVT_DVmass_max", "FCCAnalyses::myFinalSel::get_max(Vertex_mass, Vertex_isPV, CUT_VtxInd)")
               .Define("EVT_DVmass_ave", "FCCAnalyses::myFinalSel::get_ave(Vertex_mass, Vertex_isPV, CUT_VtxInd)")
               .Define("EVT_PVmass", "Vertex_mass.at(0)")

               .Define("EVT_ThrustDiff_E",        "EVT_ThrustEmax_E-EVT_ThrustEmin_E")
               .Define("EVT_ThrustDiff_N",        "EVT_ThrustEmax_N-EVT_ThrustEmin_N")
               .Define("EVT_ThrustDiff_Echarged", "EVT_ThrustEmax_Echarged-EVT_ThrustEmin_Echarged")
               .Define("EVT_ThrustDiff_Eneutral", "EVT_ThrustEmax_Eneutral-EVT_ThrustEmin_Eneutral")
               .Define("EVT_ThrustDiff_Ncharged", "EVT_ThrustEmax_Ncharged-EVT_ThrustEmin_Ncharged")
               .Define("EVT_ThrustDiff_Nneutral", "EVT_ThrustEmax_Nneutral-EVT_ThrustEmin_Nneutral")

               .Define("CUT_MCVtxInd", f"{candidates}Candidates_mcvertex.at(CUT_CandInd)")
               #.Define("MCVertex_PDG", "MC_Vertex_PDG.at(CUT_MCVtxInd)")
               #.Define("MCVertex_PDGmother", "MC_Vertex_PDGmother.at(CUT_MCVtxInd)")
               #.Define("MCVertex_PDGgmother", "MC_Vertex_PDGgmother.at(CUT_MCVtxInd)")
               #.Define("MCVertex_n", "int(MC_Vertex_PDG.at(CUT_MCVtxInd).size())")
               #.Define("MCVertex_nmother", "int(MC_Vertex_PDGmother.at(CUT_MCVtxInd).size())")
               #.Define("MCVertex_ngmother", "int(MC_Vertex_PDGgmother.at(CUT_MCVtxInd).size())")

            )

        if not training:
            df4 = (df3
               # Build MVA
               .Define("MVAVec", ROOT.computeModel, ("EVT_CandMass",
                                                     "EVT_CandN",           "EVT_CandVtxFD",    "EVT_CandVtxChi2",
                                                     "EVT_CandPx",          "EVT_CandPy",       "EVT_CandPz",
                                                     "EVT_CandP",           "EVT_CandD0",       "EVT_CandZ0",
                                                     "EVT_CandAngleThrust", "EVT_DVd0_min",     "EVT_DVd0_max",
                                                     "EVT_DVd0_ave",        "EVT_DVz0_min",     "EVT_DVz0_max",
                                                     "EVT_DVz0_ave",        "EVT_PVmass",       "EVT_Nominal_B_E"))
               .Define("EVT_MVA2", "MVAVec.at(0)")
               .Filter(MVAFilter)
            )
        else:
            df4 = df3

        branchList = ROOT.vector('string')()
        desired_branches = [
                "CUT_CandTruth",
                "CUT_CandVtxThrustEmin",

                "EVT_ThrustEmin_E",          "EVT_ThrustEmax_E",
                "EVT_ThrustEmin_Echarged",   "EVT_ThrustEmax_Echarged",
                "EVT_ThrustEmin_Eneutral",   "EVT_ThrustEmax_Eneutral",
                "EVT_ThrustEmin_Ncharged",   "EVT_ThrustEmax_Ncharged",
                "EVT_ThrustEmin_Nneutral",   "EVT_ThrustEmax_Nneutral",
                "EVT_ThrustEmin_NDV",        "EVT_ThrustEmax_NDV",
                "EVT_ThrustDiff_E",          "EVT_ThrustDiff_N",
                "EVT_ThrustDiff_Echarged",   "EVT_ThrustDiff_Eneutral",
                "EVT_ThrustDiff_Ncharged",   "EVT_ThrustDiff_Nneutral",
                "EVT_Thrust_Mag",
                "EVT_Thrust_X",  "EVT_Thrust_XErr",
                "EVT_Thrust_Y",  "EVT_Thrust_YErr",
                "EVT_Thrust_Z",  "EVT_Thrust_ZErr",

                "EVT_CandN",
                "EVT_CandMass",
                "EVT_CandVtxFD","EVT_CandVtxFDErr", "EVT_CandVtxChi2",
                "EVT_CandPx","EVT_CandP","EVT_CandPz","EVT_CandPy",
                "EVT_CandD0","EVT_CandZ0","EVT_CandAngleThrust",
                "EVT_MVA1",

                "EVT_Candh1P","EVT_Candh1D0","EVT_Candh1Z0",
                "EVT_Candh2P","EVT_Candh2D0","EVT_Candh2Z0",

                "EVT_DVd0_min", "EVT_DVd0_max", "EVT_DVd0_ave",
                "EVT_DVz0_min", "EVT_DVz0_max", "EVT_DVz0_ave",
                "EVT_DVmass_min", "EVT_DVmass_max", "EVT_DVmass_ave",
                "EVT_PVmass",
                "EVT_Nominal_B_E",
                #"MCVertex_PDG","MCVertex_PDGmother","MCVertex_PDGgmother","MCVertex_n","MCVertex_nmother","MCVertex_ngmother",
                "MC_PDG","MC_M1","MC_M2","MC_n","MC_D1","MC_D2", "MC_D3", "MC_D4",
                f"True{candidates}_vertex"
                ]

        if not training:
            desired_branches.append("EVT_MVA2")
        for branchName in desired_branches:
            branchList.push_back(branchName)
        df4.Snapshot("events", self.outname, branchList)

if __name__ == "__main__":

    print("Initialising...")

    import argparse
    parser = argparse.ArgumentParser(description="Applies second stage cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input',nargs="+", required=True, help='Select the input file(s).')
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('--MVA_cut', default = -1., type=float, help='Choose the MVA cut.')
    parser.add_argument('--n_events', default = 0, type=int, help='Choose the number of events to process.')
    parser.add_argument('--n_cpus', default = 8, type=int, help='Choose the number of cpus to use.')
    parser.add_argument('--decay', required=True, type=str, help='Choose the decay to reconstruct.')
    parser.add_argument('--mva', default="", type=str, help='Path to the trained MVA ROOT file.')
    parser.add_argument("--training", default=False, action="store_const", const=True, help="prepare tuples for BDT training.")
    args = parser.parse_args()

    if not args.training:
        assert(args.mva!="")
        # TODO make the above take the BDT name according to the decay
        ROOT.gInterpreter.ProcessLine(f'''
        TMVA::Experimental::RBDT<> bdt("{args.decay}_BDT", "{args.mva}");
        computeModel = TMVA::Experimental::Compute<19, float>(bdt);
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
    if n_events==0:
        for f in input_files:
            tf=ROOT.TFile.Open(str(f),"READ")
            tt=tf.Get("events")
            n_events+=tt.GetEntries()
        n_cpus=args.n_cpus
    else:
        print(f"WARNING: Cannot use multi-threading when running over a finite set of events. Setting n_cpus to 1.")
        n_cpus=1

    print("===============================STARTUP SUMMARY===============================")
    print(f"Training Mode     : {args.training}")
    print(f"Input File(s)     : {args.input}")
    print(f"Output File       : {args.output}")
    print(f"Events to process : {n_events}")
    if not args.training:
        print(f"MVA Cut           : {args.MVA_cut}")
    print(f"Number of CPUs    : {n_cpus}")
    print("=============================================================================")

    from config import decay_to_candidates, decay_to_pdgids
    candidates = decay_to_candidates[args.decay]
    child_pdgid, parent_pdgid = decay_to_pdgids[args.decay]
    import time
    start_time = time.time()
    analysis = analysis(input_files, args.output, n_cpus)
    analysis.run(n_events, args.MVA_cut, args.decay, candidates, child_pdgid, parent_pdgid, args.training)

    elapsed_time = time.time() - start_time
    print  ("==============================COMPLETION SUMMARY=============================")
    print  ("Elapsed time (H:M:S)     :  ",time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print  ("Events Processed/Second  :  ",int(n_events/elapsed_time))
    print  ("Total Events Processed   :  ",int(n_events))
    print  ("=============================================================================")


    outf = ROOT.TFile( args.output, "update" )
    meta = ROOT.TTree( "metadata", "metadata informations" )
    n = array( "i", [ 0 ] )
    meta.Branch( "eventsProcessed", n, "eventsProcessed/I" )
    n[0]=n_events
    meta.Fill()
    p = ROOT.TParameter(int)( "eventsProcessed", n[0])
    p.Write()
    outf.Write()
    outf.Close()

