#!/usr/bin/env python

# Wrapper to submit a script to Slurm using a custom job script.
#
# __author__: Aidan Wiederhold
# __email__: aidan.richard.wiederhold@cern.ch
#
# Thanks to Blaise Delaney who wrote a Condor script which I've changed into a Slurm script, who also directs *many* thanks to John Smeaton for the template script

#===========================================================================
# run:"snakemake <target_file(s)> -s <path_to_snakefile> --cluster <path_to_slurm_wrapper> --latency-wait 120 --use-conda --jobs <max_number_of_cores_to_occupy / max_number_of_cores_assigned_to_a_rule> "
#===========================================================================

from tempfile import NamedTemporaryFile
import subprocess
import sys
import os

jobscript = sys.argv[1]

logdir = os.path.abspath("SlurmLogs")
if not os.path.exists(logdir):
    os.makedirs(logdir)
logfile=f"{logdir}/0.out"

large_jobs = []

with NamedTemporaryFile(mode="w") as sub_file:
    sub_file.write(f"#!/bin/bash \n")
    sub_file.write(f"#SBATCH --ntasks=1 \n")
    sub_file.write(f"#SBATCH --mem-per-cpu=3997 \n")
    sub_file.write(f"#SBATCH --time=24:00:00 \n")
    sub_file.write(f"#SBATCH --cpus-per-task=8 \n")
    sub_file.write(f"#SBATCH --partition=epp \n")
    sub_file.write(f'{jobscript} \n')
    sub_file.flush()
    subprocess.call( ["sbatch", sub_file.name, ">", logfile] )
