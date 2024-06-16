cmake_minimum_required(VERSION 3.24)

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

# Set the project's include path
if(DEFINED ENV{tnlsphdir})
    include_directories($ENV{tnlsphdir}/include)
else()
    message(FATAL_ERROR "Environment variable tnlsphdir is not set")
endif()


# Set the install path for Python modules
# FIXME: for some reason relying on find_package from libs/pytnl fails (dependent target 'Python3::Module' is not defined)
find_package(Python 3 COMPONENTS Interpreter Development REQUIRED)

# TODO:
# Require python vtk

# Add TNL modules
find_package(TNL REQUIRED)
# FIXME: There  is some problem with linking
find_package(TBB REQUIRED COMPONENTS tbb)

# compile the benchmark target
add_executable(damBreak3D_WCSPH-DBC_cuda damBreak3D_WCSPH-DBC.cu)

# add TNL to all targets
target_link_libraries(damBreak3D_WCSPH-DBC_cuda PUBLIC TNL::TNL_CUDA tbb)

set(TARGETS
        damBreak3D_WCSPH-DBC_cuda
)

foreach(target IN ITEMS ${TARGETS})
    # add special flags
    target_compile_definitions(${target} PUBLIC "-DHAVE_CUDA")

    # enable OpenMP for the target
   find_package(OpenMP COMPONENTS CXX)
   if(OPENMP_FOUND)
        target_compile_definitions(${target} PUBLIC "-DHAVE_OPENMP")
        target_link_libraries(${target} PUBLIC OpenMP::OpenMP_CXX)
        # nvcc needs -Xcompiler
        target_compile_options(${target} PUBLIC $<$<CUDA_COMPILER_ID:NVIDIA>: -Xcompiler=-fopenmp >)
   endif()
endforeach()
