# with the current environment set up snakemake cannot be imported so need to just run this bit in a separate conda environment
# TODO fix that

def cache(outf_name, sample_portion, group_size):
    from snakemake.remote.XRootD import RemoteProvider as XRootDRemoteProvider
    XRootD = XRootDRemoteProvider(stay_on_remote=True)
    import json
    from config import MC, event_types, decay_model_to_fname, decays, outputs, training_proportions
    from pathlib import Path
    import math
    import random

    eos_cache = {}

    print("Starting EOS querying!")
    for decay in decays:
        eos_cache[decay] = {}
        for event_type, decay_models in event_types.items():
            eos_cache[decay][event_type] = {}
            for decay_model in decay_models:
                eos_cache[decay][event_type][decay_model] = {}
                path = MC+f"{event_type}{decay_model_to_fname(decay_model, decay)}"
                result = XRootD.glob_wildcards(path+"/events_{sample}.root")
                result = result[0][0:int(len(result[0])*sample_portion)]
                eos_cache[decay][event_type][decay_model]["samples"]=[]
                for i in range(1, max(math.floor(len(result)/group_size),1)+1):
                    eos_cache[decay][event_type][decay_model]["samples"].append(result[(i-1)*group_size:i*group_size])
                if result[i*group_size:-1]!=[]:
                    eos_cache[decay][event_type][decay_model]["samples"].append(result[i*group_size:-1])
                eos_cache[decay][event_type][decay_model]["expected_output"] = [f"{outputs}root/stage1/{decay}/{event_type}/{decay_model}/{i}.root" for i in range(len(eos_cache[decay][event_type][decay_model]["samples"]))]

                
                training_portion = training_proportions[decay][event_type][decay_model]
                total_samples = len(eos_cache[decay][event_type][decay_model]["samples"])
                eos_cache[decay][event_type][decay_model]["training"] = random.sample(eos_cache[decay][event_type][decay_model]["samples"], int(total_samples*training_portion))
                eos_cache[decay][event_type][decay_model]["training_output"] = []
                print(f"For {decay} the {event_type} {decay_model} BDT 1 training will feature {group_size*int(total_samples*training_portion)} input files!")
                for sample_group in eos_cache[decay][event_type][decay_model]["training"]:
                    index = eos_cache[decay][event_type][decay_model]["samples"].index(sample_group)
                    output_name = eos_cache[decay][event_type][decay_model]["expected_output"][index].replace("stage1", "training")
                    eos_cache[decay][event_type][decay_model]["training_output"].append(output_name)
                    eos_cache[decay][event_type][decay_model]["samples"].remove(eos_cache[decay][event_type][decay_model]["samples"][index])
                    eos_cache[decay][event_type][decay_model]["expected_output"].remove(eos_cache[decay][event_type][decay_model]["expected_output"][index])
        print(f"Finished {decay}!")

    if not Path(outputs).exists():
        Path(outputs).mkdir()
    with open(outf_name, 'w', encoding='utf-8') as f:
        json.dump(eos_cache, f, ensure_ascii=False, indent=4)

    return eos_cache

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Applies preselection cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--sample_portion', default = 1., type=float, help='Choose the fraction of MC to use.')
    parser.add_argument('--group_size', default = 20, type=int, help='Choose how many MC samples to group together for processing to reduce the total number of files in the workflow.')
    args = parser.parse_args()
    cache(f"eos_cache.json", args.sample_portion, args.group_size)

