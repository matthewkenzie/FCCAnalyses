import uproot
from particle import Particle
import json
from config import MVA_cuts, decay_to_candidates, mass_cut
import copy

def pdgid_to_name(pdgid, conjugate):
    global unknown_cache
    if conjugate:
        pdgid=-pdgid

    # names based on https://pdg.lbl.gov/2021/reviews/contents_sports.html
    missing_pdgids = {
        20413: "D_1(H)+",
        -20413: "D_1(H)-",
        20423: "D_1(2430)0",
        -20423: "D_1(2430)0~",
        10413: "D_1(2420)+",
        -10413: "D_1(2420)-",
        30221: "X",
        -30221: "X",
        5214: "Sigma_b*0",
        -5214: "Sigma_b*0~",
        5212: "Sigma_b0",
        -5212: "Sigma_b0~",
        4124: "X",
        -4124: "X",
        5322: "Xi_b'0",
        -5322: "Xi_b'0~",
        5324: "Xi_b0*",
        -5324: "Xi_b0*~",
        5312: "Xi_b'-",
        -5312: "Xi_b'+",
        5314: "Omega_bb-",
        -5314: "Omega_bb+",
        5334: "Omega_b*-",
        -5334: "Omega_b*+",
        543: "B_c*+",
        -543: "B_c*-",
    }

    if abs(pdgid) in missing_pdgids.keys():
        print(f"WARNING: particle module does not recognise {pdgid} as a pdgid, it should correspond to {missing_pdgids[pdgid]}")
        return missing_pdgids[pdgid]
    else:
        try:
            try:
                name = Particle.from_pdgid(pdgid).name
            except: # to handle things like Ks0
                name = Particle.from_pdgid(-pdgid).name
            return name
        except:
            unknown_cache.append(pdgid)
            return "X"

def decay_child(string, child, child_tree):
    #if child[:-1]=="B~0":
    #    print(f"{child}: {child_tree = }")
    if not isinstance(child_tree, int):
        if len(list(child_tree.keys()))>1:
            string += f"{child[:-1]} -> ("
            for new_child, new_children in child_tree.items():
                string = decay_child(string, new_child, new_children)
            string += ") "
        else:
            string += f"{child[:-1]} -> "
            for new_child, new_children in child_tree.items():
                string = decay_child(string, new_child, new_children)
    else:
        string += f"{child[:-1]} "
    #print(string)
    return string

def add_to_existing_tree(name, value, tree, counter, verbose=False):
    while f"{name}{counter}" in tree.keys():
        counter+=1
    tree[f"{name}{counter}"] = value
    return tree, f"{name}{counter}"

def ignore_excited(decay_tree):
    tree_copy = decay_tree.copy()
    for parent, children in tree_copy.items():
        if not isinstance(children, int):
            if "*" in parent and parent[:-1].replace("*", "") in [name[:-1] for name in children.keys()]:
                for child in children.keys():
                    if child[:-1]==parent[:-1].replace("*", ""):
                        # replace the X*: {X: ..., gamma: ..., pi0: ...} like entry in the decay tree with X: ... i.e. ignore the X* and the gamma/pi0
                        decay_tree, child_name = add_to_existing_tree(child[:-1], children[child], decay_tree, 0, verbose=True)
                        decay_tree.pop(parent)
                        #print(decay_tree)
                        #print(decay_tree[child_name])
                        if decay_tree[child_name]!=-1:
                            decay_tree[child_name] = ignore_excited(decay_tree[child_name])
                        break
            else:
                decay_tree[parent] = ignore_excited(children)
    return decay_tree

def descriptor(decay_tree):
    if len(decay_tree.keys())>1:
        raise ValueError(f"A decay tree cannot have more than 1 initial particle, this decay tree is {decay_tree}")
    else:
        copied_tree = decay_tree.copy()
        copied_tree = ignore_excited(copied_tree)
        initial_particle = list(copied_tree.keys())[0]
        string = f"{initial_particle[:-1]} -> "
        if len(list(copied_tree[initial_particle].keys()))>1:
            string += "("
        for child, child_tree in copied_tree[initial_particle].items():
            if child_tree!=-1:
                child_tree = dict(sorted(child_tree.items()))
            if len(list(copied_tree[initial_particle].keys()))>1 and child_tree!=-1:
                string += "("
            string = decay_child(string, child, child_tree)
            if len(list(copied_tree[initial_particle].keys()))>1 and child_tree!=-1:
                string += ") "
        if len(list(copied_tree[initial_particle].keys()))>1:
            string += ") "
    if string[-1] == " ":
        string = string[:-1]
    return string

def check_oscillation(arr, event_index, parent_index, parent_pdgid):
    d_pdgids = {}
    for d_number in range(1, 5):
        d_index=arr[f"MC_D{d_number}"][event_index][parent_index]
        if d_index!=-999:
            d_pdgid = arr[f"MC_PDG"][event_index][d_index]
            d_pdgids[d_pdgid] = d_index
    if list(d_pdgids.keys())==[-parent_pdgid]:
        #return -999
        return d_pdgids[-parent_pdgid]
    else:
        return -999

def ignore_initial_excited(arr, event_index, initial_particle_index, initial_particle_pdgid):
    initial_particle_name = pdgid_to_name(initial_particle_pdgid, False)
    if "*" in initial_particle_name:
        ignore=True
        interesting_children = []
        for d_number in range(1, 5):
            d_index=arr[f"MC_D{d_number}"][event_index][initial_particle_index]
            if d_index!=-999:
                d_pdgid = arr[f"MC_PDG"][event_index][d_index]
                d_name = pdgid_to_name(d_pdgid, False)
                if d_name not in ["pi0", "gamma"]:
                    interesting_children.append(d_index)
                    if d_name!=initial_particle_name.replace("*", ""):
                        ignore=False
        if ignore:
            if len(interesting_children)!=1:
                raise RuntimeError("An excited state should not be marked for ignoring if it produces more than one non pi0/gamma!")
            return interesting_children[0], arr[f"MC_PDG"][event_index][interesting_children[0]]
    return initial_particle_index, initial_particle_pdgid

        

def ignore_oscillation(arr, event_index, initial_particle_index, initial_particle_pdgid):
    d_pdgids = {}
    for d_number in range(1, 5):
        d_index=arr[f"MC_D{d_number}"][event_index][initial_particle_index]
        if d_index!=-999:
            d_pdgid = arr[f"MC_PDG"][event_index][d_index]
            d_pdgids[d_pdgid] = d_index
    if list(d_pdgids.keys())==[-initial_particle_pdgid]:
        initial_particle_index, initial_particle_pdgid = ignore_oscillation(arr, event_index, d_pdgids[-initial_particle_pdgid], -initial_particle_pdgid)
    return initial_particle_index, initial_particle_pdgid

def descendants(arr, event_index, parent_index, parent_pdgid, candidate_index, conjugate):
    has_children = False
    parent_dictionary = {}
    for d_number in range(1, 5):
        #print(d_number, event_index, parent_index)
        if arr[f"MC_D{d_number}"][event_index][parent_index] != -999:
            has_children = True
    if has_children:
        """
        oscillation = check_oscillation(arr, event_index, parent_index, parent_pdgid)
        if oscillation!=-999:
            d_pdgid = -parent_pdgid
            d_name = unique_name(pdgid_to_name(d_pdgid, conjugate), parent_dictionary.keys())
            parent_dictionary = descendants(arr, event_index, oscillation, d_pdgid, candidate_index, conjugate)
        else:
            """
        for d_number in range(1, 5):
            d_index = arr[f"MC_D{d_number}"][event_index][parent_index]
            if d_index!=-999:
                d_pdgid = arr[f"MC_PDG"][event_index][d_index]
                #if event_index==981 and parent_index==166:
                #    print(pdgid_to_name(d_pdgid, conjugate), parent_dictionary.keys())
                d_name = unique_name(pdgid_to_name(d_pdgid, conjugate), parent_dictionary.keys())
                if d_index == candidate_index:
                    d_name = "^"+d_name
                parent_dictionary[d_name] = descendants(arr, event_index, d_index, d_pdgid, candidate_index, conjugate)
    else:
        return -1

    return parent_dictionary

def ignore_extra_neutrals(decay_descriptors):
    decay_descriptors_copy = copy.deepcopy(decay_descriptors)
    for mva_cut in decay_descriptors_copy.keys():
        for duplicates in range(5):
            for neutral in [" pi0", " gamma", " (pi0)"]:
                ignore = neutral*duplicates
                changed=True
                # every time we update the dict we want to run through again
                while changed:
                    changed=False
                    for decay in decay_descriptors_copy[mva_cut].keys():
                        if decay in decay_descriptors[mva_cut].keys():
                            if decay.replace(ignore, "", 1) != decay:
                                if decay.replace(ignore, "", 1) in decay_descriptors[mva_cut].keys():
                                    decay_descriptors[mva_cut][decay.replace(ignore, "", 1)]["count"]+=decay_descriptors[mva_cut][decay]["count"]
                                    decay_descriptors[mva_cut][decay.replace(ignore, "", 1)]["decay_trees"].extend(decay_descriptors[mva_cut][decay]["decay_trees"])
                                    decay_descriptors[mva_cut].pop(decay)
                                    changed=True
    return decay_descriptors

def unique_name(name, names):
    i = 0
    new_name = f"{name}{i}"
    while new_name in names:
        i+=1
        new_name = f"{name}{i}"
    return new_name

def get_parent(arr, event_index, child_index):
    ignore_pdgids = list(range(-9,9))+[21,-21]
    child_pdgid = arr["MC_PDG"][event_index][child_index]
    m1_index = arr["MC_M1"][event_index][child_index]
    m1_pdgid = arr["MC_PDG"][event_index][m1_index] if m1_index!=-999 else 0
    if m1_pdgid not in ignore_pdgids:
        result = get_parent(arr, event_index, m1_index)
        return result
    else:
        return child_index

def generalise_leptons(decay_descriptor):
    lepton_flavours = []
    if "tau+" in decay_descriptor:
        lepton_flavours.append("tau")
    if "mu+" in decay_descriptor:
        lepton_flavours.append("mu")
    if "e+" in decay_descriptor:
        lepton_flavours.append("e")
    decay_descriptor = decay_descriptor.replace("nu(e)", "nu")
    decay_descriptor = decay_descriptor.replace("nu(mu)", "nu")
    decay_descriptor = decay_descriptor.replace("nu(tau)", "nu")
    decay_descriptor = decay_descriptor.replace("e+", "l+")
    decay_descriptor = decay_descriptor.replace("mu+", "l+")
    decay_descriptor = decay_descriptor.replace("tau+", "l+")
    return decay_descriptor, [lepton_flavours]

def condense_neutrals(decay_descriptor):
    decay_descriptor = decay_descriptor.replace("pi0 -> (gamma gamma)", "pi0")
    return decay_descriptor

def unit_tests():
    print("Running unit tests")
    failed = {}
    test_tree = {"X*0": {"X0": {"a*0": {"a0": -1, "c0": -1,},
                                "d0": -1,
                                },
                         "gamma0": -1,
                         "pi00": {"gamma0": -1, "gamma1": -1,},
                         },
                 }

    # add_to_existing_tree
    added = {"X*0": {"X0": {"a*0": {"a0": -1, "c0": -1,},
                            "d0": -1,
                            },
                     "gamma0": -1,
                     "pi00": {"gamma0": -1, "gamma1": -1,},
                     },
             "X*1": {"a0": -1, "b0": -1,},
             }
    name = "X*"
    value = {"a0": -1, "b0": -1}
    test_add_to_existing_tree = add_to_existing_tree(name, value, test_tree.copy(), 0)
    if test_add_to_existing_tree!=(added, "X*1"):
        failed["add_to_existing_tree"] = {"incorrect": test_add_to_existing_tree, "correct": added}
    
    # ignore_excited
    excited_ignored = {"X0": {"a0": -1,
                             "d0": -1,
                             },
                       }
    test_ignore_excited = ignore_excited(test_tree.copy())
    if test_ignore_excited!=excited_ignored:
        failed["ignore_excited"] = {"incorrect": test_ignore_excited, "correct": excited_ignored}

    # ignore extra gammas
    with_extra_neutrals = {
        "0.6": {
            "B0 -> ((^K*(892)0 -> (K+ pi-)) nu nu~)": {
                "count": 135362,
                "decay_trees": [
                    {
                        "B00": {
                            "^K*(892)00": {
                                "K+0": -1,
                                "pi-0": -1
                            },
                            "nu(e)0": -1,
                            "nu(e)~0": -1
                        }
                    },
                ],
            },
            "B0 -> ((^K*(892)0 -> (K+ pi- gamma)) nu nu~)": {
                "count": 10382,
                "decay_trees": [
                    {
                        "B00": {
                            "^K*(892)00": {
                                "K+0": -1,
                                "pi-0": -1,
                                "gamma0": -1
                            },
                            "nu(e)0": -1,
                            "nu(e)~0": -1
                        }
                    }
                ],
            },
            "B0 -> ((^K*(892)0 -> (K+ pi- pi0)) nu nu~)": {
                "count": 1,
                "decay_trees": [
                    {
                        "B00": {
                            "^K*(892)00": {
                                "K+0": -1,
                                "pi-0": -1,
                                "pi00": -1
                            },
                            "nu(e)0": -1,
                            "nu(e)~0": -1
                        }
                    }
                ],
            },
            "B+ -> (nu l+ (D*(2007)~0 -> (^D~0 -> (K- K+ pi0 pi0) pi0)))": {
                "count": 41742,
                "decay_trees": [1],
            },
            "B+ -> (nu l+ (D*(2007)~0 -> (^D~0 -> (K- K+) pi0)))": {
                "count": 1,
                "decay_trees": [2],
            },
        }
    }

    extra_neutrals_ignored = {
        "0.6": {
            "B0 -> ((^K*(892)0 -> (K+ pi-)) nu nu~)": {
                "count": 135362+10382+1,
                "decay_trees": [
                    {
                        "B00": {
                            "^K*(892)00": {
                                "K+0": -1,
                                "pi-0": -1
                            },
                            "nu(e)0": -1,
                            "nu(e)~0": -1
                        }
                    },
                    {
                        "B00": {
                            "^K*(892)00": {
                                "K+0": -1,
                                "pi-0": -1,
                                "pi00": -1
                            },
                            "nu(e)0": -1,
                            "nu(e)~0": -1
                        }
                    },
                    {
                        "B00": {
                            "^K*(892)00": {
                                "K+0": -1,
                                "pi-0": -1,
                                "gamma0": -1
                            },
                            "nu(e)0": -1,
                            "nu(e)~0": -1
                        }
                    },
                ],
            },
            "B+ -> (nu l+ (D*(2007)~0 -> (^D~0 -> (K- K+) pi0)))": {
                "count": 41743,
                "decay_trees": [2,1],
            },
        }
    }
    test_ignore_extra_neutrals = ignore_extra_neutrals(with_extra_neutrals)
    if test_ignore_extra_neutrals!=extra_neutrals_ignored:
        failed["ignore_excited"] = {"incorrect": test_ignore_extra_neutrals, "correct": extra_neutrals_ignored}


    if len(failed.keys())!=0:
        for test, result in failed.items():
            print(f"{test} failed with result:\n{result['incorrect']}\nInstead of:\n{result['correct']}\n")
        raise RuntimeError("Unit tests failed, see above for details!")
    else:
        print("All tests passed!")

    

def main(input_files, decay, output_file):
    unit_tests()
    decay_descriptors = {}
    for cut in MVA_cuts:
        decay_descriptors[cut] = {}
    bkg_branches = [f"{candidate}Candidates_truth",
                    f"{candidate}Candidates_mass",
                    "MC_PDG",
                    "MC_M1",
                    "MC_M2",
                    "MC_D1",
                    "MC_D2",
                    "MC_D3",
                    "MC_D4",
                    "EVT_MVA1",
                    ]
    for arr in uproot.iterate(input_files, expressions=bkg_branches, step_size="10000MB"):
        n_events = len(arr)
        for event_index, event in enumerate(arr[f"{candidate}Candidates_truth"]):
            if event_index<n_events:
                #print(f"{100*event_index/n_events:.2f} % of events determined", end="\r")
                for candidate_number, candidate_index in enumerate(event):
                    candidate_mass = arr[f"{candidate}Candidates_mass"][event_index][candidate_number]
                    if event_index<=5:
                        print(f"{candidate_mass = }")
                    if candidate_index!=-999 and (candidate_mass >= mass_cut[candidate][0] and candidate_mass <= mass_cut[candidate][1]): # TODO what to do with events where the candidate index is -999? Could try find some particle that does have an index and grow the tree from there
                        initial_particle_index = get_parent(arr, event_index, candidate_index)
                        decay_tree = {}
                        initial_particle_pdgid = arr["MC_PDG"][event_index][initial_particle_index]
                        initial_particle_index, initial_particle_pdgid = ignore_initial_excited(arr, event_index, initial_particle_index, initial_particle_pdgid)
                        initial_particle_index, initial_particle_pdgid = ignore_oscillation(arr, event_index, initial_particle_index, initial_particle_pdgid)
                        if initial_particle_pdgid<0:
                            conjugate=True
                        else:
                            conjugate=False
                        initial_particle_name = unique_name(pdgid_to_name(initial_particle_pdgid, conjugate), [])
                        if initial_particle_index==candidate_index:
                            initial_particle_name = "^"+initial_particle_name
                        decay_tree[initial_particle_name] = descendants(arr, event_index, initial_particle_index, initial_particle_pdgid, candidate_index, conjugate)
                        decay_descriptor = descriptor(decay_tree)
                        decay_descriptor = decay_descriptor.replace("( ", "(")
                        decay_descriptor = decay_descriptor.replace(" )", ")")
                        decay_descriptor = decay_descriptor.replace("  ", " ")
                        decay_descriptor, lepton_flavours = generalise_leptons(decay_descriptor)
                        decay_descriptor = condense_neutrals(decay_descriptor)
                        for cut in MVA_cuts:
                            if arr["EVT_MVA1"][event_index]>=cut:
                                if decay_descriptor not in decay_descriptors[cut].keys():
                                    decay_descriptors[cut][decay_descriptor] = {}
                                    decay_descriptors[cut][decay_descriptor]["count"] = 1
                                    decay_descriptors[cut][decay_descriptor]["lepton_flavours"] = lepton_flavours
                                    decay_descriptors[cut][decay_descriptor]["decay_trees"] = [decay_tree]
                                    decay_descriptors[cut][decay_descriptor]["candidate_mass"] = [candidate_mass]
                                else:
                                    decay_descriptors[cut][decay_descriptor]["count"] += 1
                                    if [] not in lepton_flavours:
                                        decay_descriptors[cut][decay_descriptor]["lepton_flavours"].extend(lepton_flavours)
                                    if decay_tree not in decay_descriptors[cut][decay_descriptor]["decay_trees"]:
                                        decay_descriptors[cut][decay_descriptor]["decay_trees"].append(decay_tree)
                                        decay_descriptors[cut][decay_descriptor]["candidate_mass"].append(candidate_mass)

    decay_descriptors = ignore_extra_neutrals(decay_descriptors)
    new_decay_descriptors = {}
    for cut in MVA_cuts:
        ordered_decay_descriptors = []     
        for decay_descriptor, values in decay_descriptors[cut].items():
            ordered_decay_descriptors.append([decay_descriptor, values["decay_trees"], values["count"], values["lepton_flavours"], values["candidate_mass"]])
        ordered_decay_descriptors = sorted(ordered_decay_descriptors, key = lambda x: x[2], reverse=True)
        new_decay_descriptors[cut] = {}
        for decay_descriptor, decay_trees, count, lepton_flavours, candidate_mass in ordered_decay_descriptors:
            new_decay_descriptors[cut][decay_descriptor] = {"count": count, "decay_trees": decay_trees, "lepton_flavours": lepton_flavours, "candidate_mass": candidate_mass}

    # TODO count the total number of input events and calculate what fraction survive
    #for input_file in input_files:

    with open(args.output_file, "w") as outf:
        json.dump(new_decay_descriptors, outf, indent=4)

if __name__ == "__main__":
    # test with `python ./scripts/bkg_matching.py --input_files ./p8_ee_Zbb_Bd2KstNuNu_stage1.root:events --output_file ./decay_trees.json`
    import argparse
    parser = argparse.ArgumentParser(description="Applies preselection cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input_files',nargs="+", required=True, help='Select the input file(s).')
    parser.add_argument('--tree_name', type=str, required=True, help='Select the input tree.')
    parser.add_argument('--decay', type=str, required=True, help='Select the decay.')
    parser.add_argument('--output_file', required=True, type=str, help='Select the output file.')
    args = parser.parse_args()
    candidate = decay_to_candidates[args.decay]
    unknown_cache = []
    input_files = [f"{file}:{args.tree_name}" for file in args.input_files]
    main(input_files, candidate, args.output_file)
    print(f"{unknown_cache = }")