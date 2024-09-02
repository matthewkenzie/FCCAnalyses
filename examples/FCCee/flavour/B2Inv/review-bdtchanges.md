# Existing BDT

| Feature name         |   Description  |
| -------------------- | -------------- |
| `EVT_Thrust_mag`| Figure of merit of the thrust reconstruction (projected momentum / total reconstructed momentum) |
| `EVT_Thrust_x`  | $x$ component of the thrust axis vector |
| `EVT_Thrust_y`  | $y$ component of the thrust axis vector |
| `EVT_Thrust_z`  | $z$ component of the thrust axis vector | 
| `EVT_Thrust_deltaE` | Energy difference between the minimum (signal) and maximum (tag) sides |
| `EVT_hemisEmin_e`   | Energy on the minimum side |
| `EVT_hemisEmin_eCharged` | Energy of charged particles on the minimum side |
| `EVT_hemisEmin_eNeutral` | Energy of neutrals on the minimum side |
| `EVT_hemisEmax_e`   | |
| `EVT_hemisEmax_eCharged` | |
| `EVT_hemisEmax_eNeutral` | |
| --- | --- |
| `Rec_PV_x` | $x$ coordinate of the Primary Vertex
| `Rec_PV_y` | $y$ coordinate of the Primary Vertex
| `Rec_PV_z` | $z$ coordinate of the Primary Vertex
| `Rec_vtx_d2PV_min` | Min distance between a displaced vertex and the PV
| `Rec_vtx_d2PV_max` | Max distance between a displaced vertex and the PV
| `Rec_vtx_d2PV_ave` | Average distance between a displaced vertex and the PV
| --- | --- |
| `EVT_hemisEmin_maxeKaon` | Maximum energy of $K^\pm$ on the minimum (signal) side | 
| `EVT_hemisEmin_maxePion` | Maximum energy of $\pi^\pm$ on the minimum side | 
| `EVT_hemisEmax_maxeLept` | Maximum energy of leptons ($e$, $\mu$) on the maximum (tag) side |
| `EVT_hemisEmax_maxeKaon` | Maximum energy of $K^\pm$ on the maximum side |
| `EVT_hemisEmax_maxePion` | Maximum energy of $\pi^\pm$ on the minimum side | 
| --- | --- |
| `EVT_hemisEmin_n` | Number of reconstructed particles on the minimum side |
| `EVT_hemisEmin_nCharged` | Number of reconstructed charged particles on the minimum side |
| `EVT_hemisEmin_nNeutral` | Number of reconstructed neutrals on the minimum side |
| `EVT_hemisEmin_nDV` | Number of displaced vertices on the minimum side |
| `EVT_hemisEmax_n` | |
| `EVT_hemisEmax_nCharged` | |
| `EVT_hemisEmax_nNeutral` | |
| `EVT_hemisEmax_nDV` | |
| --- | --- |
| `Rec_track_n` | Total number of tracks |
| `Rec_PV_ntracks` | Number of tracks from the Primary Vertex |
| `Rec_vtx_n` | Total number of vertices |
| --- | --- |
| `EVT_hemisEmin_nKaon` | Number of $K^\pm$ on the minimum side | 
| `EVT_hemisEmin_nPion` | Number of $\pi^\pm$ on the minimum side |
| `EVT_hemisEmin_maxeKaon_fromtruePV` | Is the maximum energy $K^\pm$ on the minimum side from the MC Primary Vertex |
| `EVT_hemisEmin_maxePion_fromtruePV` | Is the maximum energy $\pi^\pm$ on the minimum side from the MC Primary Vertex |
| `EVT_hemisEmax_nLept` | |
| `EVT_hemisEmax_nKaon` | |
| `EVT_hemisEmax_nPion` | |
| `EVT_hemisEmax_maxeLept_fromtruePV` | |
| `EVT_hemisEmax_maxeKaon_fromtruePV` | |
| `EVT_hemisEmax_maxePion_fromtruePV` | |

# Planned new BDTs
Goals:
- Keep only broad "event level" variables in BDT1
- Use "vertex level" or "particle level" variables in BDT2 (in aggregate)
- Define vertex variables separately for the minimum and maximum hemispheres

## New stage1 BDT (planned)
| Feature name         |   Description  |
| -------------------- | -------------- |
| `EVT_Thrust_mag`|  |
| `EVT_Thrust_x`  |  |
| `EVT_Thrust_y`  |  |
| `EVT_Thrust_z`  |  | 
| `EVT_Thrust_deltaE` |  |
| --- | --- |
| `EVT_hemisEmin_e`   |  |
| `EVT_hemisEmin_eCharged` |  |
| `EVT_hemisEmin_eNeutral` |  |
| `EVT_hemisEmin_n`   |  |
| `EVT_hemisEmin_nCharged` |  |
| `EVT_hemisEmin_nNeutral` |  |
| `EVT_hemisEmin_nDV` | |
| `EVT_hemisEmax_e`   | |
| `EVT_hemisEmax_eCharged` | |
| `EVT_hemisEmax_eNeutral` | |
| `EVT_hemisEmax_n`   |  |
| `EVT_hemisEmax_nCharged` |  |
| `EVT_hemisEmax_nNeutral` |  |
| `EVT_hemisEmax_nDV` | |
| --- | --- |
| `Rec_track_n` | |
| `Rec_PV_ntracks` | |
| `Rec_vtx_n` | |
| `Rec_PV_x` |  |
| `Rec_PV_y` |  |
| `Rec_PV_z` |  |

## New stage2 BDT (planned)
| Feature name         |   Description  |
| -------------------- | -------------- |
| `Rec_vtx_d2PV_min_hemisEmin` | The minimum distance from the PV to a displaced vertex on the minmum (signal) side |
| `Rec_vtx_d2PV_max_hemisEmin` | The maximum distance from the PV to a displaced vertex on the minimum side |
| `Rec_vtx_d2PV_ave_hemisEmin` | The average distance from the PV to a displaced vertex on the minimum side |
| `Rec_vtx_thrustCosTheta_min_hemisEmin` | The minimum $\cos{\theta}$ (i.e. maximum angle) between a vertex and the thrust axis, on the minimum side |
| `Rec_vtx_thrustCosTheta_max_hemisEmin` | |
| `Rec_vtx_thrustCosTheta_ave_hemisEmin` | |
| (Similarly on the maximum side) | 
| --- | --- |
| `Rec_thrustCosTheta_min_hemisEmin` | Similar to above but for reconstructed particles |
| `Rec_thrustCosTheta_max_hemisEmin` | |
| ... (etc etc) | |
| --- | --- |
| `Rec_track_d0_min`, `max`, `ave` | (Min/max/average) transverse impact parameter of a track relative to the PV |
| `Rec_track_z0_min`, `max`, `ave` | (Min/max/average) distance between PV and the start of a track |
| --- | --- |
| `EVT_hemisEmin_maxeKaon`, `maxePion`, `maxeLept` | |
| `EVT_hemisEmin_nKaon`, `nPion`, `nLept` | |
| `EVT_hemisEmin_maxeKaon_fromtruePV`, `Pion`, `Lept` | |