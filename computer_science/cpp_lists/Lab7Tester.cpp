//
//
// Lab7Tester.cpp
// Designed to test the implementation of List.h and its sub classes
// Created by Kenny Potts on 11/4/16.
//

#include <iostream>
#include <cmath>
#include "LinkedList.h"
#include <string>

//tests the calcSizeOf function for a List object
//returns true if passed and false for fail
//takes a List l and the correct size of the
bool ClacSizeOfListTester(List* l, int checkSize) {

    std::cout << "Checking calcSize function" << std::endl;

    int failCount = 0;

    // uncomment the next line for debugging
    std::cout << "Actual size: " << l->calcSizeOf() << " CheckSize: " << checkSize << std::endl;

    if (l->calcSizeOf() == (checkSize)) {
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed" << std::endl;
        return false;
    }
}

//tests the frontAdd function for a List object
//returns true if passed and false for fail
//takes a List l and the number to be added
bool frontAddListTester(List* l, int toAdd) {
    std::cout << "Checking frontAdd" << std::endl;
    int beforeSize = l->size();
    l->addToFront(toAdd);

    if ((l->get(0) == toAdd) && (beforeSize + 1 == l->size())) {
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed, either returned wrong value or has the wrong size." << std::endl;
        return false;
    }
}

//tests the addToEnd function for a List object
//returns true if passed and false for fail
//takes a List l and the number to be added
bool addToEndListTester(List* l, int toAdd){
    std::cout << "Checking addToEnd" << std::endl;
    int beforeSize = l->size();
    l->addToEnd(toAdd);

    if (l->get(beforeSize) == toAdd){
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed, either returned wrong value or has the wrong size." << std::endl;
        return false;
    }
}

//tests the frontAdd function for a List object
//returns true if passed and false for fail
//takes a List l, the number to be added, and the index of where to add it
bool addListTester(List* l, int toAdd, int idx){
    std::cout << "Checking 'add' function" << std::endl;


    if ((idx >= 0)&&(idx <= l->size())) {
        int beforeSize = l->size();
        l->add(toAdd,idx);

        if ((l->get(idx) == toAdd) && (l->size() == beforeSize+1)){
            std::cout << "pass" << std::endl;
            return true;
        } else {
            std::cout << "failed, either returned wrong value or has the wrong size." << std::endl;
            return false;
        }
    } else {
        try {
            std::cout << "Attempting to get value out of range index" << std::endl;
            l->add(toAdd,idx);
            return false;
        } catch (std::out_of_range& e) {
            std::cout << "pass: Out of Range error: " << e.what() << '\n';
            return true;
        }
    }
}

//tests the 'get' function for a List object
//returns true if passed and false for fail
//takes a List l, the index to get the value from, and the correct value
// also tests the error throwing functionality for a List object in the get function
bool getListTester(List* l, int idx, int checkVal){
    std::cout << "Testing 'get' function" << std::endl;
    if ((idx >= 0)&&(idx < l->size())) {
        if (l->get(idx) == checkVal){
            std::cout << "pass" << std::endl;
            return true;
        } else {
            std::cout << "failed, returned the wrong value." << std::endl;
            return false;
        }
    } else {
        try {
            std::cout << "Attempting to get value out of range index" << std::endl;
            l->get(idx);
            return false;
        } catch (std::out_of_range& e) {
            std::cout << "pass: Out of Range error: " << e.what() << '\n';
            return true;
        }
    }
}

//tests the 'get' function error throwing functionality for a List object
// does not require a checkVal
//returns true if passed and false for fail
//takes a List l, and out of range index
bool getListErrorTester(List* l, int idx){
    return getListTester(l,idx,0);
}

//tests the 'remove' function for a List object
//returns true if passed and false for fail
//takes a List l and the index to get the value from
//will check for the proper error when the index is out of range
bool removeListTester(List* l, int idx){
    std::cout << "Testing 'remove' function" << std::endl;
    int beforeSize = l->size();
    if ((idx >= 0)&&(idx < beforeSize)) {
        int checkVal = l->get(idx);
        int rVal = l->remove(idx);
        if ((rVal == checkVal)&&(beforeSize -1 == l->size())){
            std::cout << "pass" << std::endl;
            return true;
        } else {
            std::cout << "failed, returned the wrong value." << std::endl;
            return false;
        }
    } else {
        try {
            std::cout << "Attempting to get value out of range index" << std::endl;
            l->get(idx);
            return false;
        } catch (std::out_of_range& e) {
            std::cout << "pass: Out of Range error: " << e.what() << '\n';
            return true;
        }
    }
}

//this function tests the isEmpty function for Lists
//takes a List l and the bool listIsEmpty state of the array
//returns true for a successful run and false for a failed test
bool isEmptyListTester(List* l, bool listIsEmpty){
    std::cout << "Testing the isEmpty function" << std::endl;

    if (((l->isEmpty())&&(listIsEmpty))||((!l->isEmpty())&&(!listIsEmpty))){
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed, isEmpty result does not match the given state." << std::endl;
        return false;
    }
}

//this function tests the clearList function for Lists
//takes a List l
//returns true for a successful run and false for a failed test
bool clearListTester(List* l) {
    std::cout << "Testing the 'clearList' function" << std::endl;

    l->clearList();
    if (l->isEmpty()) {
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed, did not clear the list" << std::endl;
        return false;
    }
}

//this function tests the 'find' function for Lists
//takes a List l, the item to find, and the correct index of the item
//if the item is not in the list, -1 should be used as the idx
//returns true for a successful run and false for a failed test
bool findListTester(List* l, int itemToFind, int idx){
    std::cout << "Testing the 'find' function" << std::endl;

    if (l->find(itemToFind) == idx) {
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed" << std::endl;
        return false;
    }
}

//this function tests the 'findLst' function for Lists
//takes a List l, the item to find, and the correct index of the lsat occurrence of the item
//if the item is not in the list, -1 should be used as the idx
//returns true for a successful run and false for a failed test
bool findLastListTester(List* l, int itemToFind, int idx){
    std::cout << "Testing the 'findLast' function" << std::endl;

    if (l->findLast(itemToFind) == idx) {
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed" << std::endl;
        return false;
    }
}

//this function tests the 'findMax' function for Lists
//takes a List l and the correct index of the lsat occurrence of the list max
//if the list is empty, tests for the out of range exception
//returns true for a successful run and false for a failed test
bool findMaxListTester(List* l, int idx){
    //this function tests the findMax function for ArrayLists on varying categories of ArrayLists, and varying values, present or not, repeated or not
    std::cout << "Testing the 'findMax' function" << std::endl;

    if (!l->isEmpty()) {
        if (l->findMax() == idx){
            std::cout << "pass" << std::endl;
            return true;
        } else {
            std::cout << "failed, returned the wrong index." << std::endl;
            return false;
        }
    } else {
        try {
            std::cout << "Attempting to findMax on empty list" << std::endl;
            l->findMax();
            return false;
        } catch (std::out_of_range& e) {
            std::cout << "pass: Out of Range error: " << e.what() << '\n';
            return true;
        }
    }
}

//this function tests the 'toString' function for Lists
//takes a List l and the correct string to check against
//returns true for a successful run and false for a failed test
bool toStringListTester(List* l, std::string correctString){
    //this function tests the toString function for ArrayLists on varying categories of ArrayLists, and varying values, present or not, repeated or not
    std::cout << "Testing the 'toString' function" << std::endl;

    if (l->toString() == correctString){
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed, returned the string." << std::endl;
        return false;
    }
}

//this function tests the 'size' function for Lists
//takes a List l and the correct size to check against
//returns true for a successful run and false for a failed test
bool sizeListTester(List* l, int correctSize){
    std::cout << "Testing the 'size' function" << std::endl;

    if (l->size() == correctSize){
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed, returned the string." << std::endl;
        return false;
    }
}

//this function tests the 'resetTotalLinesRun' function for Lists
//takes a List l
//returns true for a successful run and false for a failed test
bool resetTotalLinesRunListTester(List* l){
    std::cout << "Testing the 'resetTotalLinesRun' function" << std::endl;

    l->resetTotalLinesRun();
    if (l->getTotalLinesRun() == 0){
        std::cout << "pass" << std::endl;
        return true;
    } else {
        std::cout << "failed, returned the string." << std::endl;
        return false;
    }
}


int main(){
    int totalFailures = 0;

    // for the add functions
    List* a0 = new LinkedList();
    List* a1 = new LinkedList();
    totalFailures += !frontAddListTester(a1,5); // tests front add on empty list
    //a1 = {5}

    List* a2 = new LinkedList();
    totalFailures += !addToEndListTester(a2,5); //tests add to end on empty list
    totalFailures += !addListTester(a2,6,0); //tests add function on non-empty list, to index 0
    totalFailures += !addListTester(a2,7,-1); // tests exception case, index out of range
    //a2 = {6, 5}

    List* a3 = new LinkedList();
    totalFailures += !addListTester(a3,-1,0); // tests add to the 0 index of empty list, added negative number
    totalFailures += !addListTester(a3, -6,2); // tests the exception case, index out of range, greater than itemsCount
    totalFailures += !addToEndListTester(a3,-9); // tests the addToEnd function of negative number of list of length 1
    totalFailures += !frontAddListTester(a3,-6); // test the addToFront function with a negative number on an array of length 2
    //a3 = {-6,-1,-9}

    std::cout << "\n\n" << std::endl;

    // for the calcSizeOf function
    LinkedNode* unLinkedNodeSize = new LinkedNode(5);
    LinkedNode* linkedNodeSize = new LinkedNode(5);
    linkedNodeSize->setNext(unLinkedNodeSize);
    int a0Size = sizeof(nullptr)*2 + sizeof(int) + sizeof(long);
    totalFailures += !ClacSizeOfListTester(a0,a0Size);
    //int a1Size = sizeof(LinkedNode*) + sizeof(*unLinkedNodeSize) + sizeof(int) + sizeof(long);
    int a1Size = sizeof(LinkedNode*) + sizeof(*unLinkedNodeSize) + sizeof(int) + sizeof(long);
    totalFailures += !ClacSizeOfListTester(a1,a1Size);

    int a2Size = sizeof(*linkedNodeSize) + sizeof(*unLinkedNodeSize) + sizeof(int) + sizeof(long);
    totalFailures += !ClacSizeOfListTester(a2,a2Size);

    //int a3Size = sizeof(*linkedNodeSize)*2 + sizeof(*unLinkedNodeSize) + sizeof(int) + sizeof(long);
    //totalFailures += !ClacSizeOfListTester(a3,a3Size); //TODO: Resolve calcSizeOf here

    //for debugging:
    /*
    std::cout << "Size of LinkedNode* (pointer to a linked node?): " << sizeof(LinkedNode*) << std::endl;
    std::cout << "Size of *LinkedNodeSize: " << sizeof(*linkedNodeSize) << std::endl;
    std::cout << "Size of *unLinkedNodeSize: " << sizeof(*unLinkedNodeSize) << std::endl;
    std::cout << "Size of nullptr: " << sizeof(nullptr) << std::endl;
    std::cout << "done" << std::endl;
    */

    std::cout << "\n\n" << std::endl;

    // the following code will test the get function for a list
    totalFailures += !getListTester(a0,0,-1); //  empty List, index 0, a0 = {}
    totalFailures += !getListTester(a1,0,5); // List of length 1, index 0, //a1 = {5}
    totalFailures += !getListTester(a1,-1,5); //List of length 1, index out of range, -1, //a1 = {5}
    totalFailures += !getListTester(a1,1,5); // List of length 1, index out of range, 1, //a1 = {5}
    //a2 = {6, 5}

    totalFailures += !getListTester(a2, 1, 5); // List of length 2, second item
    //a3 = {-6,-1,-9}

    totalFailures += !getListTester(a3, 2, -9); // List of length 3, last item

    totalFailures += !getListTester(a3, 1, -1); // List of length 3, middle item

    //std::cout << "here" << std::endl;
    //std::cout << totalFailures << std::endl;

    std::cout << "\n\n" << std::endl;

    // The following code will test the remove function for a list

    totalFailures += !removeListTester(a0,0); // check for error, empty list
    totalFailures += !removeListTester(a3, -1); // check for error, out of range -1 index
    totalFailures += !removeListTester(a3, 3); // check for error, out of range 3 index
    std::cout << "here" << std::endl;
    List* a4 = new LinkedList();
    for (int i = 0; i < 4; ++i) {
        a4->addToEnd(i);
    }
    // a4 = {0, 1, 2, 3}

    totalFailures += !removeListTester(a4,0); // remove first item, length 4 list
    totalFailures += !removeListTester(a4,1); // remove middle item, length 3 list
    totalFailures += !removeListTester(a4,1); // remove last item, length 2 list

    std::cout << "\n\n" << std::endl;
    // The following code will test the isEmpty function for a list
    totalFailures += !isEmptyListTester(a0, true); // empty list
    totalFailures += !isEmptyListTester(a1, false); // list of size 1
    totalFailures += !isEmptyListTester(a2, false); // list of size 2
    totalFailures += !isEmptyListTester(a3, false); // list of size 3
    totalFailures += !isEmptyListTester(a4, false); // list of size 4

    std::cout << "\n\n" << std::endl;
    // The following code will test the 'clear' function for a list

    List* a5 = new LinkedList();

    totalFailures += !clearListTester(a5); // empty list
    for (int i = 0; i < 1; ++i) {
        a5->addToEnd(i);
    }
    totalFailures += !clearListTester(a5); // list of length 1
    for (int i = 0; i < 2; ++i) {
        a5->addToEnd(i);
    }
    totalFailures += !clearListTester(a5); // list of length 2
    for (int i = 0; i < 3; ++i) {
        a5->addToEnd(i);
    }
    totalFailures += !clearListTester(a5); // list of length 3
    for (int i = 0; i < 4; ++i) {
        a5->addToEnd(i);
    }
    totalFailures += !clearListTester(a5); // list of length 4


    std::cout << "\n\n" << std::endl;
    // The following code will test the 'find' function for a list

    totalFailures += !findListTester(a0,-1,-1); // negative item not in empty list
    totalFailures += !findListTester(a0,2,-1); // item not in empty list
    //a1 = {5}
    totalFailures += !findListTester(a1,-1,-1); // item not in list of length 1
    totalFailures += !findListTester(a1,5,0); // item in list of length 1
    //a2 = {6, 5}
    totalFailures += !findListTester(a2,-1,-1); // item not in list of length 2
    totalFailures += !findListTester(a2,6,0); // item in idx=0 list of length 2
    totalFailures += !findListTester(a2,5,1); // item in idx=1 list of length 2
    //a3 = {-6, -1, -9}
    totalFailures += !findListTester(a3,-1,1); // negative number in middle of list of length 3

    for (int i = 0; i < 4; ++i) {
        a5->addToEnd(int(std::pow((-1),i)));
    }
    //a5 = {1, -1, 1, -1}
    totalFailures += !findListTester(a5,-1,1); // repeated number, first occurrence idx = 1
    totalFailures += !findListTester(a5,1,0); // repeated number, first occurrence idx = 0

    std::cout << "\n\n" << std::endl;
    // The following code will test the 'findLast' function for a list

    totalFailures += !findLastListTester(a0,-11,-1); // empty list, not in list
    totalFailures += !findLastListTester(a1,-11,-1); // list of length 1, not in list
    totalFailures += !findLastListTester(a1,5,0); // list of length 1, only item in list
    totalFailures += !findLastListTester(a3,-1,1); // list of length 3, middle item in list
    totalFailures += !findLastListTester(a5,-1,3); // list of length 4, last item in list, repeated
    totalFailures += !findLastListTester(a5,1,2); // list of length 4, 3rd item in list, repeated


    std::cout << "\n\n" << std::endl;
    // The following code will test the 'findMax' function for a list

    totalFailures += !findMaxListTester(a0, -1); // empty list, no max, out of range exception
    totalFailures += !findMaxListTester(a1, 0); //  length 1, max idx = 0
    totalFailures += !findMaxListTester(a2, 0); //  length 2, max idx = 0
    totalFailures += !findMaxListTester(a3, 1); //  length 3, max idx = 1 , negative max
    totalFailures += !findMaxListTester(a5, 0); //  length 4, max idx = 0, repeated max


    std::cout << "\n\n" << std::endl;
    // The following code will test the 'toString' function for a list

    std::string a0String = "{}";
    std::string a1String = "{5}";
    std::string a2String = "{6, 5}";
    std::string a3String = "{-6, -1, -9}";
    std::string a5String = "{1, -1, 1, -1}";


    totalFailures += !toStringListTester(a0, a0String);
    totalFailures += !toStringListTester(a1, a1String);
    totalFailures += !toStringListTester(a2, a2String);
    totalFailures += !toStringListTester(a3, a3String);
    totalFailures += !toStringListTester(a5, a5String);

    std::cout << "\n\n" << std::endl;
    // The following code will test the 'size' function for a list

    totalFailures += !sizeListTester(a0, 0); // empty list, size 0
    totalFailures += !sizeListTester(a1, 1); // size 1
    totalFailures += !sizeListTester(a2, 2); // size 2
    totalFailures += !sizeListTester(a3, 3); // size 3
    totalFailures += !sizeListTester(a5, 4); // size 4


    std::cout << "\n\n" << std::endl;
    // The following code will test the 'size' function for a list


    totalFailures += !resetTotalLinesRunListTester(a0);
    totalFailures += !resetTotalLinesRunListTester(a5);


    std::cout << "\n\n" << std::endl;


    // TESTING FINISHED
    std::cout << "====== Testing Complete ======\n" << std::endl;
    std::cout << "FINISHED WITH " << totalFailures << " TOTAL FAILED TESTS" << std::endl;


    delete a0;
    delete a1;
    delete a2;
    delete a3;
    delete a4;
    delete a5;
    delete unLinkedNodeSize;
    delete linkedNodeSize;
    a0 = nullptr;
    a1 = nullptr;
    a2 = nullptr;
    a3 = nullptr;
    a4 = nullptr;
    a5 = nullptr;
    unLinkedNodeSize = nullptr;
    linkedNodeSize = nullptr;






    return 0;
}