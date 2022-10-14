import uproot
import pandas
import argparse
import matplotlib.pyplot as plt
parser = argparse.ArgumentParser(description="Applies preselection cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--inclusive_bbbar',nargs="+", required=True, help='Select the input file(s).')
parser.add_argument('--inclusive_ccbar',nargs="+", required=True, help='Select the input file(s).')
parser.add_argument('--inclusive_qqbar',nargs="+", required=True, help='Select the input file(s).')
parser.add_argument('--signal',nargs="+", required=True, help='Select the input file(s).')
parser.add_argument('--output', type=str, required=True, help='Select the output file.')
parser.add_argument('--var', type=str, default="EVT_MVA1", help='Plot variable')
parser.add_argument('--bins', type=int, default=500, help='Number of bins')
parser.add_argument('--range', type=str, default='(0,1)', help='Plot range')
parser.add_argument('--xtitle', type=str, default='BDT Response', help='Plot x label')
#parser.add_argument('--decay', type=str, required=True, help='Select the reconstructed decay.')
args = parser.parse_args()

def load_df(input_files):
    mva_df = pandas.DataFrame()
    for input_name in input_files:
        with uproot.open(input_name) as inf:
            mva_df = pandas.concat([mva_df, inf["events"][args.var].array(library="pd")])
    return mva_df

dfs = {"signal" : load_df(args.signal),
       "bbbar_df": load_df(args.inclusive_bbbar),
       "qqbar_df": load_df(args.inclusive_qqbar),
       "ccbar_df": load_df(args.inclusive_ccbar),
}

hist_setting = {
    "signal": {"hist_type": "bar", "colour": "orange"},
    "bbbar_df": {"hist_type": "step", "colour": "red"},
    "qqbar_df": {"hist_type": "step", "colour": "green"},
    "ccbar_df": {"hist_type": "step", "colour": "blue"},
}

plt.tight_layout()
#for _name, df in {"signal": dfs["bbbar_df"]}.items():
for name, df in dfs.items():
    rng = args.range.replace('(','').replace(')','').replace('[','').replace(']','').split(',')
    rng = (float(rng[0]), float(rng[1]) )
    plt.hist(df, bins=args.bins, range=rng, density=True, alpha = 0.5, color = hist_setting[name]["colour"], edgecolor=hist_setting[name]["colour"], histtype=hist_setting[name]["hist_type"], label=name)
plt.yscale('log')
plt.legend(loc="upper center")
plt.xlabel(args.xtitle)
plt.ylabel("Normalised Counts")
plt.savefig(args.output, dpi=2000)

# python ./scripts/mva_plot.py --inclusive_bbbar ./output/stage1/Bd2KstNuNu/p8_ee_Zbb_ecm91/inclusive/0.root --inclusive_ccbar ./output/stage1/Bd2KstNuNu/p8_ee_Zcc_ecm91/inclusive/119.root --inclusive_qqbar ./output/stage1/Bd2KstNuNu/p8_ee_Zuds_ecm91/inclsive/100.root --signal ./output/stage1/Bd2KstNuNu/p8_ee_Zbb_ecm91/signal/0.root --output ./Bd2KstNuNu_test_plot.png
# python ./scripts/mva_plot.py --inclusive_bbbar ./output/stage1/Bs2PhiNuNu/p8_ee_Zbb_ecm91/inclusive/100.root --inclusive_ccbar ./output/stage1/Bs2PhiNuNu/p8_ee_Zcc_ecm91/inclusive/10.root --inclusive_qqbar ./output/stage1/Bs2PhiNuNu/p8_ee_Zuds_ecm91/inclusive/0.root --signal ./output/stage1/Bs2PhiNuNu/p8_ee_Zbb_ecm91/signal/0.root --output ./Bs2PhiNuNu_test_plot.png
