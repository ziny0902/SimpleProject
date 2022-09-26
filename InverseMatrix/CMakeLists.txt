cmake_minimum_required(VERSION 3.22)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
project(cal CXX)
project(inverse CXX)

find_package(BISON)
find_package(FLEX)

BISON_TARGET(cal cal.yy 
    ${CMAKE_CURRENT_BINARY_DIR}/cal.yy.cpp 
    COMPILE_FLAGS
    --header=${CMAKE_CURRENT_BINARY_DIR}/cal.yy.hpp
    )
FLEX_TARGET(cal cal.l
    ${CMAKE_CURRENT_BINARY_DIR}/cal.l.cpp 
    )

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
add_executable(cal
    main.cpp
    ${BISON_cal_OUTPUTS}
    ${FLEX_cal_OUTPUTS}
    calReader.cpp
    ast.cpp
)

add_executable(inverse
    gauss_elimination.cpp
    ${BISON_cal_OUTPUTS}
    ${FLEX_cal_OUTPUTS}
    calReader.cpp
    ast.cpp
)
#TARGET_LINK_LIBRARIES(input_test fl)
