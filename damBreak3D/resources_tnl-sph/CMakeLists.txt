cmake_minimum_required(VERSION 3.26)

# Set default CUDA architecture
if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
   set(CMAKE_CUDA_ARCHITECTURES "native")
endif()

project(TNL-SPH-BENCHMARK
   LANGUAGES CXX CUDA
)

# Require C++17, and disable compiler-specific extensions (if possible)
foreach(lang CXX CUDA)
    set(CMAKE_${lang}_STANDARD 17)
    set(CMAKE_${lang}_STANDARD_REQUIRED ON)
    set(CMAKE_${lang}_EXTENSIONS OFF)
endforeach()

# Set build flags for CXX
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread -Wall -Werror=vla")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELEASE} ${CMAKE_CXX_FLAGS_DEBUG}")

# Set build flags for CUDA
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -Wall")
set(CMAKE_CUDA_FLAGS_DEBUG "-g")
set(CMAKE_CUDA_FLAGS_RELEASE "-O3 -DNDEBUG --expt-relaxed-constexpr --expt-extended-lambda -use_fast_math")
set(CMAKE_CUDA_FLAGS_RELWITHDEBINFO "${CMAKE_CUDA_FLAGS_RELEASE} ${CMAKE_CUDA_FLAGS_DEBUG}")
if(CMAKE_CUDA_COMPILER_ID STREQUAL "NVIDIA")
    set(CMAKE_CUDA_FLAGS_RELWITHDEBINFO "${CMAKE_CUDA_FLAGS_RELWITHDEBINFO} --generate-line-info")
endif()

# Warn about redundant semicolons
if( CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR
    CMAKE_CXX_COMPILER_ID STREQUAL "Clang" OR
    CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang"
)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wextra-semi")
    if( CMAKE_CXX_COMPILER_ID STREQUAL "Clang" OR
        CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang"
    )
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wextra-semi-stmt")
    endif()
endif()

## Find or fetch dependencies
include(FetchContent)
FetchContent_Declare(TNL
    GIT_REPOSITORY https://gitlab.com/tnl-project/tnl.git
    GIT_TAG TH/particles
    EXCLUDE_FROM_ALL
)
set(TNL_EXPORT_INTERFACE_TARGETS ON)  # needed for adding to the interface target
FetchContent_Declare(TNL_SPH
    GIT_REPOSITORY https://gitlab.com/tnl-project/tnl-sph
    GIT_TAG main
    EXCLUDE_FROM_ALL
)
FetchContent_MakeAvailable(TNL TNL_SPH)
FetchContent_MakeAvailable(TNL)

# TODO: We should require python
# find_package(Python 3 COMPONENTS Interpreter Development REQUIRED)
# Require python numpy, vtk

# Download the gencase from DualSPHysics
option(ENABLE_GENCASE_FOR_BENCHMARKS_DOWNLOAD  "Enable downloading GenCase_linux64" FALSE)
if(ENABLE_GENCASE_FOR_BENCHMARKS_DOWNLOAD )
   set(DOWNLOAD_URL "https://github.com/DualSPHysics/DualSPHysics/raw/master/bin/linux/GenCase_linux64")
   set(DESTINATION_DIR "${CMAKE_SOURCE_DIR}/build/_deps/tnl_sph-src/src/tools/3rdparty")
   set(DESTINATION_FILE "${DESTINATION_DIR}/GenCase_linux64")

   # Create the destination directory if it doesn't exist
   file(MAKE_DIRECTORY ${DESTINATION_DIR})

   # Check if the file already exists
   if(NOT EXISTS "${DESTINATION_FILE}")
       # Download the file during the configuration phase
       file(DOWNLOAD
           ${DOWNLOAD_URL}
           ${DESTINATION_FILE}
           SHOW_PROGRESS
           STATUS DOWNLOAD_STATUS
       )
       # Set executable permissions for the downloaded file
       file(CHMOD ${DESTINATION_FILE} PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
   else()
       message(STATUS "GenCase_linux64 already exists at ${DESTINATION_FILE}, skipping download")
   endif()
else()
    message(STATUS "GenCase download is disabled (ENABLE_GENCASE_FOR_BENCHMARKS_DOWNLOAD  is FALSE)")
endif()

# compile the benchmark target
add_executable(damBreak3D_WCSPH-DBC_benchmark damBreak3D_WCSPH-DBC.cu)
# include TNL-SPH
target_include_directories(damBreak3D_WCSPH-DBC_benchmark PUBLIC ${FETCHCONTENT_BASE_DIR}/tnl_sph-src/include)
# add TNL to all targets
target_link_libraries(damBreak3D_WCSPH-DBC_benchmark PUBLIC TNL::TNL)

set(TARGETS
        damBreak3D_WCSPH-DBC_benchmark
)

foreach(target IN ITEMS ${TARGETS})
    # enable OpenMP for the target
   find_package(OpenMP COMPONENTS CXX)
   if(OPENMP_FOUND)
        target_compile_definitions(${target} PUBLIC "-DHAVE_OPENMP")
        target_link_libraries(${target} PUBLIC OpenMP::OpenMP_CXX)
        # nvcc needs -Xcompiler
        target_compile_options(${target} PUBLIC $<$<CUDA_COMPILER_ID:NVIDIA>: -Xcompiler=-fopenmp >)
   endif()
endforeach()
