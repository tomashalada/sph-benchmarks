#!/bin/bash

# Load TNL-SPH solver: Specify path to TNL-SPH directory
export tnlsphdir=${TNL_SPH_PATH}/tnl-sph

# Load DualSPHysics solver: Add link to the DualSPHysics executable
#export dirbin=/storage/brno2/home/haladto1/DualSPHysics_v5.0.5_meta/bin/linux
export dirbin=${DUALSPHYSICS_PATH}/DualSPHysics_v5.2/bin/linux

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${dirbin}
export gencase="${dirbin}/GenCase_linux64"
export dualsphysicscpu="${dirbin}/DualSPHysics5.2CPU_linux64"
export dualsphysicsgpu="${dirbin}/DualSPHysics5.2_linux64"

# Load OpenFPM solver: Source openfpm variables (source openfpm_vars) and specify path on common.mk and example.mk
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${OPENFPM_PATH}/openfpm_installation/openfpm_devices/lib:/openfpm_installation/openfpm_vcluster/lib:${OPENFPM_PATH}/openfpm_dependencies/METIS/lib:${OPENFPM_PATH}/openfpm_dependencies/PARMETIS/lib:${OPENFPM_PATH}/openfpm_dependencies/HDF5/lib:${OPENFPM_PATH}/openfpm_dependencies/LIBHILBERT/lib:${OPENFPM_PATH}/openfpm_dependencies/PETSC/lib:${OPENFPM_PATH}/openfpm_dependencies/OPENBLAS/lib"
export PURE_PYTHON=1
export openfpm_example_mk=/home/tomas/Work/openfpm_source/openfpm/example/example.mk
export openfpm_common_mk=/home/tomas/Work/openfpm_source/openfpm/example/common.mk

# Run benchmark for selected solvers using following flags --tnlsph --dualsphysics --openfpm
cd damBreak3D
./run-benchmark-damBreak3D.sh --tnlsph --dualsphysics --openfpm
