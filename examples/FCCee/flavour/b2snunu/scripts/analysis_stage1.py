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

        ROOT.ROOT.EnableImplicitMT(ncpu)
        ROOT.EnableThreadSafety()
        self.df = ROOT.RDataFrame("events", inputlist)
        print (" init done, about to run")
    #__________________________________________________________
    def run(self):
        #df2 = (self.df.Range(10)
        df2 = (self.df
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
               .Define("MC_D5",  "FCCAnalyses::myUtils::getMC_daughter(4,Particle,Particle1)")
               .Define("MC_D6",  "FCCAnalyses::myUtils::getMC_daughter(5,Particle,Particle1)")
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
               ##        Build Kstz -> KPi  candidates      ##
               #############################################
               .Define("KPiCands",         "FCCAnalyses::myUtils::build_Bd2KstNuNu(VertexObject,RecoPartPIDAtVertex)")
               .Define("KPiCandidates",    "FCCAnalyses::myUtils::add_truthmatched2(KPiCands, Particle, VertexObject, MCRecoAssociations1, ReconstructedParticles, Particle0)")

               #############################################
               ##       Filter Kstz -> KPi candidates      ##
               #############################################
               .Define("EVT_NKPi",              "float(FCCAnalyses::myUtils::getFCCAnalysesComposite_N(KPiCandidates))")
               .Filter("EVT_NKPi>0")


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

               # Build MVA
               #.Define("MVAVec", ROOT.computeModel, ("EVT_ThrustEmin_E",        "EVT_ThrustEmax_E",
               #                                      "EVT_ThrustEmin_Echarged", "EVT_ThrustEmax_Echarged",
               #                                      "EVT_ThrustEmin_Eneutral", "EVT_ThrustEmax_Eneutral",
               #                                      "EVT_ThrustEmin_Ncharged", "EVT_ThrustEmax_Ncharged",
               #                                      "EVT_ThrustEmin_Nneutral", "EVT_ThrustEmax_Nneutral",
               #                                      "EVT_NtracksPV",           "EVT_NVertex",
               #                                      "EVT_NKPi",                "EVT_ThrustEmin_NDV",
               #                                      "EVT_ThrustEmax_NDV",      "EVT_dPV2DVmin",
               #                                      "EVT_dPV2DVmax",           "EVT_dPV2DVave"))
               #.Define("EVT_MVA1", "MVAVec.at(0)")
               #.Filter(MVAFilter) 

               .Define("KPiCandidates_mass",    "FCCAnalyses::myUtils::getFCCAnalysesComposite_mass(KPiCandidates)")
               .Define("KPiCandidates_q",       "FCCAnalyses::myUtils::getFCCAnalysesComposite_charge(KPiCandidates)")
               .Define("KPiCandidates_vertex",  "FCCAnalyses::myUtils::getFCCAnalysesComposite_vertex(KPiCandidates)")
               .Define("KPiCandidates_mcvertex","FCCAnalyses::myUtils::getFCCAnalysesComposite_mcvertex(KPiCandidates,VertexObject)")
               .Define("KPiCandidates_truth",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_truthMatch(KPiCandidates)")
               .Define("KPiCandidates_px",      "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates,0)")
               .Define("KPiCandidates_py",      "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates,1)")
               .Define("KPiCandidates_pz",      "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates,2)")
               .Define("KPiCandidates_p",       "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates,-1)")
               .Define("KPiCandidates_B",       "FCCAnalyses::myUtils::getFCCAnalysesComposite_B(KPiCandidates, VertexObject, RecoPartPIDAtVertex)")

               .Define("KPiCandidates_track",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_track(KPiCandidates, VertexObject)")
               .Define("KPiCandidates_d0",      "FCCAnalyses::myUtils::get_trackd0(KPiCandidates_track)")
               .Define("KPiCandidates_z0",      "FCCAnalyses::myUtils::get_trackz0(KPiCandidates_track)")

               .Define("KPiCandidates_anglethrust", "FCCAnalyses::myUtils::getFCCAnalysesComposite_anglethrust(KPiCandidates, EVT_thrust)")
               .Define("CUT_hasCandEmin",           "FCCAnalyses::myUtils::has_anglethrust_emin(KPiCandidates_anglethrust)")
               .Filter("CUT_hasCandEmin>0")

               .Define("KPiCandidates_h1px",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 0, 0)")
               .Define("KPiCandidates_h1py",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 0, 1)")
               .Define("KPiCandidates_h1pz",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 0, 2)")
               .Define("KPiCandidates_h1p",    "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 0, -1)")
               .Define("KPiCandidates_h1q",    "FCCAnalyses::myUtils::getFCCAnalysesComposite_q(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 0)")
               .Define("KPiCandidates_h1m",    "FCCAnalyses::myUtils::getFCCAnalysesComposite_mass(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 0)")
               .Define("KPiCandidates_h1type", "FCCAnalyses::myUtils::getFCCAnalysesComposite_type(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 0)")
               .Define("KPiCandidates_h1d0",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_d0(KPiCandidates, VertexObject, 0)")
               .Define("KPiCandidates_h1z0",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_z0(KPiCandidates, VertexObject, 0)")

               .Define("KPiCandidates_h2px",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 1, 0)")
               .Define("KPiCandidates_h2py",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 1, 1)")
               .Define("KPiCandidates_h2pz",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 1, 2)")
               .Define("KPiCandidates_h2p",    "FCCAnalyses::myUtils::getFCCAnalysesComposite_p(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 1, -1)")
               .Define("KPiCandidates_h2q",    "FCCAnalyses::myUtils::getFCCAnalysesComposite_q(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 1)")
               .Define("KPiCandidates_h2m",    "FCCAnalyses::myUtils::getFCCAnalysesComposite_mass(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 1)")
               .Define("KPiCandidates_h2type", "FCCAnalyses::myUtils::getFCCAnalysesComposite_type(KPiCandidates, VertexObject, RecoPartPIDAtVertex, 1)")
               .Define("KPiCandidates_h2d0",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_d0(KPiCandidates, VertexObject, 1)")
               .Define("KPiCandidates_h2z0",   "FCCAnalyses::myUtils::getFCCAnalysesComposite_z0(KPiCandidates, VertexObject, 1)")

               .Define("TrueKPiBd_vertex",        "FCCAnalyses::myUtils::get_trueVertex(MCVertexObject,Particle,Particle0, 313, 511)")
               .Define("TrueKPiBd_track",         "FCCAnalyses::myUtils::get_truetrack(TrueKPiBd_vertex, MCVertexObject, Particle)")
               .Define("TrueKPiBd_d0",            "FCCAnalyses::myUtils::get_trackd0(TrueKPiBd_track)")
               .Define("TrueKPiBd_z0",            "FCCAnalyses::myUtils::get_trackz0(TrueKPiBd_track)")

           )
        # select branches for output file
        branchList = ROOT.vector('string')()
        for branchName in [
                
                "MC_PDG","MC_M1","MC_M2","MC_n","MC_D1","MC_D2","MC_D3","MC_D4","MC_D5","MC_D6",
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

                "EVT_NtracksPV", "EVT_NVertex", "EVT_NKPi",

                "EVT_dPV2DVmin","EVT_dPV2DVmax","EVT_dPV2DVave",
                #"EVT_MVA1",

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

                "TrueKPiBd_vertex", "TrueKPiBd_d0", "TrueKPiBd_z0",

                "KPiCandidates_mass", "KPiCandidates_vertex", "KPiCandidates_mcvertex", "KPiCandidates_B",
                "KPiCandidates_truth",
                "KPiCandidates_px", "KPiCandidates_py", "KPiCandidates_pz", "KPiCandidates_p", "KPiCandidates_q",
                "KPiCandidates_d0",  "KPiCandidates_z0","KPiCandidates_anglethrust",

                "KPiCandidates_h1px", "KPiCandidates_h1py", "KPiCandidates_h1pz",
                "KPiCandidates_h1p", "KPiCandidates_h1q", "KPiCandidates_h1m", "KPiCandidates_h1type",
                "KPiCandidates_h1d0", "KPiCandidates_h1z0",
                "KPiCandidates_h2px", "KPiCandidates_h2py", "KPiCandidates_h2pz",
                "KPiCandidates_h2p", "KPiCandidates_h2q", "KPiCandidates_h2m", "KPiCandidates_h2type",
                "KPiCandidates_h2d0", "KPiCandidates_h2z0",

                ]:
            branchList.push_back(branchName)

        #opts = ROOT.RDF.RSnapshotOptions()
        #opts.fCompressionAlgorithm = ROOT.ROOT.kLZ4
        #opts.fCompressionLevel = 3
        #opts.fAutoFlush = -1024*1024*branchList.size()
        #df2.Snapshot("events", self.outname, branchList, opts)
        df2.Snapshot("events", self.outname, branchList)

# example call for standalone file
# python ./scripts/analysis_stage1.py ./test_output/original_stage1_Bd2KstNuNu.root root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_Zbb_ecm91/events_132614370.root





if __name__ == "__main__":

    if len(sys.argv)<3:
        print ("usage:")
        print ("python ",sys.argv[0]," output.root input.root")
        print ("python ",sys.argv[0]," output.root \"inputdir/*.root\"")
        print ("python ",sys.argv[0]," output.root file1.root file2.root file3.root <nevents>")
        sys.exit(3)


    print ("Create dataframe object from ", )
    fileListRoot = ROOT.vector('string')()
    nevents=0

    print("===============================", sys.argv[2])

    if len(sys.argv)==3 and "*" in sys.argv[2]:
        import glob
        filelist = glob.glob(sys.argv[2])
        for fileName in filelist:
            fileListRoot.push_back(fileName)
            print (fileName, " ",)
            print (" ...")


    elif len(sys.argv)>2:
        for i in range(2,len(sys.argv)):
            try:
                nevents=int(sys.argv[i])
                print ("nevents found (will be in the processed events branch in root tree):",nevents)
            except ValueError:
                fileListRoot.push_back(sys.argv[i])
                print (sys.argv[i], " ",)
                print (" ...")


    outfile=sys.argv[1]
    print("output file:  ",outfile)
    if len(outfile.split("/"))>1:
        import os
        os.system("mkdir -p {}".format(outfile.replace(outfile.split("/")[-1],"")))

    if nevents==0:
        for f in fileListRoot:
            tf=ROOT.TFile.Open(str(f),"READ")
            tt=tf.Get("events")
            nevents+=tt.GetEntries()
    print ("nevents ", nevents)

    import time
    start_time = time.time()
    ncpus = 8
    analysis = analysis(fileListRoot, outfile, ncpus)
    analysis.run()

    elapsed_time = time.time() - start_time
    print  ("==============================SUMMARY==============================")
    print  ("Elapsed time (H:M:S)     :  ",time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print  ("Events Processed/Second  :  ",int(nevents/elapsed_time))
    print  ("Total Events Processed   :  ",int(nevents))
    print  ("===================================================================")


    outf = ROOT.TFile( outfile, "update" )
    meta = ROOT.TTree( "metadata", "metadata informations" )
    n = array( "i", [ 0 ] )
    meta.Branch( "eventsProcessed", n, "eventsProcessed/I" )
    n[0]=nevents
    meta.Fill()
    p = ROOT.TParameter(int)( "eventsProcessed", n[0])
    p.Write()
    outf.Write()
    outf.Close()