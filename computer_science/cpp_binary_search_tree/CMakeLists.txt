cmake_minimum_required(VERSION 3.6)
project(220_36_BstStart)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES main.cpp BST.cpp)
add_executable(220_36_BstStart ${SOURCE_FILES})