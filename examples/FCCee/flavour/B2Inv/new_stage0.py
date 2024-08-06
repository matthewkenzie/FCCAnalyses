###########################
# PLANNED MC VARIABLES
###########################
.Define("MC_ThrustCosTheta",  "Algorithms::getCosTheta(EVT_ThrustInfo, MC_px, MC_py, MC_pz)")


###########################
# PLANNED RECONSTRUCTED VARIABLES
###########################

#Already defined as EVT_ThrustCosTheta
.Define("Rec_ThrustCosTheta", "Algorithms::getCosTheta(EVT_ThrustInfo, Rec_px, Rec_py, Rec_pz)")

#Maybe operate this on RecoParticlesPID directly so nans will also have customid
.Define("RecoParticlesWithCustomID",       "ReconstructedParticle::get_customid(RecoParticlesPIDAtVertex)")
.Define("Rec_in_hemisEmin",   "myUtils::getRPinHemis(0)(Rec_ThrustCosTheta)")
.Define("Rec_in_hemisEmax",   "myUtils::getRPinHemis(1)(Rec_ThrustCosTheta)")

###########################
# PLANNED EVT VARIABLES
###########################
.Define("EVT_Thrust_deltaE",  "EVT_Thrust_Emax_e - EVT_Thrust_Emin_e")
.Define("RecoParticlesHemisNumInfo_Emin", "myUtils::get_RecoP_HemisNumInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmin)")
.Define("RecoParticlesHemisNumInfo_Emax", "myUtils::get_RecoP_HemisNumInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmax)")

.Define("EVT_hemisEmin_numLep", "myUtils:get_RecoP_HemisNumInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmin).at(0)")
.Define("EVT_hemisEmin_numK",   "myUtils:get_RecoP_HemisNumInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmin).at(1)")
.Define("EVT_hemisEmin_numPi",  "myUtils:get_RecoP_HemisNumInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmin).at(2)")
##### SIMILARLY hemisEmax

.Define("EVT_hemisEmin_maxeLep", "myUtils:get_RecoP_HemisEInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmin).at(0)")
.Define("EVT_hemisEmin_maxeK",   "myUtils:get_RecoP_HemisEInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmin).at(1)")
.Define("EVT_hemisEmin_maxePi",  "myUtils:get_RecoP_HemisEInfo(RecoParticlesPIDAtVertex, Rec_in_hemisEmin).at(2)")
##### SIMILARLY hemisEmax
