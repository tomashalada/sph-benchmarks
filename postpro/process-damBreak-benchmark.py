import re
import os
import json
import pandas as pd
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
import numpy as np
import math
from os.path import exists
from json2html import *

cases = [ "0.02_1", "0.015_1", "0.013_1", "0.012_1", "0.011_1" ,"0.01_1", "0.0095_1", "0.009_1", "0.0085_1", "0.008_1", "0.0075_1", "0.007_1", "0.0065_1", "0.006_1" ]
folder = "./results_metacentrum-nvidia-A40-second-test-added-samples_r5/"

#cases = [ "0.02_1", "0.015_1", "0.013_1", "0.012_1", "0.011_1" ,"0.01_1", "0.0095_1", "0.009_1", "0.0085_1", "0.008_1", "0.00775_1", "0.0075_1", "0.00725_1", "0.007_1", "0.00675_1", "0.0065_1", "0.0064_1", "0.0063_1", "0.0062_1", "0.0061_1", "0.006_1" ]
#folder = "./results_metacentrum-nvidia-A40-second-test-added-more-samples/"

def getCaseDetails( case, TNLSPHTimers, dualSPHTimers, numberOfParticles_all ):
    #tnl-sph details
    caseMetadataFileName = folder + "tnl-sph_" + case + ".case_metadata.json"
    with open( caseMetadataFileName ) as file_metadata:
        caseMetadata_lines = json.load( file_metadata )
        caseMetadata_json_str = json.dumps( caseMetadata_lines )
        caseMetadata_json = json.loads( caseMetadata_json_str )

        detail_string = '<center>' +'<h1> SPH damBreak3D benchmark </h1>'
        detail_string += json2html.convert( json = caseMetadata_json ) + "<br><hr>"
        detail_string += json2html.convert( json = TNLSPHTimers ) + "<br><hr>"
        detail_string += json2html.convert( json = dualSPHTimers ) + "<br><hr>"
        detail_string +='</center>'

        totalNumberOfParticles = float( caseMetadata_json['number-of-boundary-particles'] ) + float( caseMetadata_json['number-of-fluid-particles'] )
        numberOfParticles_all.append( totalNumberOfParticles )

        caseMetadataResultName = "case_" + case + "_detail.html"
        caseMetadataResultFileName = folder + caseMetadataResultName
        with open( caseMetadataResultFileName, 'w') as _file:
            _file.write( detail_string )

        return caseMetadataResultName

def parseDualSPHysicsOutput( case ):
    filename = folder + "dualSPHysics_" + case + ".out"

    timersDictionary = {
        'VA-Init' : 0,
        'NL-Limits' : 0,
        'NL-PreSort' : 0,
        'NL-RadixSort' : 0,
        'NL-CellBegin' : 0,
        'NL-SortData' : 0,
        'NL-OutCheck' : 0,
        'CF-PreForces' : 0,
        'CF-Forces' : 0,
        'SU-Shifting' : 0,
        'SU-ComputeStep' : 0,
        'SU-Floating' : 0,
        'SU-Motion' : 0,
        'SU-Periodic' : 0,
        'SU-ResizeNp' : 0,
        'SU-DownData' : 0,
        'SU-SavePart' : 0,
        'SU-Chrono' : 0,
        'SU-BoundCorr' : 0,
        'SU-InOut' : 0,
        'Steps of simulation' : 0,
        'Steps per second' : 0,
        'Total Runtime' : 0,
        'Simulation Runtime' : 0 }

    with open( filename ) as file:
        lines = file.readlines()
        for line in lines:
            for key, value in timersDictionary.items():
                if key in line:

                    #print(key)
                    #print( re.findall( r"\d+\.\d+", line ) ) if \
                    #        re.findall( r"\d+\.\d+", line ) else print( re.findall( r"\b\d+\b", line ) )

                    parsedValue = float( re.findall( r"\d+\.\d+", line )[ 0 ] ) if \
                            re.findall( r"\d+\.\d+", line ) else  int( re.findall( r"\b\d+\b", line )[ 0 ] )
                    timersDictionary[ key ] = parsedValue

                    break

    #print( "DualSPHysics parsed timers : ", timersDictionary )
    return( timersDictionary )

def parseTNLSPHOutput( case ):
    filename = folder + "tnl-sph_" + case + ".json"
    with open( filename ) as f:
        out_idx = 0
        lines = json.load( f )
        json_str = json.dumps( lines )
        timersDictionary = json.loads( json_str )

        return timersDictionary

def parseOpenFPMOutput( case ):
    filename = folder + "open-fpm_" + case + ".out"
    with open( filename ) as f:
        out_idx = 0
        lines = json.load( f )
        json_str = json.dumps( lines )
        timersDictionary = json.loads( json_str )

        return timersDictionary

def writeArrayToFile( fileName, array ):
    with open( fileName,'w' ) as file:
        for element in array:
            file.write(f"{element}\n")

results_string = '<center>' +'<h1> SPH damBreak3D benchmark </h1>'

#device metadata
deviceMetadataFileName = folder + "tnl-sph_" + cases[ 0 ] + ".device_metadata.json"
with open( deviceMetadataFileName ) as f:
    deviceMetadata_lines = json.load( f )
    deviceMetadata_json_str = json.dumps( deviceMetadata_lines )
    deviceMetadata_json = json.loads( deviceMetadata_json_str )

    deviceString = json2html.convert(json = deviceMetadata_json)
    results_string += deviceString

results_string += "<br><hr>"

#data for plot
numberOfParticles_all = []
tnlSph_totalTime_average_all = []
openfpm_totalTime_average_all = []
dualSPHysics_totalTime_average_all = []

for case in cases:

    dualSPHTimers = parseDualSPHysicsOutput( case )
    TNLSPHTimers = parseTNLSPHOutput( case )
    openfpmTimers = parseOpenFPMOutput( case )

    frames = []
    classes = [ 'dualSPHysics', 'OpenFPM', 'TNL::SPH' ]

    tnlSph_interactionTime = float( TNLSPHTimers['interaction'] ) + float( TNLSPHTimers['integrate'] )
    tnlSph_interactionTime_average = float( TNLSPHTimers['interaction-average'] ) + float( TNLSPHTimers['integrate-average'] )
    tnlSph_searchTime = float( TNLSPHTimers[ 'search' ] )
    tnlSph_searchTime_average = float( TNLSPHTimers[ 'search-average' ] )
    tnlSph_totalTime = float( TNLSPHTimers[ 'total' ] )
    tnlSph_totalTime_average = float( TNLSPHTimers[ 'total-average' ] )

    openfpm_interactionTime = float( openfpmTimers['interaction'] ) + float( openfpmTimers['integrate'] )
    openfpm_interactionTime_average = float( openfpmTimers['interaction-average'] ) + float( openfpmTimers['integrate-average'] )
    openfpm_searchTime = "-"
    openfpm_searchTime_average = "-"
    openfpm_totalTime = float( openfpmTimers[ 'total' ] )
    openfpm_totalTime_average = float( openfpmTimers[ 'total-average' ] )

    dualSph_totalSteps = int( dualSPHTimers['Steps of simulation'] )
    dualSph_interactionTime = float( dualSPHTimers['CF-PreForces'] ) + \
                              float( dualSPHTimers['CF-Forces'] ) + \
                              float( dualSPHTimers['SU-ComputeStep'] )
    dualSph_interactionTime_average = dualSph_interactionTime / dualSph_totalSteps
    dualSph_searchTime = float( dualSPHTimers[ 'NL-Limits' ] ) + \
                         float( dualSPHTimers[ 'NL-PreSort' ] ) + \
                         float( dualSPHTimers[ 'NL-RadixSort' ] ) + \
                         float( dualSPHTimers[ 'NL-CellBegin' ] ) + \
                         float( dualSPHTimers[ 'NL-SortData' ] ) + \
                         float( dualSPHTimers[ 'NL-OutCheck' ] )
    dualSph_searchTime_average = dualSph_searchTime / dualSph_totalSteps
    dualSph_totalTime = float( dualSPHTimers['Simulation Runtime'] )
    dualSph_totalTime_average = dualSph_totalTime / dualSph_totalSteps

    data_f = { 'interaction:' : [ dualSph_interactionTime, openfpm_interactionTime, tnlSph_interactionTime ],
               'interaction-average:' : [ dualSph_interactionTime_average, openfpm_interactionTime_average, tnlSph_interactionTime_average ],
               'search:' :  [ dualSph_searchTime, openfpm_searchTime, tnlSph_searchTime ],
               'search-average:' : [ dualSph_searchTime_average, openfpm_searchTime_average, tnlSph_searchTime_average ],
               'total:' : [ dualSph_totalTime, openfpm_totalTime, tnlSph_totalTime ],
               'total-average:' : [ dualSph_totalTime_average, openfpm_totalTime_average, tnlSph_totalTime_average ] }

    new_df = pd.DataFrame( data_f, classes )
    frames.append( new_df )

    result = pd.concat( frames )
    caseDetail = getCaseDetails( case, TNLSPHTimers, dualSPHTimers, numberOfParticles_all )
    detail_string = ' <a href=\"'+ caseDetail + '\"> Details </a>'
    results_string += '<h2> ' + 'Case ' + case + ' </h2>' + detail_string + result.to_html(index=True,border=2,justify="center") + '<be><hr>'

    #append data for plot:
    tnlSph_totalTime_average_all.append( tnlSph_totalTime_average );
    openfpm_totalTime_average_all.append( openfpm_totalTime_average );
    dualSPHysics_totalTime_average_all.append( dualSph_totalTime_average );

print( numberOfParticles_all )
print( tnlSph_totalTime_average_all )
print( dualSPHysics_totalTime_average_all )
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1,1, figsize=(10, 10))
plt.plot( numberOfParticles_all, tnlSph_totalTime_average_all, linestyle='--', marker='o', color='b', label='TNL-SPH' )
plt.plot( numberOfParticles_all, openfpm_totalTime_average_all, '--', marker='v', color='g', label='OpenFPM' )
plt.plot( numberOfParticles_all, dualSPHysics_totalTime_average_all, '--sr', label='DualSPHysics' )

ax.set_xlabel(r'number of particles', fontsize=24)
ax.set_ylabel(r'$t_{GPU}$/step', fontsize=24)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
ax.grid()
leg = plt.legend()
leg.get_frame().set_edgecolor('k')
ax.legend(fontsize=24, edgecolor='k')

outputFigureName = folder + "results.png"
plt.savefig( outputFigureName , bbox_inches='tight')

results_string += """
<figure>
  <img src="results.png" alt="Trulli" style="width:30%">
</figure>
"""

results_string +='</center>'

outputFileName = folder + "result.html"
with open( outputFileName, 'w') as _file:
    _file.write( results_string )

writeArrayToFile( folder + "parsedData_numberOfParticles.dat", numberOfParticles_all )
writeArrayToFile( folder + "parsedData_tnlSph_totalTime_average.dat", tnlSph_totalTime_average_all )
writeArrayToFile( folder + "parsedData_dualSPHysics_totalTime_average.dat", dualSPHysics_totalTime_average_all )
