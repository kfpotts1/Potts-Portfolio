//
//  Completed by Kenneth Potts as course project work

#include <iostream>
#include "ArrayList.h"
#include "LinkedList.h"



long removeTimeTester(List *l) {
    int size = l->size();
    l->resetTotalLinesRun();
    l->remove(size-1);
    //std::cout << "Made it here in tester: " << std::endl;
    long linesRun = l->getTotalLinesRun();
    return linesRun;

}

long isEmptyTimeTester(List* l){
    l->resetTotalLinesRun();
    l->isEmpty();
    long linesRun = l->getTotalLinesRun();
    return linesRun;
}

long getTimeTester(List *l){
    int idxToGet = l->size()-1;
    l->resetTotalLinesRun();
    l->get(idxToGet);
    long linesRun = l->getTotalLinesRun();
    return linesRun;
}

long clearListTimeTester(List *l){
    l->resetTotalLinesRun();
    l->clearList();
    long linesRun = l->getTotalLinesRun();
    return linesRun;
}

long addToFrontListTimeTester(List *l){
    l->resetTotalLinesRun();
    l->addToFront(0);
    long linesRun = l->getTotalLinesRun();
    return linesRun;
}

long addToEndListTimeTester(List *l){
    l->resetTotalLinesRun();
    l->addToEnd(0);
    long linesRun = l->getTotalLinesRun();
    return linesRun;
}



int main() {


    //TIME EFFICIENCY TESTING -------------------------------------

    //  Testing  Time efficiency of Remove function
    //  Same big-O for aList and lList
    int length_to_test = 2000;
    long *removeTimesArrayList = new long[length_to_test];
    List* aList = new ArrayList(5);


    long *removeTimesLinkedList = new long[length_to_test];
    List* lList = new LinkedList();
    for (int i = 0; i < length_to_test; ++i) {
        //std::cout << "Made it here: " << i << std::endl;
        aList->addToEnd(i);
        lList->addToEnd(i);
        removeTimesArrayList[i] = removeTimeTester(aList);
        removeTimesLinkedList[i] = removeTimeTester(lList);
        //std::cout << "Made it here: " << i << std::endl;
        aList->addToEnd(i);
        lList->addToEnd(i);
    }

    aList->clearList();
    lList->clearList();



    // Testing Time efficiency of isEmpty function
    //  Same big-O for both aList and lList

    long *isEmptyTimesArrayList = new long[length_to_test];
    long *isEmptyTimesLinkedList = new long[length_to_test];
    for (int i = 0; i < length_to_test; ++i) {
        aList->addToEnd(i);
        lList->addToEnd(i);
        isEmptyTimesArrayList[i] = isEmptyTimeTester(aList);
        isEmptyTimesLinkedList[i] = isEmptyTimeTester(lList);
        aList->addToEnd(i);
        lList->addToEnd(i);
    }

    aList->clearList();
    lList->clearList();

    // Testing Time efficiency of get function
    // ArrayList has better big-O than LinkedList

    long *getTimesArrayList = new long[length_to_test];
    long *getTimesLinkedList = new long[length_to_test];
    for (int i = 0; i < length_to_test; ++i) {
        aList->addToEnd(i);
        lList->addToEnd(i);
        getTimesArrayList[i] = getTimeTester(aList);
        getTimesLinkedList[i] = getTimeTester(lList);
        aList->addToEnd(i);
        lList->addToEnd(i);
    }

    aList->clearList();
    lList->clearList();

    // Testing Time efficiency of clearList function
    // ArrayList has better big-O than LinkedList

    long *clearListTimesArrayList = new long[length_to_test];
    long *clearListTimesLinkedList = new long[length_to_test];
    for (int i = 0; i < length_to_test; ++i) {
        for (int j = 0; j < i; ++j) {
            aList->addToEnd(j);
            lList->addToEnd(j);
        }
        clearListTimesArrayList[i] = clearListTimeTester(aList);
        clearListTimesLinkedList[i] = clearListTimeTester(lList);
    }

    aList->clearList();
    lList->clearList();


    List* eAList = new ArrayList(5);
    List* elList = new LinkedList();


    // Testing Time efficiency of addToFront function
    // LinkedList has better big-O than ArrayList

    long *addToFrontTimesArrayList = new long[length_to_test];
    long *addToFrontTimesLinkedList = new long[length_to_test];
    for (int i = 0; i < length_to_test; ++i) {
        addToFrontTimesArrayList[i] = addToFrontListTimeTester(eAList);
        addToFrontTimesLinkedList[i] = addToFrontListTimeTester(elList);
    }

    delete eAList; // fully clear lists
    delete elList;
    eAList = nullptr;
    elList = nullptr;


    List* reAList = new ArrayList(5);
    List* relList = new LinkedList();

    aList->clearList();
    lList->clearList();

    // Testing Time efficiency of addToEnd function
    // LinkedList has better big-O than ArrayList

    long *addToEndTimesArrayList = new long[length_to_test];
    long *addToEndTimesLinkedList = new long[length_to_test];
    for (int i = 0; i < length_to_test; ++i) {
        addToEndTimesArrayList[i] = addToEndListTimeTester(reAList);
        addToEndTimesLinkedList[i] = addToEndListTimeTester(relList);
    }

    delete reAList; // fully clear lists
    delete relList;
    reAList = nullptr;
    relList = nullptr;

    delete aList; // fully clear lists
    delete lList;
    aList = new ArrayList(5);
    lList = new LinkedList();





    //Space EFFICIENCY TESTING -------------------------------------

    // Array List more Efficient Than a LinkedList
    // when the Arrays are smalled, otherwise they start to double in large lengths

    long *calcSizeOfArrayList = new long[length_to_test];
    long *calcSizeOfLinkedList = new long[length_to_test];
    for (int i = 0; i < length_to_test/2; ++i) {
        aList->addToEnd(0);
        lList->addToEnd(0);
        calcSizeOfArrayList[i] = aList->calcSizeOf();
        calcSizeOfLinkedList[i] = lList->calcSizeOf();
    }

    aList->clearList();
    lList->clearList();

    for (int i = 0; i < length_to_test/2; ++i) {
        aList->addToEnd(0);
        lList->addToEnd(0);
        calcSizeOfArrayList[length_to_test/2 + i] = aList->calcSizeOf();
        calcSizeOfLinkedList[length_to_test/2 + i] = lList->calcSizeOf();
    }


    delete aList;
    delete lList;
    aList = nullptr;
    lList = nullptr;


    //OUTPUT DATA FOR SPREAD SHEET ----------------------------------
    std::cout << "Comparison of number of lines run by the functions of ArrayLists and Linked Lists \n";
    std::cout << "Comparison of the space efficiency of ArrayLists and Linked Lists \n";
    std::cout << "The following data is from a trial using arrays of up to length " << length_to_test << std::endl;
    std::cout << "Length of Array"
              << "\tRemove Time ArrayList \tremove Time LinkedList \t\t"
              << "isEmpty Time ArrayList\t isEmpty Time LinkedList\t\t"
              << "get Time ArrayList \t get Time LinkedList\t\t"
              << "clear Time ArrayList\t clear Time LinkedList\t\t"
              << "addToEnd Time ArrayList\t addToEnd Time LinkedList\t\t"
              << "addToFront Time ArrayList\t addToFront Time LinkedList\t\t"
              << "calcSizeOf Time ArrayList\t calcSizeOf Time LinkedList"<< std::endl;

    for (int k = 0; k < length_to_test; ++k) {
        std::cout << k
                  << "\t" << removeTimesArrayList[k] << "\t" << removeTimesLinkedList[k] << "\t"
                  << "\t" << isEmptyTimesArrayList[k] << "\t" << isEmptyTimesLinkedList[k] << "\t"
                  << "\t" << getTimesArrayList[k] << "\t" << getTimesLinkedList[k] << "\t"
                  << "\t" << clearListTimesArrayList[k] << "\t" << clearListTimesLinkedList[k] << "\t"
                  << "\t" << addToEndTimesArrayList[k] << "\t" << addToEndTimesLinkedList[k] << "\t"
                  << "\t" << addToFrontTimesArrayList[k] << "\t" << addToFrontTimesLinkedList[k] << "\t"
                  << "\t" << calcSizeOfArrayList[k] << "\t" << calcSizeOfLinkedList[k] << std::endl;
    }


    delete[] removeTimesArrayList;
    delete[] removeTimesLinkedList;
    removeTimesArrayList = nullptr;
    removeTimesLinkedList = nullptr;

    delete[] isEmptyTimesArrayList;
    delete[] isEmptyTimesLinkedList;
    isEmptyTimesArrayList = nullptr;
    isEmptyTimesLinkedList = nullptr;

    delete[] getTimesArrayList;
    delete[] getTimesLinkedList;
    getTimesArrayList = nullptr;
    getTimesLinkedList = nullptr;

    delete[] clearListTimesArrayList;
    delete[] clearListTimesLinkedList;
    clearListTimesArrayList = nullptr;
    clearListTimesLinkedList = nullptr;

    delete[] addToEndTimesArrayList;
    delete[] addToEndTimesLinkedList;
    addToEndTimesArrayList = nullptr;
    addToEndTimesLinkedList = nullptr;

    delete[] addToFrontTimesArrayList;
    delete[] addToFrontTimesLinkedList;
    addToFrontTimesArrayList = nullptr;
    addToFrontTimesLinkedList = nullptr;

    delete[] calcSizeOfArrayList;
    delete[] calcSizeOfLinkedList;
    calcSizeOfArrayList = nullptr;
    calcSizeOfLinkedList = nullptr;


    return 0;
}