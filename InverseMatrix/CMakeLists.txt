cmake_minimum_required(VERSION 3.22)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
project(inverse CXX)

find_package(BISON)
find_package(FLEX)

BISON_TARGET(inverse cal.yy 
    ${CMAKE_CURRENT_BINARY_DIR}/cal.yy.cpp 
    COMPILE_FLAGS
    --header=${CMAKE_CURRENT_BINARY_DIR}/cal.yy.hpp
    )
FLEX_TARGET(inverse cal.l
    ${CMAKE_CURRENT_BINARY_DIR}/cal.l.cpp 
    )
#ADD_FLEX_BISON_DEPENDENCY(lex syntax)
include_directories(${CMAKE_CURRENT_BINARY_DIR})
find_package(Boost REQUIRED COMPONENTS log_setup log)

add_executable(inverse
    ${BISON_inverse_OUTPUTS}
    ${FLEX_inverse_OUTPUTS}
    calReader.cpp
    ast.cpp
    args.cpp
    log.cpp
    main.cpp
)

target_link_libraries(inverse ${Boost_LIBRARIES})
