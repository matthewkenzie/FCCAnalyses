# Needs explicit input files when running `fccanalysis run` as this does not use processList
import os
import sys
sys.path.append('/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv')

import ROOT
import config as cfg
from yaml import safe_load, YAMLError

class RDFanalysis():
    def analysers(df):
        # Preselection cuts
        if cfg.bdt2_opts['preselection'] is not None:
            df2 = (
                df
                .Filter(f"{cfg.bdt2_opts['preselection']}")
            )
        else:
            df2 = df

        if not cfg.bdt2_opts['training']:
            # Read list of feature names used in the BDT from the config YAML file
            with open(cfg.fccana_opts['yamlPath']) as stream:
                try:
                    yaml = safe_load(stream)
                    BDTbranchList = yaml[cfg.bdt2_opts['mvaBranchList']]
                except YAMLError as exc:
                    print(f"----> ERRROR:")
                    print(f"             Could not safe_load {cfg.fccana_opts['yamlPath']}")
                    print(f"             {exc}")

            ROOT.gInterpreter.ProcessLine(f'''
            TMVA::Experimental::RBDT bdt("{cfg.bdt2_opts['mvaTreeName']}", "{cfg.bdt2_opts['mvaPath']}");
            auto computeModel = TMVA::Experimental::Compute<{len(BDTbranchList)}, float> (bdt);
            ''')

            df3 = (
                df2
                #############################################
                ##                Build BDT                ##
                #############################################
                .Define("MVAVec",    ROOT.computeModel, BDTbranchList)
                .Define("EVT_MVA2",  "MVAVec.at(0)")
            )

            # If the cut value is given filter on it else return the entire DataFrame
            if cfg.bdt2_opts['mvaCut'] is not None:
                df4 = df3.Filter(f"EVT_MVA2 > {cfg.bdt1_opts['mvaCut']}")
            else:
                df4 = df3
        
        # If training is True, do not evaluate the BDT
        else:
            df4 = df2
        
        return df4

    def output(): 
        # Get the output branchList from the config YAML file
        with open(cfg.fccana_opts['yamlPath']) as stream:
            try:
                yaml = safe_load(stream)
                branchList = yaml[cfg.fccana_opts['outBranchList2']]
                print(f"----> INFO:")
                print(f"             Output branch list from : {cfg.fccana_opts['outBranchList2']}")
            except YAMLError as exc:
                print(f"----> ERROR:")
                print(f"             Could not safe load {cfg.fccana_opts['yamlPath']}")
                print(f"             {exc}")

        if not cfg.bdt2_opts['training']:
            branchList.append("EVT_MVA2")

        return branchList
