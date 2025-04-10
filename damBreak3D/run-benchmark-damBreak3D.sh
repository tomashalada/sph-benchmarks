#!/bin/bash

## benchmark setup
benchmarkName="dambreak3D"
samples=1
#resolutions="0.02 0.015 0.013 0.012 0.011 0.01 0.009 0.0095 0.0085 0.008 0.0075 0.007 0.0065 0.006"
resolutions="0.02"


## results folder
resultsFolder="results_"$benchmarkName
mkdir -p $resultsFolder

for resolution in ${resolutions}; do
   for sample in $(seq 1 ${samples}); do

      # Setup and run example using TNL-SPH
      # note: this one is necessary since it captures the device metadata are generated here
      if [[ $* == *--tnlsph* ]]; then
         echo "Running TNL-SPH solver with resolution ${resolution}."
         cd resources_tnl-sph
         cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
         cmake --build build --target damBreak3D_WCSPH-DBC_benchmark
         python3 ./init.py --dp=${resolution} --generate-geometry
         python3 ./run.py
         cd ..
         mv resources_tnl-sph/results/time_measurements.json ${resultsFolder}/tnl-sph_${resolution}_${sample}.json
         mv resources_tnl-sph/results/device.metadata.json ${resultsFolder}/tnl-sph_${resolution}_${sample}.device_metadata.json
         mv resources_tnl-sph/results/case_metadata.json ${resultsFolder}/tnl-sph_${resolution}_${sample}.case_metadata.json
      fi

      # Setup and run example using DualSPHysics
      if [[ $* == *--dualsphysics* ]]; then
         echo "Running DualSPHysics solver with resolution ${resolution}."
         cd resoucres_dualsphysics
         cp damBreak3D_WCSPH-DBC_Def_template.xml damBreak3D_WCSPH-DBC_Def.xml
         sed -i "s/resolutionPlaceholder/${resolution}/" damBreak3D_WCSPH-DBC_Def.xml
         ./run.sh ${dualSPHysicsPath}
         cd ..
         mv resoucres_dualsphysics/damBreak3D_WCSPH-DBC_out/Run.out ${resultsFolder}/dualSPHysics_${resolution}_${sample}.out
      fi

      # Setup and run example using OpenFPM
      if [[ $* == *--openfpm* ]]; then
         echo "Running OpenFPM solver with resolution ${resolution}."
         cd resources_openfpm-gpu-opt
         python3 ./setup_and_run.py -resolution=${resolution}
         ./run.sh
         cd ..
         mv resources_openfpm-gpu-opt/timers.json ${resultsFolder}/open-fpm_${resolution}_${sample}.out
      fi
   done
done
