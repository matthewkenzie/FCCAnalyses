import os
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
    def run(self, n_events, MVA_cut, training):
        print("Running...")
        MVAFilter=f"EVT_MVA1>{MVA_cut}"

        if self.ncpu==1:
            df2 = self.df.Range(0, n_events)
        else:
            df2 = self.df
        
        df3 = (df2
               #############################################
               ##          Aliases for # in python        ##
               #############################################
               .Alias("MCRecoAssociations0", "MCRecoAssociations#0.index")
               .Alias("MCRecoAssociations1", "MCRecoAssociations#1.index")
               .Alias("Particle0", "Particle#0.index")
               .Alias("Particle1", "Particle#1.index")


               #############################################
               ##MC record to study the Z->bb events types##
               #############################################               
               .Define("MC_PDG", "FCCAnalyses::MCParticle::get_pdg(Particle)")
               .Define("MC_n",   "int(MC_PDG.size())")
               #.Define("MC_M1",  "FCCAnalyses::myUtils::get_MCMother1(Particle,Particle0)")
               #.Define("MC_M2",  "FCCAnalyses::myUtils::get_MCMother2(Particle,Particle0)")
               #.Define("MC_D1",  "FCCAnalyses::myUtils::get_MCDaughter1(Particle,Particle1)")
               #.Define("MC_D2",  "FCCAnalyses::myUtils::get_MCDaughter2(Particle,Particle1)")
               .Define("MC_M1",  "FCCAnalyses::myUtils::getMC_parent(0,Particle,Particle0)")
               .Define("MC_M2",  "FCCAnalyses::myUtils::getMC_parent(1,Particle,Particle0)")
               .Define("MC_D1",  "FCCAnalyses::myUtils::getMC_daughter(0,Particle,Particle1)")
               .Define("MC_D2",  "FCCAnalyses::myUtils::getMC_daughter(1,Particle,Particle1)")
               .Define("MC_D3",  "FCCAnalyses::myUtils::getMC_daughter(2,Particle,Particle1)")
               .Define("MC_D4",  "FCCAnalyses::myUtils::getMC_daughter(3,Particle,Particle1)")
               .Define("MC_orivtx_x",   "FCCAnalyses::MCParticle::get_vertex_x(Particle)")
               .Define("MC_orivtx_y",   "FCCAnalyses::MCParticle::get_vertex_y(Particle)")
               .Define("MC_orivtx_z",   "FCCAnalyses::MCParticle::get_vertex_z(Particle)")
               .Define("MC_endvtx_x",   "FCCAnalyses::MCParticle::get_endPoint_x(Particle)")
               .Define("MC_endvtx_y",   "FCCAnalyses::MCParticle::get_endPoint_y(Particle)")
               .Define("MC_endvtx_z",   "FCCAnalyses::MCParticle::get_endPoint_z(Particle)")
               .Define("MC_p",   "FCCAnalyses::MCParticle::get_p(Particle)")
               .Define("MC_pt",  "FCCAnalyses::MCParticle::get_pt(Particle)")
               .Define("MC_px",  "FCCAnalyses::MCParticle::get_pt(Particle)")
               .Define("MC_py",  "FCCAnalyses::MCParticle::get_pt(Particle)")
               .Define("MC_pz",  "FCCAnalyses::MCParticle::get_pt(Particle)")
               .Define("MC_e",   "FCCAnalyses::MCParticle::get_e(Particle)")
               .Define("MC_m",   "FCCAnalyses::MCParticle::get_mass(Particle)")
               .Define("MC_q",   "FCCAnalyses::MCParticle::get_charge(Particle)")
               .Define("MC_eta", "FCCAnalyses::MCParticle::get_eta(Particle)")
               .Define("MC_phi", "FCCAnalyses::MCParticle::get_phi(Particle)")
               

               #############################################
               ##               Build MC Vertex           ##
               #############################################
               .Define("MCVertexObject", "FCCAnalyses::myUtils::get_MCVertexObject(Particle, Particle0)")
               .Define("MC_Vertex_x",    "FCCAnalyses::myUtils::get_MCVertex_x(MCVertexObject)")
               .Define("MC_Vertex_y",    "FCCAnalyses::myUtils::get_MCVertex_y(MCVertexObject)")
               .Define("MC_Vertex_z",    "FCCAnalyses::myUtils::get_MCVertex_z(MCVertexObject)")
               .Define("MC_Vertex_ind",  "FCCAnalyses::myUtils::get_MCindMCVertex(MCVertexObject)")
               .Define("MC_Vertex_ntrk", "FCCAnalyses::myUtils::get_NTracksMCVertex(MCVertexObject)")
               .Define("MC_Vertex_n",    "int(MC_Vertex_x.size())")
               .Define("MC_Vertex_PDG",  "FCCAnalyses::myUtils::get_MCpdgMCVertex(MCVertexObject, Particle)")
               .Define("MC_Vertex_PDGmother",  "FCCAnalyses::myUtils::get_MCpdgMotherMCVertex(MCVertexObject, Particle)")
               .Define("MC_Vertex_PDGgmother", "FCCAnalyses::myUtils::get_MCpdgGMotherMCVertex(MCVertexObject, Particle)")


               #############################################
               ##              Build Reco Vertex          ##
               #############################################
               .Define("VertexObject", "FCCAnalyses::myUtils::get_VertexObject(MCVertexObject,ReconstructedParticles,EFlowTrack_1,MCRecoAssociations0,MCRecoAssociations1)")


               #############################################
               ##          Build PV var and filter        ##
               #############################################
               .Define("EVT_hasPV",    "FCCAnalyses::myUtils::hasPV(VertexObject)")
               .Define("EVT_NtracksPV", "float(FCCAnalyses::myUtils::get_PV_ntracks(VertexObject))")
               .Define("EVT_NVertex",   "float(VertexObject.size())")
               .Filter("EVT_hasPV==1")


               #############################################
               ##          Build RECO P with PID          ##
               #############################################
               .Define("RecoPartPID" ,"FCCAnalyses::myUtils::PID(ReconstructedParticles, MCRecoAssociations0,MCRecoAssociations1,Particle)")
               

               #############################################
               ##    Build RECO P with PID at vertex      ##
               #############################################
               .Define("RecoPartPIDAtVertex" ,"FCCAnalyses::myUtils::get_RP_atVertex(RecoPartPID, VertexObject)")


               #############################################
               ##         Build vertex variables          ##
               #############################################
               .Define("Vertex_x",        "FCCAnalyses::myUtils::get_Vertex_x(VertexObject)")
               .Define("Vertex_y",        "FCCAnalyses::myUtils::get_Vertex_y(VertexObject)")
               .Define("Vertex_z",        "FCCAnalyses::myUtils::get_Vertex_z(VertexObject)")
               .Define("Vertex_xErr",     "FCCAnalyses::myUtils::get_Vertex_xErr(VertexObject)")
               .Define("Vertex_yErr",     "FCCAnalyses::myUtils::get_Vertex_yErr(VertexObject)")
               .Define("Vertex_zErr",     "FCCAnalyses::myUtils::get_Vertex_zErr(VertexObject)")

               .Define("Vertex_chi2",     "FCCAnalyses::myUtils::get_Vertex_chi2(VertexObject)")
               .Define("Vertex_mcind",    "FCCAnalyses::myUtils::get_Vertex_indMC(VertexObject)")
               .Define("Vertex_ind",      "FCCAnalyses::myUtils::get_Vertex_ind(VertexObject)")
               .Define("Vertex_isPV",     "FCCAnalyses::myUtils::get_Vertex_isPV(VertexObject)")
               .Define("Vertex_ntrk",     "FCCAnalyses::myUtils::get_Vertex_ntracks(VertexObject)")
               .Define("Vertex_n",        "int(Vertex_x.size())")
               .Define("Vertex_mass",     "FCCAnalyses::myUtils::get_Vertex_mass(VertexObject,RecoPartPIDAtVertex)")

               .Define("Vertex_d2PV",     "FCCAnalyses::myUtils::get_Vertex_d2PV(VertexObject,-1)")
               .Define("Vertex_d2PVx",    "FCCAnalyses::myUtils::get_Vertex_d2PV(VertexObject,0)")
               .Define("Vertex_d2PVy",    "FCCAnalyses::myUtils::get_Vertex_d2PV(VertexObject,1)")
               .Define("Vertex_d2PVz",    "FCCAnalyses::myUtils::get_Vertex_d2PV(VertexObject,2)")
               
               .Define("Vertex_d2PVErr",  "FCCAnalyses::myUtils::get_Vertex_d2PVError(VertexObject,-1)")
               .Define("Vertex_d2PVxErr", "FCCAnalyses::myUtils::get_Vertex_d2PVError(VertexObject,0)")
               .Define("Vertex_d2PVyErr", "FCCAnalyses::myUtils::get_Vertex_d2PVError(VertexObject,1)")
               .Define("Vertex_d2PVzErr", "FCCAnalyses::myUtils::get_Vertex_d2PVError(VertexObject,2)")
               
               .Define("Vertex_d2PVSig",  "Vertex_d2PV/Vertex_d2PVErr")
               .Define("Vertex_d2PVxSig", "Vertex_d2PVx/Vertex_d2PVxErr")
               .Define("Vertex_d2PVySig", "Vertex_d2PVy/Vertex_d2PVyErr")
               .Define("Vertex_d2PVzSig", "Vertex_d2PVz/Vertex_d2PVzErr")

               .Define("Vertex_d2MC",     "FCCAnalyses::myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,-1)")
               .Define("Vertex_d2MCx",    "FCCAnalyses::myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,0)")
               .Define("Vertex_d2MCy",    "FCCAnalyses::myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,1)")
               .Define("Vertex_d2MCz",    "FCCAnalyses::myUtils::get_Vertex_d2MC(VertexObject,MCVertexObject,Vertex_mcind,2)")

               .Define("EVT_dPV2DVmin",   "FCCAnalyses::myUtils::get_dPV2DV_min(Vertex_d2PV)")
               .Define("EVT_dPV2DVmax",   "FCCAnalyses::myUtils::get_dPV2DV_max(Vertex_d2PV)")
               .Define("EVT_dPV2DVave",   "FCCAnalyses::myUtils::get_dPV2DV_ave(Vertex_d2PV)")
               

               #############################################
               ##        Build B->Inv  candidates         ##
               #############################################
               # this is where we would build candidates
               #.Define(f"{SigCandidates",         f"FCCAnalyses::myUtils::build_{decay}(VertexObject,RecoPartPIDAtVertex)")


               #############################################
               ##       Filter  candidates                ##
               ############################################# 
               #.Define(f"EVT_NSigCands",              f"float(FCCAnalyses::myUtils::getFCCAnalysesComposite_N(SigCandidates))")
               #.Filter(f"EVT_NSigCands>0")


               #############################################
               ##    Attempt to add a truth match         ##
               #############################################
               #.Define("TruthMatching" ,f"FCCAnalyses::myUtils::add_truthmatched2(SigCandidates, Particle, VertexObject, MCRecoAssociations1, ReconstructedParticles, Particle0)")


               #############################################
               ##              Build the thrust           ##
               ############################################# 
               .Define("RP_e",          "FCCAnalyses::ReconstructedParticle::get_e(RecoPartPIDAtVertex)")
               .Define("RP_px",         "FCCAnalyses::ReconstructedParticle::get_px(RecoPartPIDAtVertex)")
               .Define("RP_py",         "FCCAnalyses::ReconstructedParticle::get_py(RecoPartPIDAtVertex)")
               .Define("RP_pz",         "FCCAnalyses::ReconstructedParticle::get_pz(RecoPartPIDAtVertex)")
               .Define("RP_charge",     "FCCAnalyses::ReconstructedParticle::get_charge(RecoPartPIDAtVertex)")
              
               .Define("EVT_thrustNP",      'FCCAnalyses::Algorithms::minimize_thrust("Minuit2","Migrad")(RP_px, RP_py, RP_pz)')
               .Define("RP_thrustangleNP",  'FCCAnalyses::Algorithms::getAxisCosTheta(EVT_thrustNP, RP_px, RP_py, RP_pz)')
               .Define("EVT_thrust",        'FCCAnalyses::Algorithms::getThrustPointing(1.)(RP_thrustangleNP, RP_e, EVT_thrustNP)') # changed from 'Algorithms::getThrustPointing(RP_thrustangleNP, RP_e, EVT_thrustNP, 1.)' because of https://github.com/HEP-FCC/FCCAnalyses/commit/e9c4787f82505115be0c084da4453031c3cf8fdf
               .Define("RP_thrustangle",    'FCCAnalyses::Algorithms::getAxisCosTheta(EVT_thrust, RP_px, RP_py, RP_pz)')

               
               #############################################
               ##        Get thrust related values        ##
               ############################################# 
               ##hemis0 == negative angle == max energy hemisphere if pointing
               ##hemis1 == positive angle == min energy hemisphere if pointing
               .Define("EVT_thrusthemis0_n",    "FCCAnalyses::Algorithms::getAxisN(0)(RP_thrustangle, RP_charge)")
               .Define("EVT_thrusthemis1_n",    "FCCAnalyses::Algorithms::getAxisN(1)(RP_thrustangle, RP_charge)")
               .Define("EVT_thrusthemis0_e",    "FCCAnalyses::Algorithms::getAxisEnergy(0)(RP_thrustangle, RP_charge, RP_e)")
               .Define("EVT_thrusthemis1_e",    "FCCAnalyses::Algorithms::getAxisEnergy(1)(RP_thrustangle, RP_charge, RP_e)")

               .Define("EVT_ThrustEmax_E",         "EVT_thrusthemis0_e.at(0)")
               .Define("EVT_ThrustEmax_Echarged",  "EVT_thrusthemis0_e.at(1)")
               .Define("EVT_ThrustEmax_Eneutral",  "EVT_thrusthemis0_e.at(2)")
               .Define("EVT_ThrustEmax_N",         "float(EVT_thrusthemis0_n.at(0))")
               .Define("EVT_ThrustEmax_Ncharged",  "float(EVT_thrusthemis0_n.at(1))")
               .Define("EVT_ThrustEmax_Nneutral",  "float(EVT_thrusthemis0_n.at(2))")

               .Define("EVT_ThrustEmin_E",         "EVT_thrusthemis1_e.at(0)")
               .Define("EVT_ThrustEmin_Echarged",  "EVT_thrusthemis1_e.at(1)")
               .Define("EVT_ThrustEmin_Eneutral",  "EVT_thrusthemis1_e.at(2)")
               .Define("EVT_ThrustEmin_N",         "float(EVT_thrusthemis1_n.at(0))")
               .Define("EVT_ThrustEmin_Ncharged",  "float(EVT_thrusthemis1_n.at(1))")
               .Define("EVT_ThrustEmin_Nneutral",  "float(EVT_thrusthemis1_n.at(2))")


               .Define("Vertex_thrust_angle",   "FCCAnalyses::myUtils::get_Vertex_thrusthemis_angle(VertexObject, RecoPartPIDAtVertex, EVT_thrust)")
               .Define("DVertex_thrust_angle",  "FCCAnalyses::myUtils::get_DVertex_thrusthemis_angle(VertexObject, RecoPartPIDAtVertex, EVT_thrust)")
               ###0 == negative angle==max energy , 1 == positive angle == min energy
               .Define("Vertex_thrusthemis_emin",    "FCCAnalyses::myUtils::get_Vertex_thrusthemis(Vertex_thrust_angle, 1)")
               .Define("Vertex_thrusthemis_emax",    "FCCAnalyses::myUtils::get_Vertex_thrusthemis(Vertex_thrust_angle, 0)")

               .Define("EVT_ThrustEmin_NDV", "float(FCCAnalyses::myUtils::get_Npos(DVertex_thrust_angle))")
               .Define("EVT_ThrustEmax_NDV", "float(FCCAnalyses::myUtils::get_Nneg(DVertex_thrust_angle))")

               .Define("EVT_Thrust_Mag",  "EVT_thrust.at(0)")
               .Define("EVT_Thrust_X",    "EVT_thrust.at(1)")
               .Define("EVT_Thrust_XErr", "EVT_thrust.at(2)")
               .Define("EVT_Thrust_Y",    "EVT_thrust.at(3)")
               .Define("EVT_Thrust_YErr", "EVT_thrust.at(4)")
               .Define("EVT_Thrust_Z",    "EVT_thrust.at(5)")
               .Define("EVT_Thrust_ZErr", "EVT_thrust.at(6)")


               .Define("DV_tracks", "FCCAnalyses::myUtils::get_pseudotrack(VertexObject,RecoPartPIDAtVertex)")

               .Define("DV_d0",            "FCCAnalyses::myUtils::get_trackd0(DV_tracks)")
               .Define("DV_z0",            "FCCAnalyses::myUtils::get_trackz0(DV_tracks)")

               #############################################
               ##       Add candidate related value       ##
               ############################################# 
               #.Define(f"SigCandidates_mass",    f"FCCAnalyses::myUtils::getFCCAnalysesComposite_mass(SigCandidates)")
               #.Define(f"SigCandidates_q",       f"FCCAnalyses::myUtils::getFCCAnalysesComposite_charge(SigCandidates)")
               #.Define(f"SigCandidates_vertex",  f"FCCAnalyses::myUtils::getFCCAnalysesComposite_vertex(SigCandidates)")
               #.Define(f"SigCandidates_mcvertex",f"FCCAnalyses::myUtils::getFCCAnalysesComposite_mcvertex(SigCandidates,VertexObject)")
               #.Define(f"SigCandidates_truth",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_truthMatch(TruthMatching)") # KPiCandidates -> TruthMatching
               #.Define(f"SigCandidates_px",      f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates,0)")
               #.Define(f"SigCandidates_py",      f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates,1)")
               #.Define(f"SigCandidates_pz",      f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates,2)")
               #.Define(f"SigCandidates_p",       f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates,-1)")
               #.Define(f"SigCandidates_B",       f"FCCAnalyses::myUtils::getFCCAnalysesComposite_B(SigCandidates, VertexObject, RecoPartPIDAtVertex)")
               
               #.Define(f"SigCandidates_track",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_track(SigCandidates, VertexObject)")
               #.Define(f"SigCandidates_d0",      f"FCCAnalyses::myUtils::get_trackd0(SigCandidates_track)")
               #.Define(f"SigCandidates_z0",      f"FCCAnalyses::myUtils::get_trackz0(SigCandidates_track)")

               #.Define(f"SigCandidates_anglethrust", f"FCCAnalyses::myUtils::getFCCAnalysesComposite_anglethrust(SigCandidates, EVT_thrust)")
               #.Define("CUT_hasCandEmin",           f"FCCAnalyses::myUtils::has_anglethrust_emin(SigCandidates_anglethrust)")
               #.Filter("CUT_hasCandEmin>0")
               
               #.Define(f"SigCandidates_h1px",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 0, 0)")
               #.Define(f"SigCandidates_h1py",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 0, 1)")
               #.Define(f"SigCandidates_h1pz",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 0, 2)")
               #.Define(f"SigCandidates_h1p",    f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 0, -1)")
               #.Define(f"SigCandidates_h1q",    f"FCCAnalyses::myUtils::getFCCAnalysesComposite_q(SigCandidates, VertexObject, RecoPartPIDAtVertex, 0)")
               #.Define(f"SigCandidates_h1m",    f"FCCAnalyses::myUtils::getFCCAnalysesComposite_mass(SigCandidates, VertexObject, RecoPartPIDAtVertex, 0)")
               #.Define(f"SigCandidates_h1type", f"FCCAnalyses::myUtils::getFCCAnalysesComposite_type(SigCandidates, VertexObject, RecoPartPIDAtVertex, 0)")
               #.Define(f"SigCandidates_h1d0",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_d0(SigCandidates, VertexObject, 0)")
               #.Define(f"SigCandidates_h1z0",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_z0(SigCandidates, VertexObject, 0)")
               
               #.Define(f"SigCandidates_h2px",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 1, 0)")
               #.Define(f"SigCandidates_h2py",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 1, 1)")
               #.Define(f"SigCandidates_h2pz",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 1, 2)")
               #.Define(f"SigCandidates_h2p",    f"FCCAnalyses::myUtils::getFCCAnalysesComposite_p(SigCandidates, VertexObject, RecoPartPIDAtVertex, 1, -1)")
               #.Define(f"SigCandidates_h2q",    f"FCCAnalyses::myUtils::getFCCAnalysesComposite_q(SigCandidates, VertexObject, RecoPartPIDAtVertex, 1)")
               #.Define(f"SigCandidates_h2m",    f"FCCAnalyses::myUtils::getFCCAnalysesComposite_mass(SigCandidates, VertexObject, RecoPartPIDAtVertex, 1)")
               #.Define(f"SigCandidates_h2type", f"FCCAnalyses::myUtils::getFCCAnalysesComposite_type(SigCandidates, VertexObject, RecoPartPIDAtVertex, 1)")
               #.Define(f"SigCandidates_h2d0",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_d0(SigCandidates, VertexObject, 1)")
               #.Define(f"SigCandidates_h2z0",   f"FCCAnalyses::myUtils::getFCCAnalysesComposite_z0(SigCandidates, VertexObject, 1)")
               
               #.Define(f"TrueSig_vertex",        f"FCCAnalyses::myUtils::get_trueVertex(MCVertexObject,Particle,Particle0, {child_pdgid}, {parent_pdgid})")
               #.Define(f"TrueSig_track",         f"FCCAnalyses::myUtils::get_truetrack(TrueSig_vertex, MCVertexObject, Particle)")
               #.Define(f"TrueSig_d0",            f"FCCAnalyses::myUtils::get_trackd0(TrueSig_track)")
               #.Define(f"TrueSig_z0",            f"FCCAnalyses::myUtils::get_trackz0(TrueSig_track)")
           )
        
        if not training:
            df4 = (df3
               # Build MVA 
               .Define("MVAVec", ROOT.computeModel, ("EVT_ThrustEmin_E",        "EVT_ThrustEmax_E",
                                                     "EVT_ThrustEmin_Echarged", "EVT_ThrustEmax_Echarged",
                                                     "EVT_ThrustEmin_Eneutral", "EVT_ThrustEmax_Eneutral",
                                                     "EVT_ThrustEmin_Ncharged", "EVT_ThrustEmax_Ncharged",
                                                     "EVT_ThrustEmin_Nneutral", "EVT_ThrustEmax_Nneutral",
                                                     "EVT_NtracksPV",           "EVT_NVertex",
                                                     f"EVT_NSig",                "EVT_ThrustEmin_NDV",
                                                     "EVT_ThrustEmax_NDV",      "EVT_dPV2DVmin",
                                                     "EVT_dPV2DVmax",           "EVT_dPV2DVave"))
               .Define("EVT_MVA1", "MVAVec.at(0)")
               .Filter(MVAFilter)
            )
        else:
            df4 = df3

        branchList = ROOT.vector('string')()
        desired_branches = [
                "MC_PDG","MC_M1","MC_M2","MC_n","MC_D1","MC_D2","MC_D3","MC_D4",
                "MC_p","MC_pt","MC_px","MC_py","MC_pz","MC_eta","MC_phi",
                "MC_orivtx_x","MC_orivtx_y","MC_orivtx_z", 
                "MC_endvtx_x", "MC_endvtx_y", "MC_endvtx_z", "MC_e","MC_m",
                "EVT_ThrustEmin_E",          "EVT_ThrustEmax_E",
                "EVT_ThrustEmin_Echarged",   "EVT_ThrustEmax_Echarged",
                "EVT_ThrustEmin_Eneutral",   "EVT_ThrustEmax_Eneutral",
                "EVT_ThrustEmin_N",          "EVT_ThrustEmax_N",                
                "EVT_ThrustEmin_Ncharged",   "EVT_ThrustEmax_Ncharged",
                "EVT_ThrustEmin_Nneutral",   "EVT_ThrustEmax_Nneutral",
                "EVT_ThrustEmin_NDV",        "EVT_ThrustEmax_NDV",
                "EVT_Thrust_Mag",
                "EVT_Thrust_X",  "EVT_Thrust_XErr",
                "EVT_Thrust_Y",  "EVT_Thrust_YErr",
                "EVT_Thrust_Z",  "EVT_Thrust_ZErr",

                "EVT_NtracksPV", "EVT_NVertex", #f"EVT_NSig",
                
                "EVT_dPV2DVmin","EVT_dPV2DVmax","EVT_dPV2DVave",

                "MC_Vertex_x", "MC_Vertex_y", "MC_Vertex_z", 
                "MC_Vertex_ntrk", "MC_Vertex_n",
                
                "MC_Vertex_PDG","MC_Vertex_PDGmother","MC_Vertex_PDGgmother",
                
                "Vertex_x", "Vertex_y", "Vertex_z",
                "Vertex_xErr", "Vertex_yErr", "Vertex_zErr",
                "Vertex_isPV", "Vertex_ntrk", "Vertex_chi2", "Vertex_n",
                "Vertex_thrust_angle", "Vertex_thrusthemis_emin", "Vertex_thrusthemis_emax",

                "Vertex_d2PV", "Vertex_d2PVx", "Vertex_d2PVy", "Vertex_d2PVz",
                "Vertex_d2PVErr", "Vertex_d2PVxErr", "Vertex_d2PVyErr", "Vertex_d2PVzErr",
                "Vertex_mass",
                "DV_d0","DV_z0",
                
                #f"TrueSig_vertex", f"TrueSig_d0", f"TrueSig_z0", 
                
                #f"SigCandidates_mass", f"SigCandidates_vertex", f"SigCandidates_mcvertex", f"SigCandidates_B",
                #f"SigCandidates_truth",
                #f"SigCandidates_px", f"SigCandidates_py", f"SigCandidates_pz", f"SigCandidates_p", f"SigCandidates_q",
                #f"SigCandidates_d0",  f"SigCandidates_z0",f"SigCandidates_anglethrust",
                
                #f"SigCandidates_h1px", f"SigCandidates_h1py", f"SigCandidates_h1pz",
                #f"SigCandidates_h1p", f"SigCandidates_h1q", f"SigCandidates_h1m", f"SigCandidates_h1type",
                #f"SigCandidates_h1d0", f"SigCandidates_h1z0",
                #f"SigCandidates_h2px", f"SigCandidates_h2py", f"SigCandidates_h2pz",
                #f"SigCandidates_h2p", f"SigCandidates_h2q", f"SigCandidates_h2m", f"SigCandidates_h2type",
                #f"SigCandidates_h2d0", f"SigCandidates_h2z0",
                ]
        if not training:
            desired_branches.append("EVT_MVA1")
        for branchName in desired_branches:
            branchList.push_back(branchName)
        df4.Snapshot("events", self.outname, branchList)

if __name__ == "__main__":

    print("Initialising...")

    import argparse
    parser = argparse.ArgumentParser(description="Applies preselection cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input',nargs="+", required=True, help='Select the input file(s).')
    parser.add_argument('-o', '--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('-m', '--MVA_cut', default = None, type=float, help='Choose the MVA cut.')
    parser.add_argument('-n', '--n_events', default = -1, type=int, help='Choose the number of events to process.')
    parser.add_argument('--n_cpus', default = 8, type=int, help='Choose the number of cpus to use.')
    parser.add_argument('--mva', default="", type=str, help='Path to the trained MVA ROOT file.')
    parser.add_argument('-t', '--training', default=False, action="store_const", const=True, help="prepare tuples for BDT training.")
    args = parser.parse_args()

    if not args.training:
        if not os.path.exists( args.mva ):
            raise RuntimeError(f"Looking for an MVA file that doesn't exist {args.mva}")
        # TODO make the above take the BDT name according to the decay
        ROOT.gInterpreter.ProcessLine(f'''
        TMVA::Experimental::RBDT<> bdt("BDT", "{args.mva}");
        computeModel = TMVA::Experimental::Compute<18, float>(bdt);
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

    import time
    start_time = time.time()
    analysis = analysis(input_files, args.output, n_cpus)
    analysis.run(n_events, args.MVA_cut, args.training)

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
