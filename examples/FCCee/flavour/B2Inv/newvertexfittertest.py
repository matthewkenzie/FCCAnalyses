import sys
import os
import ROOT
from yaml import YAMLError, safe_load
sys.path.append('/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv')
import configtest as cfg

#Mandatory: List of processes
processList = cfg.processList

#Mandatory: Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics
prodTag   = cfg.fccana_opts['prodTag']

#Optional: output directory, default is local running directory
outputDir = cfg.fccana_opts['outputDir'] 

#Optional: analysisName, default is ""
#analysisName = cfg.fccana_opts['analysisName']

#Optional: ncpus, default is 4
nCPUs = cfg.fccana_opts['nCPUs']

#Optional running on HTCondor, default is False
runBatch    = cfg.fccana_opts['runBatch']

#Optional batch queue name when running on HTCondor, default is workday
#batchQueue = cfg.fccana_opts['batchQueue']

#Optional computing account when running on HTCondor, default is group_u_FCC.local_gen
#compGroup = cfg.fccana_opts['compGroup']

#Optional test file
testFile = cfg.fccana_opts['testFile']

print(f"----> INFO: Using config.py file:")
print(f"            /r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv/config.py")
print(f"----> INFO: Using branch names from:")
print(f"            {cfg.fccana_opts['path2yaml']}")

class RDFanalysis():

    def analysers(df):
        df2 = (
            df
            .Alias("MCRecoAssociationsRec", "MCRecoAssociations#0.index") # points to ReconstructedParticles
            .Alias("MCRecoAssociationsGen", "MCRecoAssociations#1.index") # points to Particle
            .Alias("ParticleParents",       "Particle#0.index") # gen particle parents
            .Alias("ParticleChildren",      "Particle#1.index") # gen particle children
            .Define("MC_PDG",               "MCParticle::get_pdg(Particle)")
            .Define("MC_e",                 "MCParticle::get_e(Particle)")
            .Define("MC_m",                 "MCParticle::get_mass(Particle)")


            ##############################
            ## Test
            ##############################
            #### Current method -- Franco Bedeschi, VertexFitterSimple
            .Define("MC_VertexObject",          "myUtils::get_MCVertexObject(Particle, ParticleParents)")
            .Define("Rec_PrimaryTracks",        "VertexFitterSimple::get_PrimaryTracks(EFlowTrack_1, true, 4.5, 20e-3, 300, 0., 0., 0.)")
            .Define("Rec_PrimaryVertexObject",  "VertexFitterSimple::VertexFitter_Tk( 1, Rec_PrimaryTracks, true, 4.5, 20e-3, 300 )")
            .Define("Rec_PrimaryVertex",        "Rec_PrimaryVertexObject.vertex")
            .Define("Rec_VertexObject",         "myUtils::get_VertexObject(MC_VertexObject, ReconstructedParticles, EFlowTrack_1, MCAssociations, MCRecoAssociationsRec, MCRecoAssociationsGen)")

            .Define("Rec_PV_x",                 "Rec_PrimaryVertex.position.x")
            .Define("Rec_PV_y",                 "Rec_PrimaryVertex.position.y")
            .Define("Rec_PV_z",                 "Rec_PrimaryVertex.position.z")
            .Define("Rec_vtx_n",                "Rec_VertexObject.size()")
            .Define("Rec_vtx_x",                "myUtils::get_Vertex_x(Rec_VertexObject)")
            .Define("Rec_vtx_y",                "myUtils::get_Vertex_y(Rec_VertexObject)")
            .Define("Rec_vtx_z",                "myUtils::get_Vertex_z(Rec_VertexObject)")

            #### Test method -- ACTS, VertexFinderActs or VertexFitterActs           
            #.Define("Rec_VertexObjectActs",     "VertexFinderActs::VertexFinderAMVF( EFlowTrack_1 )")
        )
    
    def output():
        branchList = [
            "MC_PDG",
            "MC_e",
            "MC_m",
            "Rec_PV_x",
            "Rec_PV_y",
            "Rec_PV_z",
            "Rec_vtx_n",
            "Rec_vtx_x",
            "Rec_vtx_y",
            "Rec_vtx_z",
        ]

        return branchList