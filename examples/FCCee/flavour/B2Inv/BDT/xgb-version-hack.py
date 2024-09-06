# Temporary hack to fix slow running when using the key4hep version of xgboost
# Use the JSON file saved using lb-conda default and save to TMVA model
import os, sys
sys.path.append('/r02/lhcb/rrm42/fcc/FCCAnalyses/examples/FCCee/flavour/B2Inv')
import config as cfg

import xgboost as xgb
import ROOT

model = xgb.XGBClassifier()
model.load_model(cfg.bdt1_opts['outputpath'])
ROOT.TMVA.Experimental.SaveXGBoost(model, cfg.bdt1_opts['mvaRBDTName'], cfg.bdt1_opts['mvaPath'], num_inputs=model.n_features_in_)
