analysis_scripts = "scripts/"
outputs = "output/"
snakemake_flags = f"{outputs}snakemake_flags/"
logs = f"logs/"
benchmarks = f"benchmarks/"
input_mc = f"{outputs}/input_mc/"

MC = "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/"

event_types = {
    "p8_ee_Zbb_ecm91": ["inclusive", "signal"],
    "p8_ee_Zcc_ecm91": ["inclusive"],
    "p8_ee_Zuds_ecm91": ["inclusive"],
}
decays = ["Bd2KstNuNu", "Bs2PhiNuNu"]#, "Bu2KNuNu"]
samples = set()

decay_to_candidates = {
    "Bd2KstNuNu": "KPi",
    "Bs2PhiNuNu": "KK", # TODO check this https://pdglive.lbl.gov/Particle.action?init=0&node=M004&home=MXXX005
    "Bu2KNuNu": "K",
}

decay_to_pdgids = {
    "Bd2KstNuNu": ["313", "511"],
    "Bs2PhiNuNu": ["333", "531"],
    "Bu2KNuNu": ["321", "521"],
}

branching_fractions = {
    "p8_ee_Zbb_ecm91": 0.1512,
    "p8_ee_Zcc_ecm91": 0.1203,
    "p8_ee_Zuds_ecm91": 0.6991-0.1512-0.1203,
}

training_proportions = {
    "Bd2KstNuNu": {
        "p8_ee_Zbb_ecm91": {
            "signal": 120/1000,
            "inclusive": 60/10000,
        },
        "p8_ee_Zcc_ecm91": {
            "inclusive": 60/10000,
        },
        "p8_ee_Zuds_ecm91": {
            "inclusive": 100/10000,
        },
    },
    "Bs2PhiNuNu": {
        "p8_ee_Zbb_ecm91": {
            "signal": 120/1000,
            "inclusive": 400/10000,
        },
        "p8_ee_Zcc_ecm91": {
            "inclusive": 300/10000,
        },
        "p8_ee_Zuds_ecm91": {
            "inclusive": 1000/10000,
        },
    },
}

tuple_id_blacklist = { # TODO should probably report broken MC
    "Bd2KstNuNu": {
        "p8_ee_Zbb_ecm91": {
            "inclusive": ["255", "230"],
            "signal": [],
        },
        "p8_ee_Zcc_ecm91": {
            "inclusive": [],
        },
        "p8_ee_Zuds_ecm91": {
            "inclusive": [],
        },
    },
    "Bs2PhiNuNu": {
        "p8_ee_Zbb_ecm91": {
            "inclusive": ["255", "230"],
            "signal": [],
        },
        "p8_ee_Zcc_ecm91": {
            "inclusive": [],
        },
        "p8_ee_Zuds_ecm91": {
            "inclusive": [],
        },
    },
    "Bu2KNuNu": {
        "p8_ee_Zbb_ecm91": {
            "inclusive": ["255", "230"],
            "signal": [],
        },
        "p8_ee_Zcc_ecm91": {
            "inclusive": [],
        },
        "p8_ee_Zuds_ecm91": {
            "inclusive": [],
        },
    },
}

def stage1_branches(candidates):
    return [
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

            "EVT_NtracksPV", "EVT_NVertex", f"EVT_N{candidates}",
            
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
            
            f"True{candidates}_vertex", f"True{candidates}_d0", f"True{candidates}_z0", 
            
            f"{candidates}Candidates_mass", f"{candidates}Candidates_vertex", f"{candidates}Candidates_mcvertex", f"{candidates}Candidates_B",
            f"{candidates}Candidates_truth",
            f"{candidates}Candidates_px", f"{candidates}Candidates_py", f"{candidates}Candidates_pz", f"{candidates}Candidates_p", f"{candidates}Candidates_q",
            f"{candidates}Candidates_d0",  f"{candidates}Candidates_z0",f"{candidates}Candidates_anglethrust",
            
            f"{candidates}Candidates_h1px", f"{candidates}Candidates_h1py", f"{candidates}Candidates_h1pz",
            f"{candidates}Candidates_h1p", f"{candidates}Candidates_h1q", f"{candidates}Candidates_h1m", f"{candidates}Candidates_h1type",
            f"{candidates}Candidates_h1d0", f"{candidates}Candidates_h1z0",
            f"{candidates}Candidates_h2px", f"{candidates}Candidates_h2py", f"{candidates}Candidates_h2pz",
            f"{candidates}Candidates_h2p", f"{candidates}Candidates_h2q", f"{candidates}Candidates_h2m", f"{candidates}Candidates_h2type",
            f"{candidates}Candidates_h2d0", f"{candidates}Candidates_h2z0",
            ]

def check_blacklist(target, blacklist):
    for entry in blacklist:
        if f"/{entry}." in target:
            return True
    return False

def blacklister(tuple_ids, blacklist):
    return [tuple_id for tuple_id in tuple_ids if not check_blacklist(str(tuple_id), blacklist)]


def decays_to_fnames(decays):
    return [f"_EvtGen_{decay}" if decay!="inclusive" else "" for decay in decays]

def decay_model_to_fname(decay_model, decay):
    if decay_model=="signal":
        return decays_to_fnames([decay])[0]
    else:
        return decays_to_fnames([decay_model])[0]

def list_to_constraints(l):
    constraints = f"({l[0]}"
    for item in l[1:]:
        constraints = f"{constraints}|{item}"
    constraints = f"{constraints})"
    return constraints