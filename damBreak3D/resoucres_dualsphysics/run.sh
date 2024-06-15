#!/bin/bash
fail () {
    echo Execution aborted.
    exit 1
}

#jmeno uhlohy, vystupni slozky
export name=damBreak3D_WCSPH-DBC
export dirout=${name}_out
export diroutdata=${dirout}/data

#nacteni prislusnych souboru
#export dirbin=$1
#export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${dirbin}
#export gencase="${dirbin}/GenCase_linux64"
#export dualsphysicscpu="${dirbin}/DualSPHysics5.0CPU_linux64"
#export dualsphysicsgpu="${dirbin}/DualSPHysics5.0_linux64"

# "dirout" to store results is removed if it already exists
if [ -e ${dirout} ]; then rm -r ${dirout}; fi

# Executes GenCase4 to create initial files for simulation.
${gencase} ${name}_Def ${dirout}/${name} -save:all
if [ $? -ne 0 ] ; then fail; fi

# Executes DualSPHysics to simulate SPH method.
${dualsphysicsgpu} -gpu ${dirout}/${name} ${dirout} -dirdataout data -svres
if [ $? -ne 0 ] ; then fail; fi
