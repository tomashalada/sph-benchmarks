#include <TNL/Devices/Cuda.h>
using Device = TNL::Devices::Cuda;

#include <TNL/Containers/StaticVector.h>
#include <TNL/Algorithms/Segments/CSR.h>
#include <TNL/Algorithms/Segments/Ellpack.h>

#include <TNL/Particles/CellIndexer.h>
#include <TNL/Particles/ParticlesTraits.h>

template< typename Device >
class ParticleSystemConfig
{
   public:
   using DeviceType = Device;

   using GlobalIndexType = int;
   using LocalIndexType = int;
   using CellIndexType = int;
   using RealType = float;

   static constexpr int spaceDimension = 3;

   using UseWithDomainDecomposition = std::false_type;
   using CoordinatesType = Containers::StaticVector< spaceDimension, int >;
   using CellIndexerType = SimpleCellIndex< spaceDimension, ParticleSystemConfig, std::index_sequence< 0, 1, 2 > >;
   using NeighborListType = typename Algorithms::Segments::Ellpack< DeviceType, int >; //deprecated
};

template< typename Device >
class SPHConfig
{
   public:
   using DeviceType = Device;

   using GlobalIndexType = int;
   using LocalIndexType = int;
   using CellIndexType = int;
   using RealType = float;

   static constexpr int spaceDimension = 3;
   static constexpr int numberOfPeriodicBuffers = 0;
};

#include <SPH/Models/EquationOfState.h>
#include <SPH/Models/DiffusiveTerms.h>
#include <SPH/Models/VisousTerms.h>
#include <SPH/Kernels.h>
#include <SPH/Models/WCSPH_DBC/BoundaryConditionsTypes.h>
#include <SPH/Models/WCSPH_DBC/IntegrationSchemes/VerletScheme.h>
#include <SPH/TimeStep.h>

/**
 * Particle system reader.
 */
#include <TNL/Particles/Readers/VTKReader.h>
#include <TNL/Particles/Writers/VTKWriter.h>
#include <TNL/Particles/Readers/readSPHSimulation.h>

template< typename Device >
class SPHParams
{
public:
   using SPHConfig = SPHConfig< Device >;

   using KernelFunction = TNL::SPH::KernelFunctions::WendlandKernel< SPHConfig >;
   using DiffusiveTerm = TNL::SPH::DiffusiveTerms::MolteniDiffusiveTerm< SPHConfig >;
   using ViscousTerm = TNL::SPH::ViscousTerms::ArtificialViscosity< SPHConfig >;
   using EOS = TNL::SPH::EquationsOfState::TaitWeaklyCompressibleEOS< SPHConfig >;
   using BCType = TNL::SPH::WCSPH_BCTypes::DBC;
   using TimeStepping = TNL::SPH::ConstantTimeStep< SPHConfig >;
   using IntegrationScheme = TNL::SPH::IntegrationSchemes::VerletScheme< SPHConfig >;
};

using SPHDefs = SPHParams< Device >;

using ParticlesConfig = ParticleSystemConfig< Device >;

/**
 * Include type of particle system.
 */
#include <TNL/Particles/ParticlesLinkedList.h>
using ParticlesSys = TNL::ParticleSystem::ParticlesLinkedList< ParticlesConfig, Device >;

/**
 * Include particular formulation of SPH method.
 */
#include <SPH/Models/WCSPH_DBC/Interactions.h>
using Model = TNL::SPH::WCSPH_DBC< ParticlesSys, SPHParams< Device > >;

/**
 * Include type of SPH simulation.
 */
#include <SPH/SPHMultiset_CFD.h>
using Simulation = TNL::SPH::SPHMultiset_CFD< Model >;

