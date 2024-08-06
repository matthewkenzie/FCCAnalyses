#Mandatory: List of processes
processList = {
        'p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu': {'fraction': 0.2, 'chunks': 10},
        'p8_ee_Zbb_ecm91': {'fraction': 0.001, 'chunks': 20},
        'p8_ee_Zcc_ecm91': {'fraction': 0.001, 'chunks': 20},
        'p8_ee_Zss_ecm91': {'fraction': 0.001, 'chunks': 20},
        'p8_ee_Zud_ecm91': {'fraction': 0.001, 'chunks': 20},
        }

#Mandatory: Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics
prodTag     = "FCCee/winter2023/IDEA/"

#Optional: output directory, default is local running directory
#outputDir   = "/r01/lhcb/mkenzie/fcc/B2Inv/stage0_v2"
outputDir = "/r01/lhcb/rrm42/fcc/vertextest"

#Optional: analysisName, default is ""
analysisName = "B2Inv"

#Optional: ncpus, default is 4
#nCPUS       = 8

#Optional running on HTCondor, default is False
#runBatch    = True

#Optional batch queue name when running on HTCondor, default is workday
#batchQueue = "longlunch"

#Optional computing account when running on HTCondor, default is group_u_FCC.local_gen
#compGroup = "group_u_FCC.local_gen"

#Optional test file
testFile = "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu/events_026683563.root"

#Mandatory: RDFanalysis class where the use defines the operations on the TTree
class RDFanalysis():

    #__________________________________________________________
    #Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        df2 = (
            df
            #############################################
            ##          Aliases for # in python        ##
            #############################################
            .Alias("MCRecoAssociationsRec", "MCRecoAssociations#0.index") # points to ReconstructedParticles
            .Alias("MCRecoAssociationsGen", "MCRecoAssociations#1.index") # points to Particle
            .Alias("ParticleParents", "Particle#0.index") # gen particle parents
            .Alias("ParticleChildren", "Particle#1.index") # gen particle children

            #############################################
            ##               MC Particles              ##
            #############################################
            .Define("MC_n",        "MCParticle::get_n(Particle)")
            .Define("MC_genstatus","MCParticle::get_genStatus(Particle)")
            .Define("MC_PDG",      "MCParticle::get_pdg(Particle)")
            .Define("MC_M1",       "myUtils::getMC_parent(0,Particle,ParticleParents)")
            .Define("MC_M2",       "myUtils::getMC_parent(1,Particle,ParticleParents)")
            .Define("MC_D1",       "myUtils::getMC_daughter(0,Particle,ParticleChildren)")
            .Define("MC_D2",       "myUtils::getMC_daughter(1,Particle,ParticleChildren)")
            .Define("MC_D3",       "myUtils::getMC_daughter(2,Particle,ParticleChildren)")
            .Define("MC_D4",       "myUtils::getMC_daughter(3,Particle,ParticleChildren)")
            .Define("MC_p",        "MCParticle::get_p(Particle)")
            .Define("MC_pt",       "MCParticle::get_pt(Particle)")
            .Define("MC_px",       "MCParticle::get_px(Particle)")
            .Define("MC_py",       "MCParticle::get_py(Particle)")
            .Define("MC_pz",       "MCParticle::get_pz(Particle)")
            .Define("MC_e",        "MCParticle::get_e(Particle)")
            .Define("MC_m",        "MCParticle::get_mass(Particle)")
            .Define("MC_q",        "MCParticle::get_charge(Particle)")
            .Define("MC_eta",      "MCParticle::get_eta(Particle)")
            .Define("MC_phi",      "MCParticle::get_phi(Particle)")
            .Define("MC_orivtx_x", "MCParticle::get_vertex_x(Particle)")
            .Define("MC_orivtx_y", "MCParticle::get_vertex_y(Particle)")
            .Define("MC_orivtx_z", "MCParticle::get_vertex_z(Particle)")
            
            #############################################
            ##                MC Vertex                ##
            #############################################
            .Define("MC_PrimaryVertex", "MCParticle::get_EventPrimaryVertex(21)(Particle)")
            .Define("MC_pv_x", "MC_PrimaryVertex.X()") 
            .Define("MC_pv_y", "MC_PrimaryVertex.Y()") 
            .Define("MC_pv_z", "MC_PrimaryVertex.Z()")

            #############################################
            ##             MC ee -> Z -> qq            ##
            #############################################
            ## Use Pythia8 generatorStatus
            ## 21 - incoming particles of hardest process (e+ e- beams)
            ## 22 - intermediate particle(s) of hardest process (Z)
            ## 23 - outgoing particles of hardest process (e.g bbbar or ccbar etc.)
            .Define("MC_ee",          "MCParticle::sel_genStatus(21)(Particle)")
            .Define("MC_Z",           "MCParticle::sel_genStatus(22)(Particle)")
            .Define("MC_qq",          "MCParticle::sel_genStatus(23)(Particle)")
            .Define("MC_em_p",        "(MCParticle::get_p(MC_ee)).at(0)")
            .Define("MC_em_pt",       "(MCParticle::get_pt(MC_ee)).at(0)")
            .Define("MC_em_px",       "(MCParticle::get_px(MC_ee)).at(0)")
            .Define("MC_em_py",       "(MCParticle::get_py(MC_ee)).at(0)")
            .Define("MC_em_pz",       "(MCParticle::get_pz(MC_ee)).at(0)")
            .Define("MC_em_e",        "(MCParticle::get_e(MC_ee)).at(0)")
            .Define("MC_em_m",        "(MCParticle::get_mass(MC_ee)).at(0)")
            .Define("MC_em_q",        "(MCParticle::get_charge(MC_ee)).at(0)")
            .Define("MC_em_eta",      "(MCParticle::get_eta(MC_ee)).at(0)")
            .Define("MC_em_phi",      "(MCParticle::get_phi(MC_ee)).at(0)")
            .Define("MC_em_orivtx_x", "(MCParticle::get_vertex_x(MC_ee)).at(0)")
            .Define("MC_em_orivtx_y", "(MCParticle::get_vertex_y(MC_ee)).at(0)")
            .Define("MC_em_orivtx_z", "(MCParticle::get_vertex_z(MC_ee)).at(0)")
            .Define("MC_ep_p",        "(MCParticle::get_p(MC_ee)).at(1)")
            .Define("MC_ep_pt",       "(MCParticle::get_pt(MC_ee)).at(1)")
            .Define("MC_ep_px",       "(MCParticle::get_px(MC_ee)).at(1)")
            .Define("MC_ep_py",       "(MCParticle::get_py(MC_ee)).at(1)")
            .Define("MC_ep_pz",       "(MCParticle::get_pz(MC_ee)).at(1)")
            .Define("MC_ep_e",        "(MCParticle::get_e(MC_ee)).at(1)")
            .Define("MC_ep_m",        "(MCParticle::get_mass(MC_ee)).at(1)")
            .Define("MC_ep_q",        "(MCParticle::get_charge(MC_ee)).at(1)")
            .Define("MC_ep_eta",      "(MCParticle::get_eta(MC_ee)).at(1)")
            .Define("MC_ep_phi",      "(MCParticle::get_phi(MC_ee)).at(1)")
            .Define("MC_ep_orivtx_x", "(MCParticle::get_vertex_x(MC_ee)).at(1)")
            .Define("MC_ep_orivtx_y", "(MCParticle::get_vertex_y(MC_ee)).at(1)")
            .Define("MC_ep_orivtx_z", "(MCParticle::get_vertex_z(MC_ee)).at(1)")
            .Define("MC_Z_p",         "(MCParticle::get_p(MC_Z)).at(0)")
            .Define("MC_Z_pt",        "(MCParticle::get_pt(MC_Z)).at(0)")
            .Define("MC_Z_px",        "(MCParticle::get_px(MC_Z)).at(0)")
            .Define("MC_Z_py",        "(MCParticle::get_py(MC_Z)).at(0)")
            .Define("MC_Z_pz",        "(MCParticle::get_pz(MC_Z)).at(0)")
            .Define("MC_Z_e",         "(MCParticle::get_e(MC_Z)).at(0)")
            .Define("MC_Z_m",         "(MCParticle::get_mass(MC_Z)).at(0)")
            .Define("MC_Z_q",         "(MCParticle::get_charge(MC_Z)).at(0)")
            .Define("MC_Z_eta",       "(MCParticle::get_eta(MC_Z)).at(0)")
            .Define("MC_Z_phi",       "(MCParticle::get_phi(MC_Z)).at(0)")
            .Define("MC_Z_orivtx_x",  "(MCParticle::get_vertex_x(MC_Z)).at(0)")
            .Define("MC_Z_orivtx_y",  "(MCParticle::get_vertex_y(MC_Z)).at(0)")
            .Define("MC_Z_orivtx_z",  "(MCParticle::get_vertex_z(MC_Z)).at(0)")
            .Define("MC_q1_PDG",      "(MCParticle::get_pdg(MC_qq)).at(0)")
            .Define("MC_q1_p",        "(MCParticle::get_p(MC_qq)).at(0)")
            .Define("MC_q1_pt",       "(MCParticle::get_pt(MC_qq)).at(0)")
            .Define("MC_q1_px",       "(MCParticle::get_px(MC_qq)).at(0)")
            .Define("MC_q1_py",       "(MCParticle::get_py(MC_qq)).at(0)")
            .Define("MC_q1_pz",       "(MCParticle::get_pz(MC_qq)).at(0)")
            .Define("MC_q1_e",        "(MCParticle::get_e(MC_qq)).at(0)")
            .Define("MC_q1_m",        "(MCParticle::get_mass(MC_qq)).at(0)")
            .Define("MC_q1_q",        "(MCParticle::get_charge(MC_qq)).at(0)")
            .Define("MC_q1_eta",      "(MCParticle::get_eta(MC_qq)).at(0)")
            .Define("MC_q1_phi",      "(MCParticle::get_phi(MC_qq)).at(0)")
            .Define("MC_q1_orivtx_x", "(MCParticle::get_vertex_x(MC_qq)).at(0)")
            .Define("MC_q1_orivtx_y", "(MCParticle::get_vertex_y(MC_qq)).at(0)")
            .Define("MC_q1_orivtx_z", "(MCParticle::get_vertex_z(MC_qq)).at(0)")
            .Define("MC_q2_PDG",      "(MCParticle::get_pdg(MC_qq)).at(1)")
            .Define("MC_q2_p",        "(MCParticle::get_p(MC_qq)).at(1)")
            .Define("MC_q2_pt",       "(MCParticle::get_pt(MC_qq)).at(1)")
            .Define("MC_q2_px",       "(MCParticle::get_px(MC_qq)).at(1)")
            .Define("MC_q2_py",       "(MCParticle::get_py(MC_qq)).at(1)")
            .Define("MC_q2_pz",       "(MCParticle::get_pz(MC_qq)).at(1)")
            .Define("MC_q2_e",        "(MCParticle::get_e(MC_qq)).at(1)")
            .Define("MC_q2_m",        "(MCParticle::get_mass(MC_qq)).at(1)")
            .Define("MC_q2_q",        "(MCParticle::get_charge(MC_qq)).at(1)")
            .Define("MC_q2_eta",      "(MCParticle::get_eta(MC_qq)).at(1)")
            .Define("MC_q2_phi",      "(MCParticle::get_phi(MC_qq)).at(1)")
            .Define("MC_q2_orivtx_x", "(MCParticle::get_vertex_x(MC_qq)).at(1)")
            .Define("MC_q2_orivtx_y", "(MCParticle::get_vertex_y(MC_qq)).at(1)")
            .Define("MC_q2_orivtx_z", "(MCParticle::get_vertex_z(MC_qq)).at(1)")

            #############################################
            ##           Find MC Vertices              ##
            #############################################
            .Define("MC_VertexObject", "myUtils::get_MCVertexObject(Particle, ParticleParents)")
            .Define("MC_vtx_x"       , "myUtils::get_MCVertex_x(MC_VertexObject)")
            .Define("MC_vtx_y"       , "myUtils::get_MCVertex_y(MC_VertexObject)")
            .Define("MC_vtx_z"       , "myUtils::get_MCVertex_z(MC_VertexObject)")
            .Define("MC_vtx_n"       , "int(MC_vtx_x.size())")
            .Define("MC_vtx_inds"    , "myUtils::get_MCindMCVertex(MC_VertexObject)")
            .Define("MC_vtx_ntrks"   , "myUtils::get_NTracksMCVertex(MC_VertexObject)")


            #############################################
            ##            Fit the Reco PV              ##
            #############################################
            # Get collection of all tracks and use this to reconstruct the PV
            .Define("ntracks", "ReconstructedParticle2Track::getTK_n(EFlowTrack_1)")
            
            # Get collection of tracks consistent with a PV (i.e. not downstream Ks, Lb etc. tracks)
            # using the get_PrimaryTracks() method with a beam spot constraint under the following parameters
            # bsc_sigma(x,y,z) = (4.5, 20e-3, 300)
            # bsc_(x,y,z) = (0,0,0)
            .Define("Rec_PrimaryTracks", "VertexFitterSimple::get_PrimaryTracks( EFlowTrack_1, true, 4.5, 20e-3, 300, 0., 0., 0. )")
            .Define("Rec_pv_ntracks", "Rec_PrimaryTracks.size()")
            
            # Run the vertex fit using only the primary tracks with the same beamspot constraint
            .Define("Rec_PrimaryVertexObject", "VertexFitterSimple::VertexFitter_Tk( 1, Rec_PrimaryTracks, true, 4.5, 20e-3, 300 )")
            .Define("Rec_PrimaryVertex", "Rec_PrimaryVertexObject.vertex")
            .Define("Rec_pv_x", "Rec_PrimaryVertex.position.x")
            .Define("Rec_pv_y", "Rec_PrimaryVertex.position.y")
            .Define("Rec_pv_z", "Rec_PrimaryVertex.position.z")

            #############################################
            ##               Reco Vertex               ##
            #############################################
            # function to get all reco vertices (uses MC vertex to seed the vertexing)
            .Define("Rec_VertexObject", "FCCAnalyses::myUtils::get_VertexObject(MC_VertexObject,ReconstructedParticles,EFlowTrack_1,MCRecoAssociationsRec,MCRecoAssociationsGen)")
            .Define("Rec_vtx_n",          "int(Rec_VertexObject.size())")
            .Define("Rec_vtx_mcind",      "myUtils::get_Vertex_indMC(Rec_VertexObject)")
            
            # Additionally get list of RecoParticle indices for each vertex
            .Define("Rec_vtx_recoind",    "myUtils::get_Vertex_ind(Rec_VertexObject)")

            .Define("Rec_vtx_x",          "myUtils::get_Vertex_x(Rec_VertexObject)")
            .Define("Rec_vtx_y",          "myUtils::get_Vertex_y(Rec_VertexObject)")
            .Define("Rec_vtx_z",          "myUtils::get_Vertex_z(Rec_VertexObject)")
            .Define("Rec_vtx_xerr",       "myUtils::get_Vertex_xErr(Rec_VertexObject)")
            .Define("Rec_vtx_yerr",       "myUtils::get_Vertex_yErr(Rec_VertexObject)")
            .Define("Rec_vtx_zerr",       "myUtils::get_Vertex_zErr(Rec_VertexObject)")
            .Define("Rec_vtx_chi2",       "myUtils::get_Vertex_chi2(Rec_VertexObject)")
            .Define("Rec_vtx_ispv",       "myUtils::get_Vertex_isPV(Rec_VertexObject)")
            .Define("Rec_vtx_ntrks",      "myUtils::get_Vertex_ntracks(Rec_VertexObject)")
            .Define("Rec_vtx_d2pv",       "myUtils::get_Vertex_d2PV(Rec_VertexObject,-1)")
            .Define("Rec_vtx_d2pv_x",     "myUtils::get_Vertex_d2PV(Rec_VertexObject, 0)")
            .Define("Rec_vtx_d2pv_y",     "myUtils::get_Vertex_d2PV(Rec_VertexObject, 1)")
            .Define("Rec_vtx_d2pv_z",     "myUtils::get_Vertex_d2PV(Rec_VertexObject, 2)")
            .Define("Rec_vtx_d2pv_err",   "myUtils::get_Vertex_d2PVError(Rec_VertexObject,-1)")
            .Define("Rec_vtx_d2pv_xerr",  "myUtils::get_Vertex_d2PVError(Rec_VertexObject, 0)")
            .Define("Rec_vtx_d2pv_yerr",  "myUtils::get_Vertex_d2PVError(Rec_VertexObject, 1)")
            .Define("Rec_vtx_d2pv_zerr",  "myUtils::get_Vertex_d2PVError(Rec_VertexObject, 2)")
            .Define("Rec_vtx_d2pv_sig",   "Rec_vtx_d2pv / Rec_vtx_d2pv_err")
            .Define("Rec_vtx_d2pv_xsig",  "Rec_vtx_d2pv_x / Rec_vtx_d2pv_xerr")
            .Define("Rec_vtx_d2pv_ysig",  "Rec_vtx_d2pv_y / Rec_vtx_d2pv_yerr")
            .Define("Rec_vtx_d2pv_zsig",  "Rec_vtx_d2pv_z / Rec_vtx_d2pv_zerr")
            .Define("Rec_vtx_d2pv_min",   "myUtils::get_dPV2DV_min(Rec_vtx_d2pv)")
            .Define("Rec_vtx_d2pv_max",   "myUtils::get_dPV2DV_max(Rec_vtx_d2pv)")
            .Define("Rec_vtx_d2pv_ave",   "myUtils::get_dPV2DV_ave(Rec_vtx_d2pv)")
            .Define("Rec_vtx_d2pv_sig_min",   "myUtils::get_dPV2DV_min(Rec_vtx_d2pv_sig)")
            .Define("Rec_vtx_d2pv_sig_max",   "myUtils::get_dPV2DV_max(Rec_vtx_d2pv_sig)")
            .Define("Rec_vtx_d2pv_sig_ave",   "myUtils::get_dPV2DV_ave(Rec_vtx_d2pv_sig)")

            #############################################
            ##            Reco Particles               ##
            #############################################
            # actually add the PID hypothesis info to the RecParticles (based on MC truth)
            # ie we assume perfect PID here
            .Define("RecoParticlesPID", "myUtils::PID(ReconstructedParticles, MCRecoAssociationsRec, MCRecoAssociationsGen, Particle)")
            # now update reco momentum based on the rec vertex
            .Define("RecoParticlesPIDAtVertex", "myUtils::get_RP_atVertex(RecoParticlesPID, Rec_VertexObject)")
            .Define("Rec_n",    "ReconstructedParticle::get_n(RecoParticlesPID)")
            .Define("Rec_type", "ReconstructedParticle::get_type(RecoParticlesPID)")
            .Define("Rec_p",    "ReconstructedParticle::get_p(RecoParticlesPID)")
            .Define("Rec_pt",   "ReconstructedParticle::get_pt(RecoParticlesPID)")
            .Define("Rec_px",   "ReconstructedParticle::get_px(RecoParticlesPID)")
            .Define("Rec_py",   "ReconstructedParticle::get_py(RecoParticlesPID)")
            .Define("Rec_pz",   "ReconstructedParticle::get_pz(RecoParticlesPID)")
            .Define("Rec_e",    "ReconstructedParticle::get_e(RecoParticlesPID)")
            .Define("Rec_m",    "ReconstructedParticle::get_mass(RecoParticlesPID)")
            .Define("Rec_q",    "ReconstructedParticle::get_charge(RecoParticlesPID)")
            .Define("Rec_eta",  "ReconstructedParticle::get_eta(RecoParticlesPID)")
            .Define("Rec_phi",  "ReconstructedParticle::get_phi(RecoParticlesPID)")

            # Can also now add the invariant mass at the vertex
            .Define("Rec_vtx_mass", "myUtils::get_Vertex_mass(Rec_VertexObject, RecoParticlesPID)")

            #############################################
            ##           Reco2MC Matching              ##
            #############################################
            .Define("Rec_MC_index", "ReconstructedParticle2MC::getRP2MC_index(MCRecoAssociationsRec,MCRecoAssociationsGen,RecoParticlesPID)")

            #############################################
            ##               Reco Thrust               ##
            #############################################
            .Define("EVT_ThrustInfoNoPointing",     'Algorithms::minimize_thrust("Minuit2","Migrad")(Rec_px, Rec_py, Rec_pz)')
            .Define("EVT_ThrustCosThetaNoPointing", "Algorithms::getAxisCosTheta(EVT_ThrustInfoNoPointing, Rec_px, Rec_py, Rec_pz)")
            .Define("EVT_ThrustInfo",               "Algorithms::getThrustPointing(1.)(EVT_ThrustCosThetaNoPointing, Rec_e, EVT_ThrustInfoNoPointing)")
            .Define("EVT_ThrustCosTheta",           "Algorithms::getAxisCosTheta(EVT_ThrustInfo, Rec_px, Rec_py, Rec_pz)")
            .Define("EVT_Thrust_mag",               "EVT_ThrustInfo.at(0)")
            .Define("EVT_Thrust_x",                 "EVT_ThrustInfo.at(1)")
            .Define("EVT_Thrust_xerr",              "EVT_ThrustInfo.at(2)")
            .Define("EVT_Thrust_y",                 "EVT_ThrustInfo.at(3)")
            .Define("EVT_Thrust_yerr",              "EVT_ThrustInfo.at(4)")
            .Define("EVT_Thrust_z",                 "EVT_ThrustInfo.at(5)")
            .Define("EVT_Thrust_zerr",              "EVT_ThrustInfo.at(6)")
            # hemis0 == negative angle == max energy hemisphere if pointing
            # hemis1 == positive angle == min energy hemisphere if pointing
            .Define("EVT_Thrust_HemisNeg_N",        "Algorithms::getAxisN(0)(EVT_ThrustCosTheta, Rec_q)")
            .Define("EVT_Thrust_HemisPos_N",        "Algorithms::getAxisN(1)(EVT_ThrustCosTheta, Rec_q)")
            .Define("EVT_Thrust_HemisNeg_E",        "Algorithms::getAxisEnergy(0)(EVT_ThrustCosTheta, Rec_q, Rec_e)")
            .Define("EVT_Thrust_HemisPos_E",        "Algorithms::getAxisEnergy(1)(EVT_ThrustCosTheta, Rec_q, Rec_e)")
            
            .Define("EVT_Thrust_Emax_e",            "EVT_Thrust_HemisNeg_E.at(0)")
            .Define("EVT_Thrust_Emax_e_charged",    "EVT_Thrust_HemisNeg_E.at(1)")
            .Define("EVT_Thrust_Emax_e_neutral",    "EVT_Thrust_HemisNeg_E.at(2)")
            .Define("EVT_Thrust_Emax_n",            "EVT_Thrust_HemisNeg_N.at(0)")
            .Define("EVT_Thrust_Emax_n_charged",    "EVT_Thrust_HemisNeg_N.at(1)")
            .Define("EVT_Thrust_Emax_n_neutral",    "EVT_Thrust_HemisNeg_N.at(2)")
            
            .Define("EVT_Thrust_Emin_e",            "EVT_Thrust_HemisPos_E.at(0)")
            .Define("EVT_Thrust_Emin_e_charged",    "EVT_Thrust_HemisPos_E.at(1)")
            .Define("EVT_Thrust_Emin_e_neutral",    "EVT_Thrust_HemisPos_E.at(2)")
            .Define("EVT_Thrust_Emin_n",            "EVT_Thrust_HemisPos_N.at(0)")
            .Define("EVT_Thrust_Emin_n_charged",    "EVT_Thrust_HemisPos_N.at(1)")
            .Define("EVT_Thrust_Emin_n_neutral",    "EVT_Thrust_HemisPos_N.at(2)")
            
            # Vertex relations to thrust 
            .Define("Rec_vtx_thrust_angle",         "myUtils::get_Vertex_thrusthemis_angle(Rec_VertexObject, RecoParticlesPID, EVT_ThrustInfo)") 
            # Flag vertex in max or min hemisphere
            .Define("Rec_vtx_thrust_hemis_emin",    "myUtils::get_Vertex_thrusthemis(Rec_vtx_thrust_angle, 1)")
            .Define("Rec_vtx_thrust_hemis_emax",    "myUtils::get_Vertex_thrusthemis(Rec_vtx_thrust_angle, 0)")
            # Count secondary vertices in each hemisphere
            .Define("SecondaryVertexThrustAngle",   "myUtils::get_DVertex_thrusthemis_angle(Rec_VertexObject, RecoParticlesPID, EVT_ThrustInfo)")
            .Define("EVT_Thrust_Emin_ndv",          "myUtils::get_Npos(SecondaryVertexThrustAngle)")
            .Define("EVT_Thrust_Emax_ndv",          "myUtils::get_Nneg(SecondaryVertexThrustAngle)")
            .Define("Rec_cosrel2thrust",            "myUtils::get_reco_cosrel2thrust(EVT_Thrust_x, EVT_Thrust_y, EVT_Thrust_z, Rec_px, Rec_py, Rec_pz, Rec_p)")

        )
        return df2

    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
            #"MC_n", 
            #"MC_genstatus",
            #"MC_PDG",
            #"MC_M1",
            #"MC_M2",
            #"MC_D1",
            #"MC_D2",
            #"MC_D3",
            #"MC_D4",
            #"MC_p",   
            #"MC_pt",  
            #"MC_px",  
            #"MC_py",  
            #"MC_pz",  
            #"MC_e",   
            #"MC_m",   
            #"MC_q",   
            #"MC_eta", 
            #"MC_phi", 
            #"MC_orivtx_x",
            #"MC_orivtx_y",
            #"MC_orivtx_z",

            #"MC_pv_x",
            #"MC_pv_y",
            #"MC_pv_z",

            #"MC_Z_p",
            #"MC_Z_pt",
            #"MC_Z_px",
            #"MC_Z_py",
            #"MC_Z_pz",
            #"MC_Z_e", 
            #"MC_Z_m", 
            #"MC_Z_q", 
            #"MC_Z_eta",     
            #"MC_Z_phi",     
            #"MC_Z_orivtx_x",
            #"MC_Z_orivtx_y",
            #"MC_Z_orivtx_z",

            #"MC_em_p",
            #"MC_em_pt",
            #"MC_em_px",
            #"MC_em_py",
            #"MC_em_pz",
            #"MC_em_e", 
            #"MC_em_m", 
            #"MC_em_q", 
            #"MC_em_eta",     
            #"MC_em_phi",     
            #"MC_em_orivtx_x",
            #"MC_em_orivtx_y",
            #"MC_em_orivtx_z",

            #"MC_ep_p",
            #"MC_ep_pt",
            #"MC_ep_px",
            #"MC_ep_py",
            #"MC_ep_pz",
            #"MC_ep_e", 
            #"MC_ep_m", 
            #"MC_ep_q", 
            #"MC_ep_eta",     
            #"MC_ep_phi",     
            #"MC_ep_orivtx_x",
            #"MC_ep_orivtx_y",
            #"MC_ep_orivtx_z",
            #
            #"MC_q1_PDG",
            #"MC_q1_p",
            #"MC_q1_pt",
            #"MC_q1_px",
            #"MC_q1_py",
            #"MC_q1_pz",
            #"MC_q1_e", 
            #"MC_q1_m", 
            #"MC_q1_q", 
            #"MC_q1_eta",     
            #"MC_q1_phi",     
            #"MC_q1_orivtx_x",
            #"MC_q1_orivtx_y",
            #"MC_q1_orivtx_z",

            #"MC_q2_PDG",
            #"MC_q2_p",
            #"MC_q2_pt",
            #"MC_q2_px",
            #"MC_q2_py",
            #"MC_q2_pz",
            #"MC_q2_e", 
            #"MC_q2_m", 
            #"MC_q2_q", 
            #"MC_q2_eta",     
            #"MC_q2_phi",     
            #"MC_q2_orivtx_x",
            #"MC_q2_orivtx_y",
            #"MC_q2_orivtx_z",

            #"MC_vtx_n",
            #"MC_vtx_x",
            #"MC_vtx_y",
            #"MC_vtx_z",
            #"MC_vtx_ntrks",
            #"MC_vtx_inds",

            "Rec_n",
            # "Rec_PDG",
            #"Rec_type",
            "Rec_p",   
            "Rec_pt",  
            "Rec_px",  
            "Rec_py",  
            "Rec_pz",  
            "Rec_e",   
            "Rec_m",   
            #"Rec_q",   
            #"Rec_eta", 
            #"Rec_phi",
            #"Rec_MC_index",

            #"ntracks",
            #"Rec_pv_ntracks",
            #"Rec_pv_x",
            #"Rec_pv_y",
            #"Rec_pv_z",
            
            #"Rec_vtx_n",
            #"Rec_vtx_mcind",
            #"Rec_vtx_x",
            #"Rec_vtx_y",
            #"Rec_vtx_z",
            #"Rec_vtx_xerr",
            #"Rec_vtx_yerr",
            #"Rec_vtx_zerr",
            #"Rec_vtx_chi2",
            #"Rec_vtx_ispv",
            #"Rec_vtx_ntrks",
            #"Rec_vtx_mass",
            #"Rec_vtx_d2pv",
            #"Rec_vtx_d2pv_x",
            #"Rec_vtx_d2pv_y",
            #"Rec_vtx_d2pv_z",
            #"Rec_vtx_d2pv_err",
            #"Rec_vtx_d2pv_xerr",
            #"Rec_vtx_d2pv_yerr",
            #"Rec_vtx_d2pv_zerr",
            #"Rec_vtx_d2pv_sig",
            #"Rec_vtx_d2pv_xsig",
            #"Rec_vtx_d2pv_ysig",
            #"Rec_vtx_d2pv_zsig",
            #"Rec_vtx_d2pv_min",
            #"Rec_vtx_d2pv_max",
            #"Rec_vtx_d2pv_ave",
            #"Rec_vtx_d2pv_sig_min",
            #"Rec_vtx_d2pv_sig_max",
            #"Rec_vtx_d2pv_sig_ave",
            #"Rec_vtx_thrust_angle",
            #"Rec_vtx_thrust_hemis_emin",
            #"Rec_vtx_thrust_hemis_emax",

            #"EVT_Thrust_mag",
            "EVT_Thrust_x",
            "EVT_Thrust_y",
            "EVT_Thrust_z",
            "EVT_Thrust_xerr",
            "EVT_Thrust_yerr",
            "EVT_Thrust_zerr",

            #"EVT_Thrust_Emax_e",
            #"EVT_Thrust_Emax_e_charged",
            #"EVT_Thrust_Emax_e_neutral",
            #"EVT_Thrust_Emax_n",
            #"EVT_Thrust_Emax_n_charged",
            #"EVT_Thrust_Emax_n_neutral",
            #"EVT_Thrust_Emax_ndv",
            #"EVT_Thrust_Emin_e",
            #"EVT_Thrust_Emin_e_charged",
            #"EVT_Thrust_Emin_e_neutral",
            #"EVT_Thrust_Emin_n",
            #"EVT_Thrust_Emin_n_charged",
            #"EVT_Thrust_Emin_n_neutral",
            #"EVT_Thrust_Emin_ndv",

            # Test for nan issue
            #"Rec_vtx_recoind",
            "Rec_cosrel2thrust",
        ]
        return branchList


