Some notes from Matt

### Variable Plotting

 - `variable_plotter.py` is a simple plotting script that reads from `config.py`
 - example usage `python -i variable_plotter.py` then can interactively make some plots

### Stage 0 Script

 - `stage0.py` is a script that produces some initial files for investigation and BDT training
 - it provides a lot of variables (stashes in the tree every `MCParticle` and every `ReconstructedParticle`
 - along with various bits of the event information, including vertex info and thrust variables etc.
 - Runs on Cambridge batch over about 25% of the signal MC and a small fraction of the background MC
 - Note batch output goes into top level `FCCAnalyses` directory in a folder called `BatchOutputs`

### Stage 1 Script

 - still a WIP

