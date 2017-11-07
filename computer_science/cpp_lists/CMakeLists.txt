cmake_minimum_required(VERSION 3.6)
project(Lab08_Project)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES main.cpp ArrayList.cpp ArrayList.h LinkedList.h LinkedList.cpp)
add_executable(Lab08_Project ${SOURCE_FILES})