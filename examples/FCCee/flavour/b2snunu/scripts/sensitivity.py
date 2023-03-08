import os
import argparse
import json
import pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate, optimize

from tqdm import tqdm

import config as cfg

def read_eff(fname):
    with open(fname) as f:
        dic = json.load(f)
    return dic['eff']

def get_cut_eff( df, ediff=0, mva1=0, mva2=0, silent=True ):
    N = len(df)
    p = len( df.query( f"(EVT_ThrustDiff_E>{ediff}) & (EVT_MVA1>{mva1}) & (EVT_MVA2>{mva2})" ) )
    if p==0 and not silent:
        print(f'WARNING: cut at ({ediff},{mva1},{mva2}) gives no events')
    return p/N

def getN( df, bfeff, nZ, ediff, mva1, mva2 ):
    n = nZ * bfeff * get_cut_eff( df, ediff, mva1, mva2 )
    return n

def sens_at_given_bf(args, sigbf=1e-5, nZ=3e12, point=None):

    plotdir = args.plot_path
    outdir  = args.output_path
    if point is not None:
        plotdir += f"/p{point}"
        outdir += f"/p{point}"
        os.system(f"mkdir -p {plotdir}")
        os.system(f"mkdir -p {outdir}")

    # backgrounds
    bfs = cfg.branching_fractions
    effs = { mode : read_eff(f"{args.path_eff}/{mode}/inclusive_eff.json") for mode in bfs.keys() }
    dfs  = { mode : pd.read_pickle(f"{args.path}/{mode}/inclusive.pkl") for mode in bfs.keys() }

    # signal
    sigeff = read_eff(f"{args.path_eff}/p8_ee_Zbb_ecm91/signal_eff.json")
    sigdf  = pd.read_pickle(f"{args.path}/p8_ee_Zbb_ecm91/signal.pkl")

    # collated
    bfeff = {}
    for mode in bfs.keys():
        bfeff[mode] = bfs[mode] * effs[mode]
    bfeff[args.channel] = cfg.branching_fractions["p8_ee_Zbb_ecm91"] * cfg.prod_frac[args.channel] * cfg.dec_frac[args.channel] * sigbf * sigeff
    dfs[args.channel] = sigdf

    # EVT_MVA1 vs EVT_MVA2
    xmin, xmax = cfg.mva1_min, 1
    ymin, ymax = cfg.mva2_min, 1

    # do the evaluation in a sparse grid
    grid_df = pd.DataFrame()
    desc = f'Scanning efficiency {cfg.sens_scan_grid_points}x{cfg.sens_scan_grid_points} grid'
    xspace = np.linspace(xmin, xmax, cfg.sens_scan_grid_points)
    yspace = np.linspace(ymin, ymax, cfg.sens_scan_grid_points)
    X, Y = np.meshgrid(xspace, yspace)
    xflat, yflat = X.flatten(), Y.flatten()
    grid_df['MVA1'] = xflat
    grid_df['MVA2'] = yflat
    predN = {}
    for mode in bfeff.keys():
        zflat = np.array( [ getN( dfs[mode], bfeff[mode], nZ, ediff=cfg.ediff_min, mva1=x, mva2=y ) for x, y in tqdm(zip(xflat,yflat), total=len(xflat), ascii=True, desc=f"{mode:15s} - {desc}", position=1, leave=False) ] )
        grid_df[f'N_{mode}'] = zflat
        # now create a bivariate spline to interpolate the grid
        predN[mode] = interpolate.RectBivariateSpline(xspace, yspace, zflat.reshape(X.shape))
        with open(f"{outdir}/N_{mode}_spline.pkl","wb") as f:
            pickle.dump(predN[mode],f)

        fig, ax = plt.subplots()
        cb = ax.imshow(zflat.reshape(X.shape), extent=[xmin,xmax,ymin,ymax], origin='lower', aspect='auto', interpolation='bicubic')
        fig.colorbar(cb)
        ax.set_xlabel('EVT MVA1')
        ax.set_ylabel('EVT MVA2')
        fig.suptitle( f"{cfg.label_map[args.channel]} - {cfg.label_map[mode]}" )
        fig.savefig(f"{plotdir}/predN_{mode}.pdf")
        plt.close()

    # save the grid
    grid_df.to_pickle(f"{outdir}/grid_scan.pkl")

    # now make the FOM in a tighter grid based on the interpolation
    xspace = np.linspace(xmin,xmax, 100)
    yspace = np.linspace(ymin,ymax, 100)
    totB = predN['p8_ee_Zbb_ecm91'](xspace,yspace) + predN['p8_ee_Zcc_ecm91'](xspace,yspace) + predN['p8_ee_Zuds_ecm91'](xspace,yspace)
    totS = predN[args.channel](xspace,yspace)
    with np.errstate(divide='ignore', invalid='ignore'):
        FOM  = np.nan_to_num( totS / np.sqrt(totS + totB) )

    # now make interpolation for the FOM itself
    fFOM = interpolate.RectBivariateSpline(xspace,yspace,FOM)
    with open(f"{outdir}/FOM_spline.pkl","wb") as f:
        pickle.dump(fFOM, f)

    # and find the maximum
    optf = lambda pos: -fFOM.ev(pos[0],pos[1])
    res = optimize.basinhopping( optf, [0.98,0.98] )

    max_fom = fFOM.ev(res.x[0],res.x[1])
    #print('Optimum FOM at', res.x, max_fom )

    fig, ax = plt.subplots()
    im = ax.imshow( FOM, extent=[xmin,xmax,ymin,ymax], origin='lower', aspect='auto', interpolation='bicubic')
    ax.plot( res.x[0], res.x[1], 'rX' )
    cb = fig.colorbar(im)
    cb.set_label( r"$S/\sqrt{S+B}$")
    ax.set_xlabel('EVT MVA1')
    ax.set_ylabel('EVT MVA2')
    fig.suptitle( f"{cfg.label_map[args.channel]}" + r" - $S/\sqrt{S+B}$" )
    fig.savefig(f"{plotdir}/fom.pdf")
    plt.close()

    return res.x[0], res.x[1], max_fom

def run(args):

    bfs = np.logspace(*cfg.sens_scan_bf_range[args.channel],cfg.sens_scan_bf_points)
    foms = []
    for i, bf in tqdm(enumerate(bfs), desc='Scanning BF values', position=0, total=cfg.sens_scan_bf_points, ascii=True):
        x, y, fom = sens_at_given_bf(args, sigbf=bf, point=i+1)
        foms.append(fom)
    foms = np.array(foms)
    df = pd.DataFrame( { 'bfs': bfs, 'foms': foms, 'excl': 1/foms } )
    df.to_pickle( f"{args.output_path}/sensitivity.pkl" )

    xexp = np.linspace(*cfg.sens_scan_bf_range[args.channel],cfg.sens_scan_bf_points)
    _f = interpolate.interp1d(xexp,1/foms,kind='cubic')

    sens = _f( np.log10( cfg.sm_preds[args.channel][0] ) )
    print('Estimate of sensitivty at SM', sens )
    with open(f"{args.output_path}/sensitivity.json","w") as f:
        dic = { "sensitivity" : float(sens) }
        json.dump(dic,f)

    xinter = np.linspace(*cfg.sens_scan_bf_range[args.channel],100)
    y = _f( xinter )
    x = np.logspace(*cfg.sens_scan_bf_range[args.channel],100)
    fig, ax = plt.subplots()
    ax.plot(x, 100*y, 'b-', label='Sensitivity (FCCee)')
    ax.axvline( cfg.best_limits[args.channel], color='g', ls=':', label='Current Limit' )
    ax.axvspan( cfg.sm_preds[args.channel][0]-cfg.sm_preds[args.channel][1], cfg.sm_preds[args.channel][0]+cfg.sm_preds[args.channel][1], ec='none', fc='r', alpha=0.5, label='SM Prediction')
    ax.set_xlabel( f"BF({cfg.label_map[args.channel]})" )
    ax.set_ylabel( r"$\sqrt{S+B}/S$ (%)" )
    ax.legend()
    ax.set_xscale('log')
    fig.tight_layout()
    fig.savefig(f"{args.plot_path}/sensitivity.pdf")

def main():
    default_base_path = "/storage/epp2/phutmn/FCC/FCCAnalyses/examples/FCCee/flavour/b2snunu/output/root"
    parser = argparse.ArgumentParser(description='Make background splines for efficiency calculation')
    parser.add_argument("--channel", type=str, required=True, choices=cfg.stage1_efficiencies.keys(), help="Channel")
    parser.add_argument("--path", type=str, default=None, help="Path to pkl location e.g. /storage/epp2/phutmn/FCC/FCCAnalyses/examples/FCCee/flavour/b2snunu/output/root/mva_st2_pkl/Bd2KstNuNu")
    parser.add_argument("--path_eff", type=str, default=None, help="Path to eff location")
    parser.add_argument("--plot_path", type=str, default=None, help="Plots location")
    parser.add_argument("--output_path", type=str, default=None, help="Output file")
    args = parser.parse_args()

    args.path = args.path or f"{default_base_path}/mva_st2_pkl/{args.channel}"
    args.path_eff = args.path_eff or f"{default_base_path}/efficiency_st2/{args.channel}"
    args.plot_path = args.plot_path or f"plots/{args.channel}"
    args.output_path = args.output_path or f"output/{args.channel}"

    os.system(f"mkdir -p {args.plot_path}")
    os.system(f"mkdir -p {args.output_path}")

    run(args)

if __name__ == '__main__':
    main()

