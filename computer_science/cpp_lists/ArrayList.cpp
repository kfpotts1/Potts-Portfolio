//ArrayList.cpp
//this Library implements the ArrayList and its functions
// Created by Kenny Potts on 10/17/16.
//
//  Completed by Kenneth Potts as course project work
//

#include <iostream>
#include "ArrayList.h"

ArrayList::ArrayList(int initialCapacity) {
    if (initialCapacity >= 0) {
        this->array = new int[initialCapacity];
        this->currCapacity = initialCapacity;
    } else {
        this->array = new int[5];
        this->currCapacity = 5;
    }
    this->currItemCount = 0;
    this->totalLinesRun = 4;
}

ArrayList::~ArrayList() {
    //std::cout << "ArrayList object as been deconstructed" << std::endl; // uncomment for debugging if needed
    delete[] this->array; //deletes the array from heap
    this->array = nullptr; // nullifies pointer
}

void ArrayList::doubleCapacity() {
    long total = 0;
    total +=2;
    if (this->currCapacity != 0){
        this->currCapacity = (this->currCapacity)*2; // doubles capacity
    } else {
        this->currCapacity = 1;
    }
    int* newA = new int[this->currCapacity];
    total +=2;
    for (int i = 0; i < this->currItemCount; ++i) {
        total +=3;
        newA[i] = this->array[i]; // copies all current values in array
    }
    total +=3;
    delete[] this->array; // deletes old array
    this->array = newA; //points array to new double capacity array
    newA = nullptr;
    this->totalLinesRun += total;
}

void ArrayList::addToFront(int itemToAdd) {
    int* newA; // init new ptr for new array
    this->currItemCount++;
    this->totalLinesRun +=3;
    if (this->currItemCount == this->currCapacity){
        this->currCapacity = (this->currCapacity)*2; // doubles capacity
        newA = new int[this->currCapacity]; //creates new array
        newA[0] = itemToAdd; // adds item to beginning
        this->totalLinesRun +=4;
        for (int i = 1; i < this->currItemCount; ++i) {
            this->totalLinesRun +=3;
            newA[i] = this->array[i-1]; // copies all current values in array after new value
        }
    } else {
        newA = new int[this->currCapacity]; //creates new array
        newA[0] = itemToAdd; // adds item to beginning
        this->totalLinesRun +=3;
        for (int i = 1; i < this->currItemCount; ++i) {
            this->totalLinesRun +=3;
            newA[i] = this->array[i-1]; // copies all current values in array after new value
        }
    }
    this->totalLinesRun +=3;
    delete[] this->array; // deletes old array
    this->array = newA; //points array to new double capacity array
    newA = nullptr;
}

void ArrayList::addToEnd(int itemToAdd) {
    if (this->currItemCount == this->currCapacity) {
        this->doubleCapacity();
    }
    this->array[this->currItemCount] = itemToAdd;
    this->totalLinesRun +=2;
    this->currItemCount++;
}

void ArrayList::add(int itemToAdd, int index) {
    this->totalLinesRun++;
    if ((index >= 0) && (index <= this->currItemCount)) {
        int* newA; // init new ptr for new array
        this->currItemCount++;
        this->totalLinesRun +=3;
        if (this->currItemCount == this->currCapacity){
            this->currCapacity = (this->currCapacity)*2; // doubles capacity
            newA = new int[this->currCapacity]; //creates new array
            this->totalLinesRun +=3;
            for (int i = 0; i < this->currItemCount; ++i) {
                this->totalLinesRun +=3;
                if (index == i){
                    newA[i] = itemToAdd; // adds new item
                } else if (i < index) {
                    newA[i] = this->array[i]; //adds items from old array
                } else {
                    newA[i] = this->array[i-1]; // adds items from old array shifted after new item
                }
            }
        } else {
            newA = new int[this->currCapacity]; //creates new array
            this->totalLinesRun +=2;
            for (int i = 0; i < this->currItemCount; ++i) {
                this->totalLinesRun +=3;
                if (index == i){
                    this->totalLinesRun +=1;
                    newA[i] = itemToAdd; // adds new item
                } else if (i < index) {
                    this->totalLinesRun +=2;
                    newA[i] = this->array[i]; //adds items from old array
                } else {
                    this->totalLinesRun +=1;
                    newA[i] = this->array[i-1]; // adds items from old array shifted after new item
                }
            }
        }
        this->totalLinesRun +=3;
        delete[] this->array; // deletes old array
        this->array = newA; //points array to new double capacity array
        newA = nullptr;
    } else {
        this->totalLinesRun++;
        throw std::out_of_range("Index out of range"); // throws out of range exception
    }
}

int ArrayList::get(int index) {
    this->totalLinesRun++;
    if ((index >= 0) && (index < this->currItemCount)) { // checks index in range
        this->totalLinesRun++;
        return this->array[index];
    } else {
        this->totalLinesRun++;
        throw std::out_of_range("Index out of range"); // throws out of range exception
    }
}

int ArrayList::remove(int index) {
    this->totalLinesRun++;
    if ((index >= 0) && (index < this->currItemCount)) { // checks index in range
        this->totalLinesRun += 4;

        int* newA = new int[this->currCapacity];
        int val;
        for (int i = 0; i < this->currItemCount; ++i) {
            this->totalLinesRun +=3;
            if (index == i){
                this->totalLinesRun +=2;
                val = this->array[i]; // value to be returned and removed
                newA[i] = this->array[i+1]; // skips over value
            } else if (i < index) {
                this->totalLinesRun +=2;
                newA[i] = this->array[i]; //adds items from old array
            } else {
                this->totalLinesRun +=1;
                newA[i] = this->array[i+1]; // adds items from old array shifted after item removed
            }
        }
        this->currItemCount--;
        delete[] this->array;
        this->array = newA;
        newA = nullptr;
        return val;
    } else {
        this->totalLinesRun++;
        throw std::out_of_range("Index out of range"); // throws out of range exception
    }
}

bool ArrayList::isEmpty() {
    this->totalLinesRun +=2;
    if (this->currItemCount == 0) {
        return true; // returns true for no valid items
    } else {
        return false;
    }
}

int ArrayList::size() {
    this->totalLinesRun++;
    return this->currItemCount;
}

void ArrayList::clearList() {
    this->totalLinesRun++;
    this->currItemCount = 0; // doesn't change values, only changes currItemCount to 0
}

int ArrayList::find(int itemToFind) {
    this->totalLinesRun++;
    for (int i = 0; i < this->currItemCount; ++i) { //loops through the num of valid items
        this->totalLinesRun +=3;
        if (this->array[i] == itemToFind) {
            this->totalLinesRun++;
            return i; //returns index of first occurrence
        }
    }
    this->totalLinesRun++;
    return -1; // return -1 if the item was not found
}

int ArrayList::findLast(int itemToFind) {
    this->totalLinesRun +=2;
    int idx = -1; // initializes as -1, remains -1 if item not in array
    for (int i = 0; i < this->currItemCount; ++i) {
        this->totalLinesRun +=3;
        if (this->array[i] == itemToFind) {
            this->totalLinesRun++;
            idx = i; // resets idx at every occurrence (final occurrence remains)
        }
    }
    this->totalLinesRun++;
    return idx;
}

int ArrayList::findMax() {
    this->totalLinesRun++;
    if (this->currItemCount > 0) { // checks index in range
        this->totalLinesRun +=2;
        int idx = 0;
        for (int i = 0; i < this->currItemCount; ++i) {
            this->totalLinesRun +=4;
            if (this->array[i] > this->array[idx]) { // compares current value with max
                this->totalLinesRun++;
                idx = i; // updates max index
            }
        }
        this->totalLinesRun++;
        return idx;
    } else {
        this->totalLinesRun++;
        throw std::out_of_range("Operation not valid for arrays of size 0"); // throws out of range exception
    }
}

std::string ArrayList::toString() {
    this->totalLinesRun +=2;
    std::string newStr = "{"; // starts string with {
    for (int i = 0; i < this->currItemCount; ++i) {
        this->totalLinesRun +=3;
        if (i > 0) {
            this->totalLinesRun++;
            newStr += " "; //ensures proper space formatting
        }
        this->totalLinesRun +=2;
        newStr += std::to_string(this->array[i]); // convert int to string
        if (i != this->currItemCount - 1) {
            this->totalLinesRun++;
            newStr += ",";
        }
    }
    this->totalLinesRun +=2;
    newStr += "}"; // end string with }
    return newStr;
}

long ArrayList::getTotalLinesRun() {
    this->totalLinesRun++;
    return (long) this->totalLinesRun;
}

void ArrayList::resetTotalLinesRun() {
    this->totalLinesRun++;
    this->totalLinesRun = 0;
}

int ArrayList::calcSizeOf() {
    this->totalLinesRun++;
    return ((this->currCapacity) + 3)*sizeof(int);; // sizeof(int) = 4 (bytes)
    // object holds one int[] of length currCapacity and 3 ints
}
