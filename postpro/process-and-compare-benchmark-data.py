import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots( 1,1, figsize=(10, 10) )

outputFigureName = 'results_compare-search-and-block-search.png'

numberOfParticles_all = np.genfromtxt( './9results_local-test/parsedData_numberOfParticles.dat' )
timeData_all = np.genfromtxt( './9results_local-test/parsedData_tnlSph_totalTime_average.dat' )
plt.plot( numberOfParticles_all, timeData_all, '--sr', label='block search' )

numberOfParticles_all = np.genfromtxt( './27results_local-test/parsedData_numberOfParticles.dat' )
timeData_all = np.genfromtxt( './27results_local-test/parsedData_tnlSph_totalTime_average.dat' )
plt.plot( numberOfParticles_all, timeData_all, '--ok', label='simple search' )

numberOfParticles_all = np.genfromtxt( './results_local-test_old/parsedData_numberOfParticles.dat' )
timeData_all = np.genfromtxt( './results_local-test_old/parsedData_tnlSph_totalTime_average.dat' )
plt.plot( numberOfParticles_all, timeData_all, '--ob', label='marked as old' )

ax.set_xlabel(r'number of particles', fontsize=24)
ax.set_ylabel(r'$t_{GPU}$/step', fontsize=24)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
ax.grid()
leg = plt.legend()
leg.get_frame().set_edgecolor('k')
ax.legend(fontsize=24, edgecolor='k')

plt.savefig( outputFigureName , bbox_inches='tight')
