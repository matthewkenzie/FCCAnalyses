import uproot
import os
filepath = '/r01/lhcb/mkenzie/fcc/B2Inv/stage0/'

signal = os.path.join(filepath, 'p8_ee_Zbb_ecm91_EvtGen_Bs2NuNu/chunk_0.root:events')
bb = os.path.join(filepath, 'p8_ee_Zbb_ecm91/chunk_0.root:events')
cc = os.path.join(filepath, 'p8_ee_Zcc_ecm91/chunk_0.root:events')
ss = os.path.join(filepath, 'p8_ee_Zss_ecm91/chunk_0.root:events')
dd = os.path.join(filepath, 'p8_ee_Zud_ecm91/chunk_0.root:events')

files = [signal, bb, cc, ss, dd]

for file in files:
    with uproot.open(file) as tree:
        nocut = uproot.concatenate(tree, expresions='MC_PDG')['MC_PDG']
        average = [0, 0]
        for x in nocut:
            count = [0, 0]
            for y in x:
                if abs(y) == 311:
                    count[0] = count[0] + 1
                elif abs(y) == 321:
                    count[1] = count[1] + 1

            average[0] = average[0] + (count[0]/len(x))
            average[1] = average[1] + (count[1]/len(x))

        print(f'{file} no cut. K0/bar = {average[0]/len(nocut)} \n Kpm = {average[1]/len(nocut)}')

        cut = uproot.concatenate(tree, expresions='MC_PDG', cut = 'EVT_Thrust_Emin_e < 20')['MC_PDG']
        average = [0, 0]
        for x in cut:
            count = [0, 0]
            for y in x:
                if abs(y) == 311:
                    count[0] = count[0] + 1
                elif abs(y) == 321:
                    count[1] = count[1] + 1

            average[0] = average[0] + (count[0]/len(x))
            average[1] = average[1] + (count[1]/len(x))

        print(f'{file} with cut. K0/bar = {average[0]/len(cut)} \n Kpm = {average[1]/len(cut)}')
