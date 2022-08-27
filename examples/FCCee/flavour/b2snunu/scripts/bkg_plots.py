import json
import matplotlib.pyplot as plt
import numpy as np
import config as cfg
import math

def round_sf(x, sf=3):
    return round(x, sf-int(math.floor(math.log10(abs(x))))-1)

def main(input_files, output_file, spruced, mva_cut, hist_plot, eos_cache, decay, event_type, decay_model):

    with open("eos_cache.json") as inf:
        eos_cache = json.load(inf)
    samples = eos_cache[decay][event_type][decay_model]["samples"]
    total_samples = sum([len(sample) for sample in samples])
    total_events = total_samples*cfg.events_per_file[decay][event_type][decay_model]
    print(f"{total_samples = }, {cfg.events_per_file[decay][event_type][decay_model] = }, {total_events = }")

    combined_counts = {}
    lepton_counts = {}
    candidate_mass = {}
    for input_file in input_files:
        with open(input_file, "r") as inf:
            decay_descriptors = json.load(inf)[mva_cut]
        for decay_descriptor, values in decay_descriptors.items():
            if not decay_descriptor in combined_counts.keys():
                combined_counts[decay_descriptor] = 0
                lepton_counts[decay_descriptor] = []
                candidate_mass[decay_descriptor] = []
            combined_counts[decay_descriptor] += values["count"]
            lepton_counts[decay_descriptor].extend(values["lepton_flavours"])
            candidate_mass[decay_descriptor].extend(values["candidate_mass"])

    ordered_decay_descriptors = []     
    for decay, count in combined_counts.items():
        ordered_decay_descriptors.append([decay, count])
    ordered_decay_descriptors = sorted(ordered_decay_descriptors, key = lambda x: x[1], reverse=True)
    ordered_counts = {}
    for decay, count in ordered_decay_descriptors:
        ordered_counts[decay] = count

    max_count = max(ordered_counts.values())
    total_count = sum(ordered_counts.values())
    spruced_counts = {}
    for decay, count in ordered_counts.items():
        if count>=0.01*total_events or len(spruced_counts.keys())<=25:
            spruced_counts[decay] = {}
            spruced_counts[decay]["count"] = count
            spruced_counts[decay]["fraction"] = count/total_events
            spruced_counts[decay]["lepton_flavours"] = lepton_counts[decay]
            spruced_counts[decay]["candidate_mass"] = candidate_mass[decay]
            

    decay_descriptors = list(spruced_counts.keys())
    y_pos = list(np.arange(len(spruced_counts.keys())))
    counts = [spruced_counts[decay_descriptor]["count"] for decay_descriptor in spruced_counts.keys()]
    y_pos.reverse()
    decay_descriptors.reverse()
    counts.reverse()

    fig, ax = plt.subplots()
    ax.barh(y_pos, counts, align="center")
    ax.set_yticks(y_pos, [f"{round_sf(count*100/total_events)}" for count in counts])
    for bar, decay in zip(ax.patches, decay_descriptors):
        ax.text(0.5, bar.get_y()+bar.get_height()/2, decay.replace("gamma", "g"), color = 'black', ha = 'left', va = 'center')
    fig.tight_layout()
    #fig.set_size_inches(16,9)
    fig.savefig(args.output, dpi=400)

    fig.clf()
    plt.clf()
    plot_values = [values["candidate_mass"] for values in list(spruced_counts.values())[:10]]
    total_entries = sum(len(values) for values in plot_values)
    bins = total_entries/100

    fig = plt.figure(figsize=[10,10])
    ax = plt.subplot(111)
    ax.hist(plot_values, int(bins), stacked=True)
    #box = ax.get_position()
    #ax.set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax.legend(list(spruced_counts.keys())[:10], loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=1)
    fig.tight_layout()
    fig.savefig(hist_plot)

    with open(spruced, "w") as outf:
        json.dump(spruced_counts, outf, indent=4)

if __name__ == "__main__":
    # test with 
    import argparse
    parser = argparse.ArgumentParser(description="Applies preselection cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input',nargs="+", required=True, help='Select the input file(s).')
    parser.add_argument('--mva_cut', type=str, required=True, help='Select the mva_cut.')
    parser.add_argument('--output', required=True, type=str, help='Select the output file.')
    parser.add_argument('--spruced', required=True, type=str, help='Select the output file.')
    parser.add_argument('--hist_plot', required=True, type=str, help='Select the output file.')
    parser.add_argument('--eos_cache', required=True, type=str, help='Select the output file.')
    parser.add_argument('--decay', required=True, type=str, help='Select the output file.')
    parser.add_argument('--event_type', required=True, type=str, help='Select the output file.')
    parser.add_argument('--decay_model', required=True, type=str, help='Select the output file.')
    args = parser.parse_args()
    main(args.input, args.output, args.spruced, args.mva_cut, args.hist_plot, args.eos_cache, args.decay, args.event_type, args.decay_model)