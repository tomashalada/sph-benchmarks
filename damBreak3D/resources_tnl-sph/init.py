#! /usr/bin/env python3

import numpy as np
import sys
import os
import subprocess
sys.path.append( os.environ[ "tnlsphdir" ] + '/src/tools' )
import saveParticlesVTK
import vtk
from vtk.numpy_interface import dataset_adapter as dsa

def generate_geometry_with_dualsphysics_gencase( dp ):
    subprocess.check_call( [ './generateGeometryWithDualSPHysicsGenCase.sh', str( dp ) ], cwd='./template/generateGeometryWithDualSPHysicsGenCase/' )

def process_dam_break_fluid_particles( setup ):
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName( f'./sources/genCaseGeometries/dambreak_fluid_dp{setup[ "dp" ]}.vtk' )
    reader.ReadAllScalarsOn()
    reader.ReadAllVectorsOn()
    reader.Update()

    polydata = reader.GetOutput()
    np_points_fluid = dsa.WrapDataObject( polydata ).Points

    fluid_n = len( np_points_fluid )
    fluid_r = np.array( np_points_fluid, dtype=float ) #!!
    fluid_v = np.array( dsa.WrapDataObject( polydata ).PointData[ 'Vel' ], dtype=float )
    fluid_rho = np.array( dsa.WrapDataObject( polydata ).PointData[ 'Rhop' ] )
    fluid_p = np.zeros( fluid_n )
    fluid_ptype = np.zeros( fluid_n )

    fluidToWrite = saveParticlesVTK.create_pointcloud_polydata( fluid_r, fluid_v, fluid_rho, fluid_p, fluid_ptype )
    saveParticlesVTK.save_polydata( fluidToWrite, "sources/dambreak_fluid.vtk" )
    setup[ "fluid_n" ] = fluid_n

def process_dam_break_boundary_particles( setup ):
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName( f'./sources/genCaseGeometries/dambreak_bound_dp{setup[ "dp" ]}.vtk' )
    reader.ReadAllScalarsOn()
    reader.ReadAllVectorsOn()
    reader.Update()

    polydata = reader.GetOutput()
    np_points_box = dsa.WrapDataObject( polydata ).Points

    box_n = len( np_points_box )
    box_r = np.array( np_points_box, dtype=float ) #!!
    box_v = np.array( dsa.WrapDataObject( polydata ).PointData[ 'Vel' ], dtype=float )
    box_rho = np.array( dsa.WrapDataObject( polydata ).PointData[ 'Rhop' ] )
    box_p = np.zeros( box_n )
    box_ptype = np.zeros( box_n )

    boundToWrite = saveParticlesVTK.create_pointcloud_polydata( box_r, box_v, box_rho, box_p, box_ptype )
    saveParticlesVTK.save_polydata( boundToWrite, "sources/dambreak_boundary.vtk" )

    setup[ "boundary_n" ] = box_n
    setup[ "domain_origin_x" ] = min( np_points_box[ :, 0 ] )
    setup[ "domain_origin_y" ] = min( np_points_box[ :, 1 ] )
    setup[ "domain_origin_z" ] = min( np_points_box[ :, 2 ] )
    setup[ "domain_end_x" ] = max( np_points_box[ :, 0 ] )
    setup[ "domain_end_y" ] = max( np_points_box[ :, 1 ] )
    setup[ "domain_end_z" ] = max( np_points_box[ :, 2 ] )

def compute_domain_size( setup ):
    search_radius = setup[ "search_radius" ]

    # Resize domain by one layer of cells
    eps = 1.005
    eps_sloshing = 1.5
    domain_origin_x = eps * ( setup[ "domain_origin_x" ] - search_radius )
    domain_origin_y = eps * ( setup[ "domain_origin_y" ] - search_radius )
    domain_origin_z = eps * ( setup[ "domain_origin_z" ] - search_radius )
    domain_end_x = eps * ( setup[ "domain_end_x" ] + search_radius )
    domain_end_y = eps * ( setup[ "domain_end_y" ] + search_radius )
    domain_end_z = eps_sloshing * ( setup[ "domain_end_z" ] + search_radius ) #increase size in z due to sloshing
    domain_size_x = domain_end_x - domain_origin_x
    domain_size_y = domain_end_y - domain_origin_y
    domain_size_z = domain_end_z - domain_origin_z

    extra_parameters = {
        "domain_origin_x" : domain_origin_x,
        "domain_origin_y" : domain_origin_y,
        "domain_origin_z" : domain_origin_z,
        "domain_size_x" : domain_size_x,
        "domain_size_y" : domain_size_y,
        "domain_size_z" : domain_size_z
    }
    setup.update( extra_parameters )

def write_simulation_params( setup ):

    # write parameters to config file
    with open( 'template/config_template.ini', 'r' ) as file :
      config_file = file.read()

    config_file = config_file.replace( 'placeholderSearchRadius', str( round( setup[ "search_radius" ], 7 ) ) )
    config_file = config_file.replace( 'placeholderDomainOrigin-x', str( round( setup[ "domain_origin_x" ], 5 ) ) )
    config_file = config_file.replace( 'placeholderDomainOrigin-y', str( round( setup[ "domain_origin_y" ], 5 ) ) )
    config_file = config_file.replace( 'placeholderDomainOrigin-z', str( round( setup[ "domain_origin_z" ], 5 ) ) )
    config_file = config_file.replace( 'placeholderDomainSize-x', str( round( setup[ "domain_size_x" ], 5  ) ) )
    config_file = config_file.replace( 'placeholderDomainSize-y', str( round( setup[ "domain_size_y" ], 5  ) ) )
    config_file = config_file.replace( 'placeholderDomainSize-z', str( round( setup[ "domain_size_z" ], 5  ) ) )

    config_file = config_file.replace( 'placeholderInitParticleDistance', str( setup[ "dp" ] ) )
    config_file = config_file.replace( 'placeholderSmoothingLength', str( round( setup[ "smoothing_length" ], 7 ) ) )
    config_file = config_file.replace( 'placeholderMass', str( round( setup[ "particle_mass" ], 7 ) ) )
    config_file = config_file.replace( 'placeholderSpeedOfSound', str( setup[ "speed_of_sound" ] ) )
    config_file = config_file.replace( 'placeholderDensity', str( setup[ "density" ] ) )
    config_file = config_file.replace( 'placeholderTimeStep', str( round( setup[ "time_step" ], 8 ) ) )
    config_file = config_file.replace( 'placeholderFluidParticles', str( setup[ "fluid_n" ] ) )
    config_file = config_file.replace( 'placeholderAllocatedFluidParticles', str( setup[ "fluid_n" ] ) )
    config_file = config_file.replace( 'placeholderBoundaryParticles', str( setup[ "boundary_n" ] ) )
    config_file = config_file.replace( 'placeholderAllocatedBoundaryParticles', str( setup[ "boundary_n" ] ) )

    with open( 'sources/config.ini', 'w' ) as file:
      file.write( config_file )

if __name__ == "__main__":
    import sys
    import argparse

    argparser = argparse.ArgumentParser(description="Heat equation example initial condition generator")
    g = argparser.add_argument_group("resolution parameters")
    g.add_argument("--dp", type=float, default=0.02, help="initial distance between particles")
    g.add_argument("--h-coef", type=float, default=2, help="smoothing length coefficient")
    g = argparser.add_argument_group("simulation parameters")
    g.add_argument("--density", type=float, default=1000, help="referential density of the fluid")
    g.add_argument("--speed-of-sound", type=float, default=45.17, help="speed of sound")
    g.add_argument("--cfl", type=float, default=0.15, help="referential density of the fluid")
    g = argparser.add_argument_group("control initialization")
    g.add_argument( '--generate-geometry', default=True, action=argparse.BooleanOptionalAction, help="generate new geometry with gencase" )

    args = argparser.parse_args()

    dambreak_setup = {
        # general parameteres
        "dp" : args.dp,
        "h_coef" : args.h_coef,
        "density" : args.density,
        "speed_of_sound" : args.speed_of_sound,
        "cfl" : args.cfl,
        "particle_mass" : args.density * ( args.dp * args.dp * args.dp ),
        "smoothing_length" : args.h_coef * args.dp,
        "search_radius" :  2 * args.h_coef * args.dp,
        "time_step" : args.cfl * ( args.h_coef * args.dp ) / args.speed_of_sound
    }

    # create necessary folders
    resultsPath = r'./results'
    if not os.path.exists( resultsPath ):
        os.makedirs( resultsPath )

    sourcesPath = r'./sources'
    if not os.path.exists( sourcesPath ):
        os.makedirs( sourcesPath )

    # generate particles using DualSPHysics genCase
    if args.generate_geometry:
        generate_geometry_with_dualsphysics_gencase( dambreak_setup[ "dp" ] )

    # generate particles
    process_dam_break_fluid_particles( dambreak_setup )
    process_dam_break_boundary_particles( dambreak_setup )

    # setup parameters
    compute_domain_size( dambreak_setup )

    # write simulation params
    print( dambreak_setup )
    write_simulation_params( dambreak_setup )
