/////////////////////////////
  // Count of particle categories in given hemisphere
  // `should_eval` is meant to be the output of get_RP_inHemis
  /*   output[0] -> number of leptons (e, mu) in the hemisphere
   *   output[1] -> number of kaons (k+/k-) in the hemisphere
   *   output[2] -> number of pions (pi+/pi-) in the hemisphere
  */
  std::vector<int> get_RP_HemisNumInfo(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> recop, 
                ROOT::VecOps::RVec<int> should_eval);
  
  // Maximum energy of different particle categories in given hemisphere
  // `should_eval` is meant to be the output of get_RP_inHemis()()
  /*   output[0] -> max energy of leptons (e, mu) in the hemisphere
   *   output[1] -> max energy of kaons (k+/k-) in the hemisphere
   *   output[2] -> max energy of pions (pi+/pi-) in the hemisphere
  */
  std::vector<float> get_RP_HemisEInfo(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> recop, 
                ROOT::VecOps::RVec<int> should_eval);

  // Checks if maximum energy particle of each type is from the PrimaryVertex or not
  // `should_eval` is meant to be the output of get_RP_inHemis()
  /*   output[0] -> is the max energy lepton from PV
   *   output[1] -> is the max energy kaon (k+/k-) from PV
   *   output[2] -> is the max energy pion (pi+/pi-) from PV
  */
  std::vector<int> get_maxEparticle_isfromPV(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> recop, 
                ROOT::VecOps::RVec<VertexingUtils::FCCAnalysesVertex> vertex, ROOT::VecOps::RVec<int> should_eval,
                std::vector<float> max_energy);

//////////////////////////
std::vector<int> get_RP_HemisNumInfo(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> recop, 
    ROOT::VecOps::RVec<int> should_eval) {
  std::vector<int> result {0, 0, 0};

  for (size_t i = 0; i < recop.size(); ++i){
    if (should_eval.at(i) != (int)1) continue;
    #if edm4hep_VERSION > EDM4HEP_VERSION(0, 10, 5)
      else if ((recop.at(i).PDG == 11) || (recop.at(i).PDG == 13)) result[0]++;
      else if (recop.at(i).PDG == 321) result[1]++;
      else if (recop.at(i).PDG == 211) result[2]++;
    #else
      else if ((recop.at(i).type == 11) || (recop.at(i).type == 13)) result[0]++;
      else if (recop.at(i).type == 321) result[1]++;
      else if (recop.at(i).type == 211) result[2]++;
    #endif
  }

  return result;
}

std::vector<float> get_RP_HemisEInfo(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> recop, 
    ROOT::VecOps::RVec<int> should_eval) {
  std::vector<float> result {0., 0., 0.};
  
  for (size_t i = 0; i < recop.size(); ++i){
    if (should_eval.at(i) != (int)1) continue;
    #if edm4hep_VERSION > EDM4HEP_VERSION(0, 10, 5)
      else if ((recop.at(i).PDG == 11) || (recop.at(i).PDG == 13)) {
        if (recop.at(i).energy > result[0]) result[0] = recop.at(i).energy;
      }
      else if (recop.at(i).PDG == 321) {
        if (recop.at(i).energy > result[1]) result[1] = recop.at(i).energy;
      }
      else if (recop.at(i).PDG == 211) {
        if (recop.at(i).energy > result[2]) result[2] = recop.at(i).energy;
      }
    #else
      else if ((recop.at(i).type == 11) || (recop.at(i).type == 13)) {
        if (recop.at(i).energy > result[0]) result[0] = recop.at(i).energy;
      }
      else if (recop.at(i).type == 321) {
        if (recop.at(i).energy > result[1]) result[1] = recop.at(i).energy;
      }
      else if (recop.at(i).type == 211) {
        if (recop.at(i).energy > result[2]) result[2] = recop.at(i).energy; 
      }
    #endif
  }

  return result;
}

std::vector<int> get_maxEparticle_isfromPV(ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> recop,
    ROOT::VecOps::RVec<VertexingUtils::FCCAnalysesVertex> vertex, ROOT::VecOps::RVec<int> should_eval,
    std::vector<float> max_energy) {
  
}

