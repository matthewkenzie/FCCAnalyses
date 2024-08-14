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
    "stage1": {
        "Bs2NuNu": {
            'eff': 0.931654, 
            'sel': 931654,
            'proc': 1000000,
            'aveeff': 0.931654, 
            'stdeff': 0.0005513111644071647},
        "bb" : {
            'eff': 0.08436945703319386, 
            'sel': 3709784,
            'proc': 43970699,
            'aveeff': 0.0843684355706641, 
            'stdeff': 0.0003160042609441379},
        "cc": {
            'eff': 0.08457565235334542,
            'sel': 4233143,
            'proc': 50051556,
            'aveeff': 0.08457507303477463,
            'stdeff': 0.0002669246409145492},
        "ss": {
            'eff': 0.11353,
            'sel': 0,
            'proc': 0,
            'aveeff': 0,
            'stdeff': 0},
        "ud": {
            'eff': 0.08848,
            'sel': 0,
            'proc': 0,
            'aveeff': 0,
            'stdeff': 0}
    }
}

variable_plot_titles = {}

PIDs = {
    "kaon": {
        "K0L":         130,
        "K0Lbar":     -130,
        "K0S":         310,
        "K0Sbar":     -310,
        "K0":          311,
        "K0bar":      -311,
        "K+":          321,
        "K-":         -321,
        "K0star":      313,
        "K0starbar":  -313,
        "K+star":      323,
        "K-star":     -323,
    }
}

# Samples of post_stage0 analysis
samples_poststage0 = [
    "Bs2NuNu_fromrecp",
    "bb_fromrecp",
    "cc_fromrecp",
    "ss_fromrecp",
    "ud_fromrecp",
]
