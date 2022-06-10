import math
from config import branching_fractions

# events per file * files
events_per_signal = 1e4*1e3 # 1e7
events_per_bkg = 1e5*1e4 # 1e9
stage1_efficiencies = {
    "Bd2KstNuNu": {
        "p8_ee_Zbb_ecm91": {
            "signal": 168569./200000.,
            "inclusive": 385753./2000000.,
        },
        "p8_ee_Zcc_ecm91": {
            "inclusive": 308961./2000000.,
        },
        "p8_ee_Zuds_ecm91": {
            "inclusive": 9067./2000000.,
        },
    },
    "Bs2PhiNuNu": {
        "p8_ee_Zbb_ecm91": {
            "signal": 171835./200000.,
            "inclusive": 35289./2000000.,
        },
        "p8_ee_Zcc_ecm91": {
            "inclusive": 25415./2000000.,
        },
        "p8_ee_Zuds_ecm91": {
            "inclusive": 1046./2000000.,
        },
    },
}

target_events = int(1e6)

def round_up(multiple_of, value):
    """round up value to a multiple of"""
    return value - (value%multiple_of) + multiple_of

print("bkg estimations")
for decay in stage1_efficiencies.keys():
    total_eff = 0.
    for event_type in stage1_efficiencies[decay].keys():
        total_eff += branching_fractions[event_type]*stage1_efficiencies[decay][event_type]["inclusive"]

    print(f"Total efficiency: {total_eff}")
    for event_type in stage1_efficiencies[decay].keys():
        desired_events = int(target_events * (branching_fractions[event_type]*stage1_efficiencies[decay][event_type]["inclusive"]/total_eff))
        initial_events = int(float(desired_events) / stage1_efficiencies[decay][event_type]["inclusive"])
        required_events = int(round_up(1e5, initial_events))
        print(f"{decay}: {event_type}: Efficiency: {stage1_efficiencies[decay][event_type]['inclusive']} and BF: {branching_fractions[event_type]} so we need {desired_events} from {initial_events} so round up to {required_events} events which is {int(required_events/1e5)} files out of {int(1e4)}.")

print("\nsignal estimations")
for decay in stage1_efficiencies.keys():
    initial_events = int(target_events / stage1_efficiencies[decay]["p8_ee_Zbb_ecm91"]["signal"])
    required_events = int(round_up(1e4, initial_events))
    print(f"{decay}: {event_type}: {target_events} from {initial_events} so round up to {required_events} events which is {int(required_events/1e4)} files out of {int(1e3)}.")