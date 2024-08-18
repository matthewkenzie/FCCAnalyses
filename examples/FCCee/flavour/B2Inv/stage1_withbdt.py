import os
import argparse
import sys
sys.path.append('/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv')

import ROOT
import config as cfg

testFile = "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu/events_026683563.root"


class RDFanalysis():
    def __init__(self, cmdline_args):
        parser = argparse.ArgumentParser(description="Applies preselection cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.ana_args, _ = parser.parse_known_args(cmdline_args['unknown'])

# Optional: output directory, default is local running directory
        self.output_dir = cfg.outputs

        # Mandatory: List of processes to run over
        self.process_list = {
            "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu" : {"fraction": 0.5, "chunks":15},
            "p8_ee_Zbb_ecm91" : {"fraction": 0.1, "chunks": 50},
            "p8_ee_Zcc_ecm91" : {"fraction": 0.1, "chunks": 50},
            "p8_ee_Zss_ecm91" : {"fraction": 0.1, "chunks": 50},
            "p8_ee_Zud_ecm91" : {"fraction": 0.1, "chunks": 50},
        }

        # Mandatory: Production tag when running over the centrally produced
        # samples, this points to the yaml files for getting sample statistics
        self.prod_tag = 'FCCee/winter2023/IDEA/'

        # Optional: analysisName, default is ''
        # self.analysis_name = 'My Analysis'

        # Optional:number of threads to run on, default is 'all available'
        self.nCPUs = 8

        # Optional: running on HTCondor, default is False
        self.run_batch = True
        #self.batch_queue = "workday"
        #self.comp_group = "group_u_FCC.local_gen"
        self.test_file = testFile
        
        # List of branches
        self.branchList = cfg.stage1_branchList
        # List of BDT features used in the model
        self.BDTbranchList = cfg.bdt_branchList

        # Load BDT model
        if not self.ana_args.training:
            ROOT.gInterpreter.ProcessLine(f'''
            TMVA::Experimental::RBDT<> bdt("bdt", "{args.mvapath}");
            computeModel = TMVA::Experimental::Compute<{len(self.BDTbranchList)}, float> (bdt);
            ''')

    def analyzers(self, df):
        df2 = (
            df
            #############################################
            ##          Aliases for # in python        ##
            #############################################
            .Alias("MCRecoAssociationsRec", "MCRecoAssociations#0.index") # points to ReconstructedParticles
            .Alias("MCRecoAssociationsGen", "MCRecoAssociations#1.index") # points to Particle
            .Alias("ParticleParents",       "Particle#0.index") # gen particle parents
            .Alias("ParticleChildren",      "Particle#1.index") # gen particle children


            # --------------------------------------- #
            #        List of intermediates used       #
            #
            # MC_ee
            # MC_Z
            # MC_qq
            # MC_fromRP -- needs RecoParticlesPIDAtVertex
            # MC_VertexObject --- only to seed Rec_VertexObject
            # Rec_PrimaryTracks
            # Rec_PrimaryVertexObject
            # Rec_VertexObject
            # -- RecoParticlesPID : NOT USED EXCEPT TO DEFINE RECOPARTICLESPIDATVERTEX
            # RecoParticlesPIDAtVertex
            # True_ParentInfo
            # EVT_ThrustInfo
            # EVT_ThrustInfoMin_N
            # EVT_ThrustInfoMax_N
            # EVT_ThrustInfoMin_E
            # EVT_ThrustInfoMax_E
            # SecondaryVertexThrustAngle
            # EVT_EminPartInfo
            # EVT_EmaxPartInfo
            # --------------------------------------- #
            #############################################
            ##               MC Particles              ##
            #############################################
            # --------------------------------------- #
            #             MC intermediates            #
            # --------------------------------------- #
            # Pythia8 generatorStatus
            # 21 - incoming particles of hardest process (e+ e- beams)
            # 22 - intermediate particles of hardest process (Z)
            # 23 - outgoing particles of hardest process (quark pair produced from Z)
            #  1 - final-state particles
            .Define("MC_ee",          "MCParticle::sel_genStatus(21)(Particle)")
            .Define("MC_Z",           "MCParticle::sel_genStatus(22)(Particle)")
            .Define("MC_qq",          "MCParticle::sel_genStatus(23)(Particle)")
            # .Define("MC_fromRP") --- needs RecoParticlesPIDAtVertex so defined later

            # --------------------------------------- #
            #           MC e+ e- variables            #
            # --------------------------------------- #
            .Define("MCem_e",         "(MCParticle::get_e(MC_ee)).at(0)")
            .Define("MCem_m",         "(MCParticle::get_mass(MC_ee)).at(0)")
            .Define("MCem_q",         "(MCParticle::get_charge(MC_ee)).at(0)")
            .Define("MCem_p",         "(MCParticle::get_p(MC_ee)).at(0)")
            .Define("MCem_pt",        "(MCParticle::get_pt(MC_ee)).at(0)")
            .Define("MCem_px",        "(MCParticle::get_px(MC_ee)).at(0)")
            .Define("MCem_py",        "(MCParticle::get_py(MC_ee)).at(0)")
            .Define("MCem_pz",        "(MCParticle::get_pz(MC_ee)).at(0)")
            .Define("MCem_eta",       "(MCParticle::get_eta(MC_ee)).at(0)")
            .Define("MCem_phi",       "(MCParticle::get_phi(MC_ee)).at(0)")
            .Define("MCem_orivtx_x",  "(MCParticle::get_vertex_x(MC_ee)).at(0)")
            .Define("MCem_orivtx_y",  "(MCParticle::get_vertex_y(MC_ee)).at(0)")
            .Define("MCem_orivtx_z",  "(MCParticle::get_vertex_z(MC_ee)).at(0)")
            .Define("MCep_e",         "(MCParticle::get_e(MC_ee)).at(1)")
            .Define("MCep_m",         "(MCParticle::get_mass(MC_ee)).at(1)")
            .Define("MCep_q",         "(MCParticle::get_charge(MC_ee)).at(1)")
            .Define("MCep_p",         "(MCParticle::get_p(MC_ee)).at(1)")
            .Define("MCep_pt",        "(MCParticle::get_pt(MC_ee)).at(1)")
            .Define("MCep_px",        "(MCParticle::get_px(MC_ee)).at(1)")
            .Define("MCep_py",        "(MCParticle::get_py(MC_ee)).at(1)")
            .Define("MCep_pz",        "(MCParticle::get_pz(MC_ee)).at(1)")
            .Define("MCep_eta",       "(MCParticle::get_eta(MC_ee)).at(1)")
            .Define("MCep_phi",       "(MCParticle::get_phi(MC_ee)).at(1)")
            .Define("MCep_orivtx_x",  "(MCParticle::get_vertex_x(MC_ee)).at(1)")
            .Define("MCep_orivtx_y",  "(MCParticle::get_vertex_y(MC_ee)).at(1)")
            .Define("MCep_orivtx_z",  "(MCParticle::get_vertex_z(MC_ee)).at(1)")

            # --------------------------------------- #
            #           MC Z boson variables          #
            # --------------------------------------- #
            .Define("MCZ_e",          "(MCParticle::get_e(MC_Z)).at(0)")
            .Define("MCZ_m",          "(MCParticle::get_mass(MC_Z)).at(0)")
            .Define("MCZ_q",          "(MCParticle::get_charge(MC_Z)).at(0)")
            .Define("MCZ_p",          "(MCParticle::get_p(MC_Z)).at(0)")
            .Define("MCZ_pt",         "(MCParticle::get_pt(MC_Z)).at(0)")
            .Define("MCZ_px",         "(MCParticle::get_px(MC_Z)).at(0)")
            .Define("MCZ_py",         "(MCParticle::get_py(MC_Z)).at(0)")
            .Define("MCZ_pz",         "(MCParticle::get_pz(MC_Z)).at(0)")
            .Define("MCZ_eta",        "(MCParticle::get_eta(MC_Z)).at(0)")
            .Define("MCZ_phi",        "(MCParticle::get_phi(MC_Z)).at(0)")
            .Define("MCZ_orivtx_x",   "(MCParticle::get_vertex_x(MC_Z)).at(0)")
            .Define("MCZ_orivtx_y",   "(MCParticle::get_vertex_y(MC_Z)).at(0)")
            .Define("MCZ_orivtx_z",   "(MCParticle::get_vertex_z(MC_Z)).at(0)")

            # --------------------------------------- #
            #            MC qqbar variables           #
            # --------------------------------------- #
            .Define("MCq1_PDG",       "(MCParticle::get_pdg(MC_qq)).at(0)")
            .Define("MCq1_e",         "(MCParticle::get_e(MC_qq)).at(0)")
            .Define("MCq1_m",         "(MCParticle::get_mass(MC_qq)).at(0)")
            .Define("MCq1_q",         "(MCParticle::get_charge(MC_qq)).at(0)")
            .Define("MCq1_p",         "(MCParticle::get_p(MC_qq)).at(0)")
            .Define("MCq1_pt",        "(MCParticle::get_pt(MC_qq)).at(0)")
            .Define("MCq1_px",        "(MCParticle::get_px(MC_qq)).at(0)")
            .Define("MCq1_py",        "(MCParticle::get_py(MC_qq)).at(0)")
            .Define("MCq1_pz",        "(MCParticle::get_pz(MC_qq)).at(0)")
            .Define("MCq1_eta",       "(MCParticle::get_eta(MC_qq)).at(0)")
            .Define("MCq1_phi",       "(MCParticle::get_phi(MC_qq)).at(0)")
            .Define("MCq1_orivtx_x",  "(MCParticle::get_vertex_x(MC_qq)).at(0)")
            .Define("MCq1_orivtx_y",  "(MCParticle::get_vertex_y(MC_qq)).at(0)")
            .Define("MCq1_orivtx_z",  "(MCParticle::get_vertex_z(MC_qq)).at(0)")
            .Define("MCq2_PDG",       "(MCParticle::get_pdg(MC_qq)).at(1)")
            .Define("MCq2_e",         "(MCParticle::get_e(MC_qq)).at(1)")
            .Define("MCq2_m",         "(MCParticle::get_mass(MC_qq)).at(1)")
            .Define("MCq2_q",         "(MCParticle::get_charge(MC_qq)).at(1)")
            .Define("MCq2_p",         "(MCParticle::get_p(MC_qq)).at(1)")
            .Define("MCq2_pt",        "(MCParticle::get_pt(MC_qq)).at(1)")
            .Define("MCq2_px",        "(MCParticle::get_px(MC_qq)).at(1)")
            .Define("MCq2_py",        "(MCParticle::get_py(MC_qq)).at(1)")
            .Define("MCq2_pz",        "(MCParticle::get_pz(MC_qq)).at(1)")
            .Define("MCq2_eta",       "(MCParticle::get_eta(MC_qq)).at(1)")
            .Define("MCq2_phi",       "(MCParticle::get_phi(MC_qq)).at(1)")
            .Define("MCq2_orivtx_x",  "(MCParticle::get_vertex_x(MC_qq)).at(1)")
            .Define("MCq2_orivtx_y",  "(MCParticle::get_vertex_y(MC_qq)).at(1)")
            .Define("MCq2_orivtx_z",  "(MCParticle::get_vertex_z(MC_qq)).at(1)")

            # --------------------------------------- #
            #           Rec_vtx intermediates         #
            # --------------------------------------- #
            # Get collection of tracks consistent with a PV (i.e. not downstream Ks, Lb etc. tracks)
            # using the get_PrimaryTracks() method with a beam spot constraint under the following parameters
            # bsc_sigma(x,y,z) = (4.5, 20e-3, 300)
            # bsc_(x,y,z) = (0,0,0) 
            .Define("Rec_PrimaryTracks",        "VertexFitterSimple::get_PrimaryTracks( EFlowTrack_1, true, 4.5, 20e-3, 300, 0., 0., 0. )")
            # Run the vertex fit using only the primary tracks with the same beamspot constraint
            .Define("Rec_PrimaryVertexObject",  "VertexFitterSimple::VertexFitter_Tk( 1, Rec_PrimaryTracks, true, 4.5, 20e-3, 300 )")
            .Define("Rec_PrimaryVertex",        "Rec_PrimaryVertexObject.vertex")
            # function to get all reco vertices (uses MC vertex to seed the vertexing)
            .Define("MC_VertexObject",   "myUtils::get_MCVertexObject(Particle, ParticleParents)")
            .Define("Rec_VertexObject",         "myUtils::get_VertexObject(MC_VertexObject, ReconstructedParticles, EFlowTrack_1, MCRecoAssociationsRec, MCRecoAssociationsGen)")
            # --------------------------------------- #
            #            Rec intermediates            #
            # --------------------------------------- #
            # actually add the PID hypothesis info to the RecParticles (based on MC truth)
            # ie we assume perfect PID here
            .Define("RecoParticlesPID",          "myUtils::PID(ReconstructedParticles, MCRecoAssociationsRec, MCRecoAssociationsGen, Particle)")
            # now update reco momentum based on the rec vertex
            .Define("RecoParticlesPIDAtVertex",  "myUtils::get_RP_atVertex(RecoParticlesPID, Rec_VertexObject)")


            #############################################
            ##         Reconstructed Particles         ##
            #############################################
            .Define("Rec_n",         "ReconstructedParticle::get_n(RecoParticlesPIDAtVertex)")
            .Define("Rec_type",      "ReconstructedParticle::get_type(RecoParticlesPIDAtVertex)")
            .Define("Rec_indvtx",    "myUtils::get_Vertex_fromRP(RecoParticlesPIDAtVertex, Rec_VertexObject)")
            .Define("Rec_customid",  "ReconstructedParticle::get_customid(RecoParticlesPIDAtVertex)")
            .Define("Rec_e",         "ReconstructedParticle::get_e(RecoParticlesPIDAtVertex)")
            .Define("Rec_m",         "ReconstructedParticle::get_mass(RecoParticlesPIDAtVertex)")
            .Define("Rec_q",         "ReconstructedParticle::get_charge(RecoParticlesPIDAtVertex)")
            .Define("Rec_p",         "ReconstructedParticle::get_p(RecoParticlesPIDAtVertex)")
            .Define("Rec_pt",        "ReconstructedParticle::get_pt(RecoParticlesPIDAtVertex)")
            .Define("Rec_px",        "ReconstructedParticle::get_px(RecoParticlesPIDAtVertex)")
            .Define("Rec_py",        "ReconstructedParticle::get_py(RecoParticlesPIDAtVertex)")
            .Define("Rec_pz",        "ReconstructedParticle::get_pz(RecoParticlesPIDAtVertex)")
            .Define("Rec_eta",       "ReconstructedParticle::get_eta(RecoParticlesPIDAtVertex)")
            .Define("Rec_phi",       "ReconstructedParticle::get_phi(RecoParticlesPIDAtVertex)")

            # --------------------------------------- #
            #   MC variables of truth matched RecoP   #
            # --------------------------------------- #
            .Define("MC_fromRP",           "myUtils::get_MCObject_fromRP(MCRecoAssociationsRec, MCRecoAssociationsGen, RecoParticlesPIDAtVertex, Particle)")
            
            .Define("Rec_true_PDG",        "MCParticle::get_pdg(MC_fromRP)")
            .Define("Rec_true_e",          "MCParticle::get_e(MC_fromRP)")
            .Define("Rec_true_m",          "MCParticle::get_mass(MC_fromRP)")
            .Define("Rec_true_q",          "MCParticle::get_charge(MC_fromRP)")
            .Define("Rec_true_p",          "MCParticle::get_p(MC_fromRP)")
            .Define("Rec_true_pt",         "MCParticle::get_pt(MC_fromRP)")
            .Define("Rec_true_px",         "MCParticle::get_px(MC_fromRP)")
            .Define("Rec_true_py",         "MCParticle::get_py(MC_fromRP)")
            .Define("Rec_true_pz",         "MCParticle::get_pz(MC_fromRP)")
            .Define("Rec_true_eta",        "MCParticle::get_eta(MC_fromRP)")
            .Define("Rec_true_phi",        "MCParticle::get_phi(MC_fromRP)")
            .Define("Rec_true_orivtx_x",   "MCParticle::get_vertex_x(MC_fromRP)")
            .Define("Rec_true_orivtx_y",   "MCParticle::get_vertex_y(MC_fromRP)")
            .Define("Rec_true_orivtx_z",   "MCParticle::get_vertex_z(MC_fromRP)")
            
            # MCParticle history
            .Define("True_ParentInfo",     "myUtils::get_MCParentandGParent_fromRP(MCRecoAssociationsRec, MCRecoAssociationsGen, ParticleParents, RecoParticlesPIDAtVertex, Particle)")
            .Define("Rec_true_M1",         "True_ParentInfo.at(0)")
            .Define("Rec_true_M2",         "True_ParentInfo.at(1)")
            .Define("Rec_true_M1ofM1",     "True_ParentInfo.at(2)")
            .Define("Rec_true_M2ofM1",     "True_ParentInfo.at(3)")
            .Define("Rec_true_M1ofM2",     "True_ParentInfo.at(4)")
            .Define("Rec_true_M2ofM2",     "True_ParentInfo.at(5)")

            # --------------------------------------- #
            #            EVT intermediates            #
            # --------------------------------------- #
            .Define("EVT_ThrustInfoNoPointing",     'Algorithms::minimize_thrust("Minuit2","Migrad")(Rec_px, Rec_py, Rec_pz)')
            .Define("EVT_ThrustCosThetaNoPointing", "Algorithms::getAxisCosTheta(EVT_ThrustInfoNoPointing, Rec_px, Rec_py, Rec_pz)")
            .Define("EVT_ThrustInfo",               "Algorithms::getThrustPointing(1.)(EVT_ThrustCosThetaNoPointing, Rec_e, EVT_ThrustInfoNoPointing)")
            
            # Remaining Rec variables
            .Define("Rec_thrustCosTheta",  "Algorithms::getAxisCosTheta(EVT_ThrustInfo, Rec_px, Rec_py, Rec_pz)")
            .Define("Rec_in_hemisEmin",    "myUtils::get_RP_inHemis(1)(Rec_thrustCosTheta)")
            .Define("Rec_in_hemisEmax",    "myUtils::get_RP_inHemis(0)(Rec_thrustCosTheta)") # Not saved because redundant but used for other variables


            #############################################
            ##       Reconstructed PrimaryVertex       ##
            #############################################
            # Get collection of all tracks and use this to reconstruct the PV
            .Define("Rec_PV_ntracks",  "Rec_PrimaryTracks.size()")
            
            .Define("Rec_PV_x",        "Rec_PrimaryVertex.position.x")
            .Define("Rec_PV_y",        "Rec_PrimaryVertex.position.y")
            .Define("Rec_PV_z",        "Rec_PrimaryVertex.position.z")

            # Track information
            .Define("Rec_track_n",       "ReconstructedParticle2Track::getTK_n(EFlowTrack_1)")
            .Define("Rec_track_d0",      "ReconstructedParticle2Track::getRP2TRK_D0(RecoParticlesPIDAtVertex, EFlowTrack_1)")
            .Define("Rec_track_normd0",  "ReconstructedParticle2Track::getRP2TRK_D0_sig(RecoParticlesPIDAtVertex, EFlowTrack_1)")
            .Define("Rec_track_z0",      "ReconstructedParticle2Track::getRP2TRK_Z0(RecoParticlesPIDAtVertex, EFlowTrack_1)")
            .Define("Rec_track_normz0",  "ReconstructedParticle2Track::getRP2TRK_Z0_sig(RecoParticlesPIDAtVertex, EFlowTrack_1)")

            #############################################
            ##           Reconstructed Vertex          ##
            #############################################
            .Define("Rec_vtx_n",               "int(Rec_VertexObject.size())")
            .Define("Rec_vtx_indRP",           "myUtils::get_Vertex_ind(Rec_VertexObject)")
            .Define("Rec_vtx_chi2",            "myUtils::get_Vertex_chi2(Rec_VertexObject)")
            .Define("Rec_vtx_isPV",            "myUtils::get_Vertex_isPV(Rec_VertexObject)")

            ################FILTER#######################
            .Filter("ROOT::VecOps::Any(Rec_vtx_isPV > 0)")

            .Define("Rec_vtx_ntracks",         "myUtils::get_Vertex_ntracks(Rec_VertexObject)")
            .Define("Rec_vtx_m",               "myUtils::get_Vertex_mass(Rec_VertexObject, RecoParticlesPIDAtVertex)")
            .Define("Rec_vtx_x",               "myUtils::get_Vertex_x(Rec_VertexObject)")
            .Define("Rec_vtx_y",               "myUtils::get_Vertex_y(Rec_VertexObject)")
            .Define("Rec_vtx_z",               "myUtils::get_Vertex_z(Rec_VertexObject)")
            .Define("Rec_vtx_xerr",            "myUtils::get_Vertex_xErr(Rec_VertexObject)")
            .Define("Rec_vtx_yerr",            "myUtils::get_Vertex_yErr(Rec_VertexObject)")
            .Define("Rec_vtx_zerr",            "myUtils::get_Vertex_zErr(Rec_VertexObject)")

            .Define("Rec_vtx_d2PV",            "myUtils::get_Vertex_d2PV(Rec_VertexObject,-1)")
            .Define("Rec_vtx_d2PV_min",        "myUtils::get_dPV2DV_min(Rec_vtx_d2PV)")
            .Define("Rec_vtx_d2PV_max",        "myUtils::get_dPV2DV_max(Rec_vtx_d2PV)")
            .Define("Rec_vtx_d2PV_ave",        "myUtils::get_dPV2DV_ave(Rec_vtx_d2PV)")
            .Define("Rec_vtx_d2PV_x",          "myUtils::get_Vertex_d2PV(Rec_VertexObject, 0)")
            .Define("Rec_vtx_d2PV_y",          "myUtils::get_Vertex_d2PV(Rec_VertexObject, 1)")
            .Define("Rec_vtx_d2PV_z",          "myUtils::get_Vertex_d2PV(Rec_VertexObject, 2)")
            .Define("Rec_vtx_d2PV_err",        "myUtils::get_Vertex_d2PVError(Rec_VertexObject,-1)")
            .Define("Rec_vtx_d2PV_xerr",       "myUtils::get_Vertex_d2PVError(Rec_VertexObject, 0)")
            .Define("Rec_vtx_d2PV_yerr",       "myUtils::get_Vertex_d2PVError(Rec_VertexObject, 1)")
            .Define("Rec_vtx_d2PV_zerr",       "myUtils::get_Vertex_d2PVError(Rec_VertexObject, 2)")
            .Define("Rec_vtx_normd2PV",        "Rec_vtx_d2PV / Rec_vtx_d2PV_err")
            .Define("Rec_vtx_normd2PV_min",    "myUtils::get_dPV2DV_min(Rec_vtx_normd2PV)")
            .Define("Rec_vtx_normd2PV_max",    "myUtils::get_dPV2DV_max(Rec_vtx_normd2PV)")
            .Define("Rec_vtx_normd2PV_ave",    "myUtils::get_dPV2DV_ave(Rec_vtx_normd2PV)")
            .Define("Rec_vtx_normd2PV_x",      "Rec_vtx_d2PV_x / Rec_vtx_d2PV_xerr")
            .Define("Rec_vtx_normd2PV_y",      "Rec_vtx_d2PV_y / Rec_vtx_d2PV_yerr")
            .Define("Rec_vtx_normd2PV_z",      "Rec_vtx_d2PV_z / Rec_vtx_d2PV_zerr")
            # Vertex relations to thrust 
            .Define("Rec_vtx_thrustCosTheta",  "myUtils::get_Vertex_thrusthemis_angle(Rec_VertexObject, RecoParticlesPIDAtVertex, EVT_ThrustInfo)") 
            # Flag vertex in max or min hemisphere
            .Define("Rec_vtx_in_hemisEmin",    "myUtils::get_Vertex_thrusthemis(Rec_vtx_thrustCosTheta, 1)")
            .Define("Rec_vtx_in_hemisEmax",    "myUtils::get_Vertex_thrusthemis(Rec_vtx_thrustCosTheta, 0)")

            #############################################
            ##               Reco Thrust               ##
            #############################################
            .Define("EVT_Thrust_mag",          "EVT_ThrustInfo.at(0)")
            .Define("EVT_Thrust_x",            "EVT_ThrustInfo.at(1)")
            .Define("EVT_Thrust_xerr",         "EVT_ThrustInfo.at(2)")
            .Define("EVT_Thrust_y",            "EVT_ThrustInfo.at(3)")
            .Define("EVT_Thrust_yerr",         "EVT_ThrustInfo.at(4)")
            .Define("EVT_Thrust_z",            "EVT_ThrustInfo.at(5)")
            .Define("EVT_Thrust_zerr",         "EVT_ThrustInfo.at(6)")
            
            #############################################
            ##         Emin and Emax Hemispheres       ##
            #############################################
            # --------------------------------------- #
            #           Hemis intermediates           #
            # --------------------------------------- #
            .Define("EVT_ThrustInfoMax_N",     "Algorithms::getAxisN(0)(Rec_thrustCosTheta, Rec_q)")
            .Define("EVT_ThrustInfoMin_N",     "Algorithms::getAxisN(1)(Rec_thrustCosTheta, Rec_q)")
            .Define("EVT_ThrustInfoMax_E",     "Algorithms::getAxisEnergy(0)(Rec_thrustCosTheta, Rec_q, Rec_e)")
            .Define("EVT_ThrustInfoMin_E",     "Algorithms::getAxisEnergy(1)(Rec_thrustCosTheta, Rec_q, Rec_e)")
            
            .Define("EVT_hemisEmin_e",         "EVT_ThrustInfoMin_E.at(0)")

            ################FILTER#######################
            .Filter("EVT_hemisEmin_e < 40")

            .Define("EVT_hemisEmin_eCharged",  "EVT_ThrustInfoMin_E.at(1)")
            .Define("EVT_hemisEmin_eNeutral",  "EVT_ThrustInfoMin_E.at(2)")
            .Define("EVT_hemisEmin_n",         "EVT_ThrustInfoMin_N.at(0)")
            .Define("EVT_hemisEmin_nCharged",  "EVT_ThrustInfoMin_N.at(1)")
            .Define("EVT_hemisEmin_nNeutral",  "EVT_ThrustInfoMin_N.at(2)")
            .Define("EVT_hemisEmax_e",         "EVT_ThrustInfoMax_E.at(0)")
            .Define("EVT_hemisEmax_eCharged",  "EVT_ThrustInfoMax_E.at(1)")
            .Define("EVT_hemisEmax_eNeutral",  "EVT_ThrustInfoMax_E.at(2)")
            .Define("EVT_hemisEmax_n",         "EVT_ThrustInfoMax_N.at(0)")
            .Define("EVT_hemisEmax_nCharged",  "EVT_ThrustInfoMax_N.at(1)")
            .Define("EVT_hemisEmax_nNeutral",  "EVT_ThrustInfoMax_N.at(2)")
            
            # Count secondary vertices in each hemisphere
            .Define("SecondaryVertexThrustAngle",  "myUtils::get_DVertex_thrusthemis_angle(Rec_VertexObject, RecoParticlesPIDAtVertex, EVT_ThrustInfo)")
            .Define("EVT_hemisEmin_nDV",     "myUtils::get_Npos(SecondaryVertexThrustAngle)")
            .Define("EVT_hemisEmax_nDV",     "myUtils::get_Nneg(SecondaryVertexThrustAngle)")
            
            #############################################
            ##      Hemisphere Particle variables      ##
            #############################################
            # --------------------------------------- #
            #           Hemis intermediates           #
            # --------------------------------------- #
            .Define("EVT_EminPartInfo",  "myUtils::get_RP_HemisInfo(RecoParticlesPIDAtVertex, Rec_VertexObject, Rec_in_hemisEmin)")
            .Define("EVT_EmaxPartInfo",  "myUtils::get_RP_HemisInfo(RecoParticlesPIDAtVertex, Rec_VertexObject, Rec_in_hemisEmax)")
            
            .Define("EVT_hemisEmin_nLept",                "(EVT_EminPartInfo.at(0)).num")

            ################FILTER#######################
            .Filter("EVT_hemisEmin_nLept == 0")

            .Define("EVT_hemisEmin_nKaon",                "(EVT_EminPartInfo.at(1)).num")
            .Define("EVT_hemisEmin_nPion",                "(EVT_EminPartInfo.at(2)).num")
            # Dont need lepton variable in min hemisphere as number is 0
            #.Define("EVT_hemisEmin_maxeLept",             "(EVT_EminPartInfo.at(0)).maxE")
            .Define("EVT_hemisEmin_maxeKaon",             "(EVT_EminPartInfo.at(1)).maxE")
            .Define("EVT_hemisEmin_maxePion",             "(EVT_EminPartInfo.at(2)).maxE")
            #.Define("EVT_hemisEmin_maxeLept_fromtruePV",  "(EVT_EminPartInfo.at(0)).fromPV")
            .Define("EVT_hemisEmin_maxeKaon_fromtruePV",  "(EVT_EminPartInfo.at(1)).fromPV")
            .Define("EVT_hemisEmin_maxePion_fromtruePV",  "(EVT_EminPartInfo.at(2)).fromPV")
            #.Define("EVT_hemisEmin_maxeLept_ind",         "(EVT_EminPartInfo.at(0)).index")
            .Define("EVT_hemisEmin_maxeKaon_ind",         "(EVT_EminPartInfo.at(1)).index")
            .Define("EVT_hemisEmin_maxePion_ind",         "(EVT_EminPartInfo.at(2)).index")
            
            .Define("EVT_hemisEmax_nLept",                "(EVT_EmaxPartInfo.at(0)).num")
            .Define("EVT_hemisEmax_nKaon",                "(EVT_EmaxPartInfo.at(1)).num")
            .Define("EVT_hemisEmax_nPion",                "(EVT_EmaxPartInfo.at(2)).num")
            .Define("EVT_hemisEmax_maxeLept",             "(EVT_EmaxPartInfo.at(0)).maxE")
            .Define("EVT_hemisEmax_maxeKaon",             "(EVT_EmaxPartInfo.at(1)).maxE")
            .Define("EVT_hemisEmax_maxePion",             "(EVT_EmaxPartInfo.at(2)).maxE")
            .Define("EVT_hemisEmax_maxeLept_fromtruePV",  "(EVT_EmaxPartInfo.at(0)).fromPV")
            .Define("EVT_hemisEmax_maxeKaon_fromtruePV",  "(EVT_EmaxPartInfo.at(1)).fromPV")
            .Define("EVT_hemisEmax_maxePion_fromtruePV",  "(EVT_EmaxPartInfo.at(2)).fromPV")
            .Define("EVT_hemisEmax_maxeLept_ind",         "(EVT_EmaxPartInfo.at(0)).index")
            .Define("EVT_hemisEmax_maxeKaon_ind",         "(EVT_EmaxPartInfo.at(1)).index")
            .Define("EVT_hemisEmax_maxePion_ind",         "(EVT_EmaxPartInfo.at(2)).index")
            
            #############################################
            ##  Thrust hemispheres energy difference   ##
            #############################################
            .Define("EVT_Thrust_deltaE",            "(EVT_hemisEmax_e) - (EVT_hemisEmin_e)")
        )
        if not self.ana_args.training:
            MVAfilter = f"EVT_MVA1 > {self.ana_args.mvacut}"
            df3 = (
                df2
                #############################################
                ##                Build BDT                ##
                #############################################
                .Define("MVAVec",    ROOT.computeModel, self.BDTbranchList)
                .Define("EVT_MVA1",  "MVAVec.at(0)")
                .Filter(MVAFilter)
            )
        else:
            df3 = df2

        return df3

    def output(self):
        desired_branches = self.branchList
        if not self.ana_args.training:
            desired_branches.append("EVT_MVA1")

        return desired_branches

 
