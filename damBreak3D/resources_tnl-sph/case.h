#include "template/config.h"

int main( int argc, char* argv[] )
{
   Simulation sph;
   sph.init( argc, argv );
   sph.writeProlog();

   while( sph.timeStepping.runTheSimulation() )
   {
      // search for neighbros
      sph.performNeighborSearch();

      // perform interaction with given model
      sph.interact();

      // in case of variable time step, compute the step
      sph.computeTimeStep();

      //integrate
      sph.integrateVerletStep( SPHDefs::BCType::integrateInTime() );

      // check timers and if output should be performed, it is performed
      sph.makeSnapshot();

      // check timers and if measurement or interpolation should be performed, it is performed
      sph.measure();

      // update time step
      sph.updateTime();
   }

   sph.writeEpilog();

   std::map< std::string, std::string > caseMetadata;
   caseMetadata.insert({ "number-of-fluid-particles",    std::to_string( sph.fluid->getNumberOfParticles()    ) } );
   caseMetadata.insert({ "number-of-boundary-particles", std::to_string( sph.boundary->getNumberOfParticles() ) } );
   caseMetadata.insert({ "time-step",                    std::to_string( sph.timeStepping.getTimeStep()       ) } );
   caseMetadata.insert({ "end-time",                     std::to_string( sph.timeStepping.getEndTime()        ) } );
   caseMetadata.insert({ "number-of-time-steps",         std::to_string( sph.timeStepping.getStep()           ) } );
   TNL::Benchmarks::writeMapAsJson( caseMetadata, "results/case_metadata", ".json" );

   std::map< std::string, std::string > metadata = TNL::Benchmarks::getHardwareMetadata();
   TNL::Benchmarks::writeMapAsJson( metadata, "results/device", ".metadata.json" );
}

