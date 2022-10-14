from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--decay", type=str, required=True, choices=["Bd2KstNuNu","Bs2PhiNuNu"], help="Decay mode")
args = parser.parse_args()

import glob
import uproot

import config as cfg

def sel_eff( files ):

    assert( len(files)>0 )
    processed = 0
    selected  = 0

    for f in files:
        with uproot.open(f) as inf:
            processed += int( inf["metadata"]["eventsProcessed"].array(library='np')[0] )
            selected  += inf["events"].num_entries

    efficiency = selected/processed
    return selected, processed, efficiency

# estimate number of signal
nz = 1

# Number of Z's expected
N_Z = float(nz) * 1e12
BF_Zbb = cfg.branching_fractions['p8_ee_Zbb_ecm91']
BF_Zcc = cfg.branching_fractions['p8_ee_Zcc_ecm91']
BF_Zqq = cfg.branching_fractions['p8_ee_Zuds_ecm91']
# Factor 2 from having 2 b quarks from Z
N_bb = N_Z * BF_Zbb * 2
N_cc = N_Z * BF_Zbb * 2
N_qq = N_Z * BF_Zqq * 2

# Number of signal
Ns = N_bb * cfg.prod_frac[args.decay] * cfg.signal_bfs[args.decay]

print(args.decay, "number of signal before cuts", Ns)
print(args.decay, "number of background before cuts")

# Number of background
for name, bkg in zip(['bb','cc','uds'],[N_bb, N_cc, N_qq]):
    print('   ', name+':', bkg)

path_st1_eff = f'/storage/epp2/phutmn/FCC/FCCAnalyses/examples/FCCee/flavour/b2snunu/output/root/stage1/{args.decay}'
path_st2_eff = f'/storage/epp2/phutmn/FCC/FCCAnalyses/examples/FCCee/flavour/b2snunu/output/root/mva_st2/{args.decay}'
path_pkl = f'/storage/epp2/phutmn/FCC/FCCAnalyses/examples/FCCee/flavour/b2snunu/output/root/mva_st2_pkl/{args.decay}'

effs = {}

for mode, path in zip( ['sig','bb','cc','qq'], [ 'p8_ee_Zbb_ecm91/signal', 'p8_ee_Zbb_ecm91/inclusive' ,'p8_ee_Zcc_ecm91/inclusive', 'p8_ee_Zuds_ecm91/inclusive'] ):

    st1_files = glob.glob( f'{path_st1_eff}/{path}/*.root' )
    st2_files = glob.glob( f'{path_st2_eff}/{path}/*.root' )

    st1_eff = sel_eff( st1_files )
    st2_eff = sel_eff( st2_files )

    print(mode, ':', 'st1:', st1_eff, ', st2:', st2_eff)

    pkl =


