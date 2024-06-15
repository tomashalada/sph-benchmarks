#!/bin/bash

## benchmark setup
benchmarkName="local-test"
samples=1
resolutions="0.02"

## results folder
resultsFolder="results_"$benchmarkName
mkdir -p $resultsFolder

for resolution in ${resolutions}; do
   for sample in $(seq 1 ${samples}); do

      # setup and run example using TNL-SPH
      # note: this one is necessary since it captures the device metadata are generated here
      if [[ $* == *--tnlsph* ]]; then
         echo "TNL."
         cd TNL-SPH_resources
         python3 ./generateCaseWithDSPHGenCase.py -resolution=${resolution} --generateNewGeometry
         make clean
         make
         ./damBreak3D_WCSPH-DBC
         cd ..
         mv TNL-SPH_resources/results/time_measurements.json ${resultsFolder}/tnl-sph_${resolution}_${sample}.json
         mv TNL-SPH_resources/results/device.metadata.json ${resultsFolder}/tnl-sph_${resolution}_${sample}.device_metadata.json
         mv TNL-SPH_resources/results/case_metadata.json ${resultsFolder}/tnl-sph_${resolution}_${sample}.case_metadata.json
      fi

      # Setup and run example using DualSPHysics
      if [[ $* == *--dualsphysics* ]]; then
         echo "DSPH."
         cd resoucres_dualsphysics
         cp damBreak3D_WCSPH-DBC_Def_template.xml damBreak3D_WCSPH-DBC_Def.xml
         sed -i "s/resolutionPlaceholder/${resolution}/" damBreak3D_WCSPH-DBC_Def.xml
         ./run.sh ${dualSPHysicsPath}
         cd ..
         mv resoucres_dualsphysics/damBreak3D_WCSPH-DBC_out/Run.out ${resultsFolder}/dualSPHysics_${resolution}_${sample}.out
      fi

      # Setup and run example using OpenFPM
      if [[ $* == *--openfpm* ]]; then
         echo "OpenFPM."
         cd resources_openfpm-gpu-opt
         python3 ./setup_and_run.py
         ./run.sh
         cd ..
         mv resources_openfpm-gpu-opt/timers.json ${resultsFolder}/open-fpm_${resolution}_${sample}.out
      fi
   done
done
