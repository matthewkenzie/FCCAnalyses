# TO DO List

## Vertexing issue
- The `winter2023` samples do not perform well with the vertexing algorithm used, which leads to very slow tupling (only ~20 events per second!)
  This makes going back and re-saving extra data almost impossible.
  The issue was raised by Aidan but I haven't seen a response/fix yet.
- See [here](https://github.com/HEP-FCC/FCCAnalyses/issues/378) and [here](https://fccsw-forum.web.cern.ch/t/legacy-vertexing-issue/219)

## Analysis progress
I have trained the second stage BDTs and saved their efficiency maps. The vertexing issue means that I was unable to save more tuples with cuts on the 
second stage BDT, but you should be able to do that if you give the batch system a week(!) or so. Currently that means that we don't have great numbers for the
second stage samples (too few background events).

As for the actual analysis, following the pipeline in Matt's b2snunu paper, the "only" things left are fitting the efficiency maps and optimising a cut. However
we still need to properly define what figure of merit should be used in this analysis, and the current signal-to-background ratio is very low (the signal is still 1000
times smaller than the background). This suggests that we either need to use better feautures in the second stage BDT or use a different approach to get the BF estimate.

Another viable option that came up was to actually fit the response curves (either the BDT response itself or the "missing energy" after all cuts), but this also needs
a good signal-to-background ratio first, so that we can actually notice a peak in the signal region.

## Misc (not as important right now)

- Streamlining the workflow (with shell scripts/snakemake) -- currently not viable because of how long the tupling takes
- Removing some redundant code. For example,
  - The BDT scripts don't have to be in their own directory, and they contain a lot of copy-pasted code. The functions used in these scripts can be moved,
    maybe to `tuple_handler` or a different script.
- Creating a `stage2` script similar to `stage1` to save tuples from CERN, instead of the current approach `stage2_fromstage1` which just adds a few branches to
  the stage1 files

# Things to keep in mind
## Version incompatibility (possibly related to vertexing issue)

FCCAnalyses uses the `key4hep` stack which has older versions of Python, ROOT, xgboost, etc. 
The latest versions of xgboost and PyROOT (which are much faster) are apparently not backwards compatible with these older version.
This comes up when training the BDTs (for now I've used the newer version to get optimum hyperparameters and use the older version to actually save the models).
