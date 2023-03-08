import argparse
import json
import pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import interpolate
from iminuit import cost, Minuit

import config as cfg

def read_eff(fname):
    with open(fname) as f:
        dic = json.load(f)
    return dic['efficiency']

def run(args):

    bfs = cfg.branching_fractions

    dfs = {}
    effs_bfs = {}
    events = {}

    for mode in bfs.keys():
        dfs[mode] = pd.read_pickle(f"{args.path}/{mode}/inclusive.pkl")
        eff = read_eff(f"{args.path_eff}/{mode}/inclusive/eff.json")
        effs_bfs[mode] = eff*bfs[mode]
        events[mode] = len( dfs[mode] )

    # add a eff * bf weight
    for mode in bfs.keys():
        dfs[mode]['xswt'] = effs_bfs[mode] / max( effs_bfs.values() ) / events[mode]
        dfs[mode]['mode'] = mode

    df = pd.concat( [ dfs[mode] for mode in bfs.keys() ] )

    # loose cuts
    cut = f'(EVT_ThrustDiff_E{cfg.energy_difference_cut}) & (EVT_MVA1>{cfg.mva1_min}) & (EVT_MVA2>{cfg.mva2_min})'
    df = df.query(cut)

    # add transforms
    df['log_EVT_MVA1'] = -np.log( 1. - df['EVT_MVA1'] )
    df['log_EVT_MVA2'] = -np.log( 1. - df['EVT_MVA2'] )

    for bins, mva in zip([cfg.mva1_spl_bins, cfg.mva2_spl_bins],['EVT_MVA1', 'EVT_MVA2']):

        fig, ax = plt.subplots()

        if mva=='EVT_MVA1':
            xmin = -np.log( 1. - cfg.mva1_min )
            xmax = -np.log( 1. - cfg.mva1_max )
        else:
            xmin = -np.log( 1. - cfg.mva2_min )
            xmax = -np.log( 1. - cfg.mva2_max )

        ax.hist( [ df[ df['mode']==mode ][f'log_{mva}'] for mode in bfs.keys() ] , stacked=True, bins=bins, range=(xmin,xmax), weights=[ df[ df['mode']==mode ]['xswt'] for mode in bfs.keys() ], label=[ cfg.label_map[mode] for mode in bfs.keys() ] )

        w, xe = np.histogram( df[f'log_{mva}'], bins=bins, range=(xmin,xmax), weights=df['xswt'] )
        w2, xe = np.histogram( df[f'log_{mva}'], bins=bins, range=(xmin, xmax), weights=df['xswt']**2 )
        cx = 0.5 * ( xe[1:] + xe[:-1] )
        err = w2**0.5

        ax.errorbar( cx, w, yerr=err, fmt='ko', ms=2, label='Background sum' )

        splwt = 1./err

        # cubic spline
        spline = interpolate.splrep( cx, w, w=splwt )

        xvals = np.linspace(xmin, xmax, 1000)
        spl_vals = interpolate.splev( xvals, spline )

        ax.plot( xvals, spl_vals, c='r', label='Spline Fit' )

        # expon fit
        #def nll(
        #def model(x, N, p):
            #return N * np.exp(-p*x)

        #c = cost.LeastSquares(cx, w, err, model)
        #mi = Minuit(c, N=sum(w), p=0.1)
        #mi.migrad()
        #mi.hesse()


        ax.set_xlabel(f"$-\log(1-{mva.replace('EVT_','')})$")
        ax.set_xlim(xmin, xmax)

        ax.legend()
        fig.tight_layout()
        fig.savefig(args.output_plot.replace('.pdf',f'_{mva}.pdf').replace('.png',f'_{mva}.png'))

        with open(args.output.replace('.pkl',f'_{mva}.pkl'), 'wb') as f:
            pickle.dump(spline, f)

    print(df)


def main():
    parser = argparse.ArgumentParser(description='Make background splines for efficiency calculation')
    parser.add_argument("--path", type=str, required=True, help="Path to pkl location e.g. /storage/epp2/phutmn/FCC/FCCAnalyses/examples/FCCee/flavour/b2snunu/output/root/mva_st2_pkl/Bd2KstNuNu")
    parser.add_argument("--path_eff", type=str, required=True, help="Path to eff location")
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('--output_plot', type=str, required=True, help='Select the output file.')

    args = parser.parse_args()

    run(args)

if __name__ == '__main__':
    main()

