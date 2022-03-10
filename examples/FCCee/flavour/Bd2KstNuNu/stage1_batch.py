import os
from glob import glob
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-n','--nchunks',default=5,type=int)
parser.add_argument('-f','--nfilesperchunk',default=5,type=int)
parser.add_argument('-s','--submit',default=False,action='store_true')
args = parser.parse_args()

nchunks = 5
nfilesperchunk = 5

exec_script = '/afs/cern.ch/user/m/mkenzie/work/private/fcc/FCCAnalyses/examples/FCCee/flavour/Bd2KstNuNu/analysis_stage1.py' 
gen_base = '/eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/'
out_base = '/eos/experiment/fcc/ee/analyses/case-studies/flavour/Bd2KstNuNu/flatNtuples/spring2022/prod_01/Batch_Training_4stage1'
#out_base = '/eos/user/m/mkenzie/fcc/Bd2KstNuNu/flatNtuples/test'

bkgs = ['p8_ee_Zbb_ecm91','p8_ee_Zcc_ecm91','p8_ee_Zuds_ecm91']
sigs = ['p8_ee_Zbb_ecm91_EvtGen_Bd2KstNuNu']

samples = bkgs + sigs

def make_batch_script(samp, ch, infs):
  
  fname = os.path.join('BatchOutputs',samp,f'job_{samp}_chunk{ch+1}.sh')
  os.system(f'mkdir -p {os.path.dirname(fname)}')

  with open(fname,'w') as f:
    f.write('#!/bin/bash\n')
    f.write('unset LD_LIBRARY_PATH\n')
    f.write('unset PYTHONHOME\n')
    f.write('unset PYTHONPATH\n')
    f.write(f'source {os.getcwd()}/setup.sh\n')
    f.write('export PYTHONPATH=/afs/cern.ch/user/m/mkenzie/work/private/fcc/FCCAnalyses:$PYTHONPATH\n')
    f.write('export LD_LIBRARY_PATH=/afs/cern.ch/user/m/mkenzie/work/private/fcc/FCCAnalyses/install/lib:$LD_LIBRARY_PATH\n')
    f.write('export ROOT_INCLUDE_PATH=/afs/cern.ch/user/m/mkenzie/work/private/fcc/FCCAnalyses/install/include/FCCAnalyses:$ROOT_INCLUDE_PATH\n')
    f.write('export LD_LIBRARY_PATH=`python -m awkward.config --libdir`:$LD_LIBRARY_PATH\n')
    f.write('\n')

    f.write(f'mkdir {samp}_chunk{ch+1}\n')
    f.write(f'cd {samp}_chunk{ch+1}\n')
    f.write('\n')

    out = f'{samp}_chunk{ch+1}.root'
    
    exec_line = 'python '+ exec_script + ' ' + out + ' ' + ' '.join(infs)
    f.write(f'{exec_line}\n')
    f.write('\n')

    f.write(f'mkdir -p {out_base}/{samp}\n')
    f.write(f'cp {out} {out_base}/{samp}/\n')
    f.write('cd ..\n')
    f.write(f'rm -rf {samp}_chunk{ch+1}\n')

  os.system(f'chmod +x {f.name}')
  return f.name

def make_batch_cfg(samp, ch_list):

  fname = os.path.join('BatchOutputs',samp,f'job_cfg_{samp}.cfg')
  os.system(f'mkdir -p {os.path.dirname(fname)}')
  with open(fname,'w') as f:
    f.write('executable     = $(filename)\n')
    f.write(f'Log            = {os.getcwd()}/BatchOutputs/{samp}/job_{samp}.$(ClusterId).$(ProcId).log\n')
    f.write(f'Output         = {os.getcwd()}/BatchOutputs/{samp}/job_{samp}.$(ClusterId).$(ProcId).out\n')
    f.write(f'Error          = {os.getcwd()}/BatchOutputs/{samp}/job_{samp}.$(ClusterId).$(ProcId).error\n')
    f.write('getenv         = True\n')
    f.write(f'environment    = "LS_SUBCWD=/afs/cern.ch/work/m/mkenzie/private/fcc/FCCAnalyses/BatchOutputs/{samp}"\n')
    f.write('requirements   = ( (OpSysAndVer =?= "CentOS7") && (Machine =!= LastRemoteHost) && (TARGET.has_avx2 =?= True) )\n')
    f.write('on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
    f.write('max_retries    = 3\n')
    f.write('+JobFlavour    = "workday"\n')
    f.write('+AccountingGroup = "group_u_FCC.local_gen"\n')
    f.write('RequestCpus = 8\n')
    f.write('queue filename matching files '+' '.join(ch_list)+'\n')

  return f.name

for samp in samples:

  infiles = glob(os.path.join(gen_base,samp)+'/events*.root')

  ch_list = []
  
  for ch in range(args.nchunks):

    ch_inputs = infiles[ch*args.nfilesperchunk:(ch+1)*args.nfilesperchunk]

    ch_list.append( make_batch_script(samp, ch, ch_inputs) )

  cfg = make_batch_cfg(samp, ch_list)

  if args.submit:
    os.system(f'condor_submit {cfg}')

    
