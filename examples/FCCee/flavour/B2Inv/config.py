# processList to pass to `fccanalysis run`
processList = {
    "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu": {"fraction": 0.5, "chunks": 20},
    "p8_ee_Zbb_ecm91": {"fraction": 0.05, "chunks": 100},
    "p8_ee_Zcc_ecm91": {"fraction": 0.05, "chunks": 100},
    "p8_ee_Zss_ecm91": {"fraction": 0.05, "chunks": 100},
    "p8_ee_Zud_ecm91": {"fraction": 0.05, "chunks": 100}
}

# Options to pass to `fccanalysis run`
fccana_opts = {
    "prodTag"      : "FCCee/winter2023/IDEA",
    "outputDir"    : "/r01/lhcb/rrm42/fcc/stage1_postBDT/",
    "analysisName" : "B2Inv",
    "nCPUs"        : 8,
    "runBatch"     : True,
    "batchQueue"   : "workday",
    "compGroup"    : "group_u_FCC.local_gen",
    #"testFile"     : "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu/events_026683563.root",
    "testFile"     : "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zbb_ecm91/events_000083138.root",
    #"testFile"     : "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zcc_ecm91/events_000046867.root",
    #"testFile"     : "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zss_ecm91/events_000099129.root",
    #"testFile"     : "root://eospublic.cern.ch//eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zud_ecm91/events_000071896.root",
    "path2yaml"    : "/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv/bdt.yaml",
    "outBranchList": "stage1-vars",
}

# TMVA options
bdt_opts = {
    "training"     : False,
    "mvaPath"      : "/r01/lhcb/rrm42/fcc/bdt1out/tmva1.root",
    "mvaTreeName"  : "bdt",
    "mvaCut"       : 0.2,
    "mvaBranchList": "bdt1-training-vars"
}

samples = [ 
    "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu",
    "p8_ee_Zbb_ecm91",
    "p8_ee_Zcc_ecm91",
    "p8_ee_Zss_ecm91",
    "p8_ee_Zud_ecm91",
]

stage0dir_in = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'
stage0dir_out = '/r01/lhcb/rrm42/fcc/post_stage0/'

sample_allocations = {
    "signal" : ["p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu"],
    "background": ["p8_ee_Zbb_ecm91", "p8_ee_Zcc_ecm91", "p8_ee_Zss_ecm91", "p8_ee_Zud_ecm91"],
    "bb only": ["p8_ee_Zbb_ecm91"]
}

titles = {
    "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu": r"$B_s^0 \to \nu \bar{\nu}$",
    "p8_ee_Zbb_ecm91": r"$Z \to b \bar{b}$",
    "p8_ee_Zcc_ecm91": r"$Z \to c \bar{c}$",
    "p8_ee_Zss_ecm91": r"$Z \to s \bar{s}$",
    "p8_ee_Zud_ecm91": r"$Z \to q \bar{q}$, $q \in [u,d]$",
}

# from PDG
# B production fractions
prod_frac = {"Bu": 0.43,
             "Bd": 0.43,
             "Bs": 0.096,
             "Lb": 0.037,
             "Bc": 0.0004
            }


# from PDG (value, error)
# Z branching fractions
# Z->ss = (Z->dd+ss+bb)/3 * 3 - Z->bb / 2
# Z->uu/cc = 2 * (11.6 +/- 0.6) = 23.2 +/- 1.2
# Z->dd/ss/bb = 3 * (15.6 +/- 0.4) = 46.8 +/- 1.2
branching_fractions = {
    "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu": (1,0), # a dummy value
    "p8_ee_Zbb_ecm91": (0.1512, 0.0005),
    "p8_ee_Zcc_ecm91": (0.1203, 0.0021),
    "p8_ee_Zss_ecm91": (0.1560, 0.0040),
    "p8_ee_Zud_ecm91": (0.1560+0.1160, (0.6**2+0.4**2)**0.5),
}

efficiencies = {
    "unity": {
        "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu": 1,
        "p8_ee_Zbb_ecm91": 1,
        "p8_ee_Zcc_ecm91": 1,
        "p8_ee_Zss_ecm91": 1,
        "p8_ee_Zud_ecm91": 1,
    },
    "presel": {
        "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu": 0.931654,
        "p8_ee_Zbb_ecm91": 0.0843694570,
        "p8_ee_Zcc_ecm91": 0.0845756524,
        "p8_ee_Zss_ecm91": 0.11353,
        "p8_ee_Zud_ecm91": 0.08848,
    },
    "presel+bdt1>0.2": {
        "p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu": 0.929954,
        "p8_ee_Zbb_ecm91": 0.026951298076923078,
        "p8_ee_Zcc_ecm91": 0.01976784759011348,
        "p8_ee_Zss_ecm91": 0.016586942271539597,
        "p8_ee_Zud_ecm91": 0.007837139711792738,
    },
}
