import sys
import argparse
import math

# Parse the input arguments
parser = argparse.ArgumentParser()
parser.add_argument( "-resolution", default=0.02, type=float )
parser.add_argument( "-smoothingLengthCoef", default=2.0, type=float )

args = parser.parse_args()
dp = args.resolution
smoothingLengthCoef = args.smoothingLengthCoef

# Set or compute remaining variables
rho0 = 1000.
smoothingLength = dp * smoothingLengthCoef
particleMass = ( dp * dp * dp ) * rho0
minTimeStep = 1.0e-9

# Dimensions of the problem domain
fpm_box_x = 3.3210; fpm_box_y = 1.1065; fpm_box_z = 1.511

# Compute new sizes ( "sz" variable based on the estimated domain size )
sz_x = math.ceil( (fpm_box_x + 0.05) / dp )
sz_y = math.ceil( (fpm_box_y + 0.05) / dp )
sz_z = math.ceil( (fpm_box_z + 0.05) / dp )
print( f'Variable [sz] related to domain size: [ { sz_x, sz_y, sz_z } ]' )

# Compute exact domain limits based on the new sizes "sz"
box_x_adjusted = sz_x * dp - 0.05
box_y_adjusted = sz_y * dp - 0.05
box_z_adjusted = sz_z * dp - 0.05
print( f'Box dimensions computed based on the [sz] and [dp] variables: [ {box_x_adjusted}, {box_y_adjusted}, {box_y_adjusted} ]' )

# Write the settings into file with example
with open( './main_template.cu', 'r' ) as file :
  fileSPHConf = file.read()

fileSPHConf = fileSPHConf.replace( 'placeholderMass', str( round( particleMass, 8 ) ) )
fileSPHConf = fileSPHConf.replace( 'placeholderDensity', str( rho0 ))
fileSPHConf = fileSPHConf.replace( 'placeholderInitParticleDistance', str( dp ) )
fileSPHConf = fileSPHConf.replace( 'placeholderSmoothingLength', str( smoothingLength ) )
fileSPHConf = fileSPHConf.replace( 'placeholderMinTimeStep', str( minTimeStep ) )

fileSPHConf = fileSPHConf.replace( 'placeholderGridXSize', str( sz_x ) )
fileSPHConf = fileSPHConf.replace( 'placeholderGridYSize', str( sz_y ) )
fileSPHConf = fileSPHConf.replace( 'placeholderGridZSize', str( sz_z ) )

with open( './main.cu', 'w' ) as file:
  file.write( fileSPHConf )
