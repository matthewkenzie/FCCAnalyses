# Changelog

All notable changes to this project will be documented in this file.

## 10 August 2024

### Summary

- New functions added to `myUtils` and  `ReconstructedParticle`
- New stage0 script with additional variables defined and saved
- Some old names changed for consistent naming

### Detailed: Added analyzers

- `myUtils::get_MCVertex_fromMC` [here](https://github.com/RMangrulkar/FCCAnalyses/blob/dev/analyzers/dataframe/FCCAnalyses/myUtils.h#L92)
- `myUtils::get_Vertex_fromRP` [here](https://github.com/RMangrulkar/FCCAnalyses/blob/dev/analyzers/dataframe/FCCAnalyses/myUtils.h#L95)
- `myUtils::get_Vertex_fromRPindex` [here](https://github.com/RMangrulkar/FCCAnalyses/blob/dev/analyzers/dataframe/FCCAnalyses/myUtils.h#L99)
- `myUtils::get_RP_inHemis` [here](https://github.com/RMangrulkar/FCCAnalyses/blob/dev/analyzers/dataframe/FCCAnalyses/myUtils.h#L103)
- `myUtils::get_RP_HemisInfo` [here](https://github.com/RMangrulkar/FCCAnalyses/blob/dev/analyzers/dataframe/FCCAnalyses/myUtils.h#L116)

- `ReconstructedParticle::get_customid` [here](https://github.com/RMangrulkar/FCCAnalyses/blob/dev/analyzers/dataframe/FCCAnalyses/ReconstructedParticle.h#L110)

### Detailed: Changed stage0 names

- Remove underscore for special MCParticle names for easy filtering
  - `MC_em_*` -> `MCem_*`
  - `MC_ep_*` -> `MCep_*`
  - `MC_Z_*` -> `MCZ_*`
  - `MC_q1_*` -> `MCq1_*`
  - `MC_q2_*` -> `MCq2_*`

- Changed "Primary Vertex" to be called `PV` instead of `pv` for consistency
  - `MC_pv_x` -> `MC_PV_x`
  - `MC_pv_y` -> `MC_PV_y`
  - `MC_pv_z` -> `MC_PV_z`
  -  `Rec_pv_*` -> `Rec_PV_*`
  
- `MC_vtx_ntrcks` -> `MC_vtx_ntracks` for clarity and consistency with `ntracks`
- `MC_vtx_inds` -> `MC_vtx_indMC` for clarity and consistency
- `Rec_MC_index` -> `Rec_indMC` for consistency with vertex names
- `Rec_vtx_ispv` -> `Rec_vtx_isPV`
- `Rec_vtx_mcind` -> `Rec_vtx_indMCvtx`
- `d2pv` variables renamed to `d2PV`
- "Normalised" distances to primary vertex now use `normd2PV` instead of "`sig`" to avoid confusion with variables called `err`
  - For example, the relative separation of the vertex from the primary vertex is called `Rec_vtx_normd2PV` instead of `Rec_vtx_d2pv_sig`
- `Rec_vtx_thrust_angle` -> `Rec_vtx_thrustCosTheta`
- `Rec_vtx_hemis_emin` -> `Rec_vtx_in_hemisEmin`
- `Rec_vtx_hemis_emax` -> `Rec_vtx_in_hemisEmax`
- `Rec_vtx_mass` -> `Rec_vtx_m`
- Variables containing information about the two hemispheres now start with `EVT_hemis` instead of `EVT_Thrust` for clarity
  - `EVT_Thrust_Emax_e` -> `EVT_hemisEmax_e`
  - `EVT_Thrust_Emax_n` -> `EVT_hemisEmax_n`
  - `EVT_Thrust_Emax_e_charged` -> `EVT_hemisEmax_eCharged`
  - `EVT_Thrust_Emax_e_neutral` -> `EVT_hemisEmax_eNeutral`
  - `EVT_Thrust_Emax_n_charged` -> `EVT_hemisEmax_nCharged`
  - `EVT_Thrust_Emax_n_neutral` -> `EVT_hemisEmax_nNeutral`
  - `EVT_Thrust_Emax_ndv` -> `EVT_hemisEmax_nDV`
  - Similarly for `EVT_Thrust_Emin` -> `EVT_hemisEmin`

- `ntracks` -> `Rec_ntracks`

### Added to stage0 output

-  `MCfinal_*` variables selecting only "final state" MCParticles
-  `MC_orivtx_ind` : index of the MC vertex to which the MCParticle belongs
-  `Rec_indvtx` : index of the reconstructed vertex to which the ReconstructedParticle belongs
-  `Rec_customid` : ~10 = photon, ~20 = lepton, ~40 = charged hadron (relevant codes for reconstructed particles)
-  `Rec_thrustCosTheta` : angle between RecoParticle and the thrust axis
-  `Rec_in_hemisEmin` : 1 if the particle travels along the direction of the thrust (cosTheta > 0.) and 0 if it travels in the opposite direction (cosTheta < 0.)
-  `Rec_vtx_indRP` : Indices of the ReconstructedParticles associated with the vertex

-  `EVT_Thrust_deltaE` : energy difference between the two hemispheres
-  `EVT_hemisEmin_nLept` : Number of leptons in minimum energy hemisphere
-  `EVT_hemisEmin_maxeLept` : Maximum energy of the lepton travelling in the minimum energy hemisphere
-  `EVT_hemisEmin_maxeLept_inPV` : 1 if the maximum energy lepton is from the PrimaryVertex, 0 if not
-  `EVT_hemisEmin_maxeLept_ind` : Index of the maximum energy lepton in the ReconstructedParticles
  - Similarly for `Kaon`, `Pion` and `hemisEmax`
 
