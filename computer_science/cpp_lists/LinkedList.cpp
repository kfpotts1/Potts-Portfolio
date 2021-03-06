//
// Created by Kenny Potts on 11/3/16.
//
//  Completed by Kenneth Potts as course project work
//

#include "LinkedList.h"
#include <iostream>

LinkedList::LinkedList() {
    this->start = nullptr;
    this->end = nullptr;
    this->currItemCount = 0;
    this->totalLinesRun = 3;
}

LinkedList::~LinkedList() {
    LinkedNode* currNode = this->start;
    while (currNode != nullptr) {
        LinkedNode* toDel = currNode;
        currNode = currNode->getNext();
        delete toDel;
    }
    this->start = nullptr;
    this->end = nullptr;
    this->totalLinesRun = 0;
}

void LinkedList::addToEnd(int itemToAdd) {
    this->totalLinesRun += 6;
    LinkedNode* n = new LinkedNode(itemToAdd);
    if (this->currItemCount) {
        this->end->setNext(n);
        this->end = n;
    } else {
        this->start = n;
        this->end = n;
    }
    this->currItemCount++;

}

void LinkedList::addToFront(int itemToAdd) {
    this->totalLinesRun += 7;
    LinkedNode* n = new LinkedNode(itemToAdd);
    n->setNext(this->start);
    this->start = n;
    if (!this->currItemCount) {
        this->end = n;
    }
    this->currItemCount++;
}

void LinkedList::add(int itemToAdd, int index) {
    this->totalLinesRun += 2;
    if ((index>=0)&&(index <= currItemCount)) {

        if (!this->currItemCount || !index) {
            //std::cout << "made it here" << std::endl;
            this->addToFront(itemToAdd);
        } else if (index == this->currItemCount) {
            this->addToEnd(itemToAdd);
        } else {
            this->totalLinesRun += 5;
            LinkedNode *n = new LinkedNode(itemToAdd);
            LinkedNode *pointNode = this->start;
            for (int i = 1; i < index; ++i) {
                this->totalLinesRun += 4;
                pointNode = pointNode->getNext();
            }
            this->totalLinesRun += 4;
            n->setNext(pointNode->getNext());
            pointNode->setNext(n);
            this->currItemCount++;
        }

    } else {
        this->totalLinesRun += 1;
        throw std::out_of_range("Index out of range"); // throws out of range exception
    }
}

int LinkedList::get(int index) {
    this->totalLinesRun += 2;
    if ((index>=0)&&(index < currItemCount)) {
        this->totalLinesRun += 2;
        LinkedNode *currNode = this->start;
        for (int i = 0; i < index; ++i) {
            this->totalLinesRun += 4;
            currNode = currNode->getNext();
        }
        this->totalLinesRun += 2;
        return currNode->getItem();
    } else {
        this->totalLinesRun += 1;
        throw std::out_of_range("Index out of range"); // throws out of range exception
    }
}

int LinkedList::remove(int index) {
    this->totalLinesRun += 2;
    if ((index>0)&&(index < currItemCount-1)) {
        this->totalLinesRun += 2;
        LinkedNode *pointNode = this->start;
        for (int i = 1; i < index; ++i) {
            this->totalLinesRun += 4;
            pointNode = pointNode->getNext();
        }
        this->totalLinesRun += 10;
        LinkedNode *toDel = pointNode->getNext();
        int val = toDel->getItem();
        pointNode->setNext(toDel->getNext());
        delete toDel;
        toDel = nullptr;
        this->currItemCount--;
        return val;
    } else if ((index>0)&&(index == currItemCount-1)) {
        this->totalLinesRun += 2;
        LinkedNode *pointNode = this->start;
        for (int i = 1; i < index; ++i) {
            this->totalLinesRun += 4;
            pointNode = pointNode->getNext();
        }
        this->totalLinesRun += 10;
        LinkedNode *toDel = pointNode->getNext();
        int val = toDel->getItem();
        pointNode->setNext(nullptr);
        this->end = pointNode;
        delete toDel;
        toDel = nullptr;
        this->currItemCount--;
        return val;
    } else if ((!index)&&(index == currItemCount-1)) {
        LinkedNode* toDel = this->start;
        int val = toDel->getItem();
        this->start = toDel->getNext();
        this->end = toDel->getNext();
        delete toDel;
        toDel = nullptr;
        this->currItemCount--;
        return val;
    } else if (!index && (index < currItemCount)) {
        LinkedNode* toDel = this->start;
        int val = toDel->getItem();
        this->start = toDel->getNext();
        delete toDel;
        toDel = nullptr;
        this->currItemCount--;
        return val;
    } else {
        this->totalLinesRun += 1;
        throw std::out_of_range("Index out of range"); // throws out of range exception
    }
}

bool LinkedList::isEmpty() {
    this->totalLinesRun++;
    return !this->currItemCount;
}

int LinkedList::size() {
    this->totalLinesRun++;
    return this->currItemCount;
}

void LinkedList::clearList() {
    this->totalLinesRun +=2;
    LinkedNode* currNode = this->start;
    while (currNode != nullptr) {
        this->totalLinesRun +=4;
        LinkedNode* toDel = currNode;
        currNode = currNode->getNext();
        delete toDel;
    }
    this->totalLinesRun +=3;
    this->start = nullptr;
    this->end = nullptr;
    this->currItemCount = 0;
}

int LinkedList::find(int itemToFind) {
    int idx = -1;
    this->totalLinesRun += 3;
    LinkedNode *currNode = this->start;
    for (int i = 0; i < this->currItemCount; ++i) {
        this->totalLinesRun += 4;
        if (currNode->getItem() == itemToFind) {
            this->totalLinesRun ++;
            return i;
        }
        currNode = currNode->getNext();
    }
    this->totalLinesRun += 1;
    return idx;
}

int LinkedList::findLast(int itemToFind) {
    int idx = -1;
    this->totalLinesRun += 3;
    LinkedNode *currNode = this->start;
    for (int i = 0; i < this->currItemCount; ++i) {
        this->totalLinesRun += 4;
        if (currNode->getItem() == itemToFind) {
            this->totalLinesRun ++;
            idx = i;
        }
        currNode = currNode->getNext();
    }
    this->totalLinesRun += 1;
    return idx;
}

int LinkedList::findMax() {
    this->totalLinesRun ++;
    if (this->currItemCount) {
        int idx = 0;
        LinkedNode *currNode = this->start;
        int maxVal = currNode->getItem();
        this->totalLinesRun += 5;
        for (int i = 0; i < this->currItemCount; ++i) {
            this->totalLinesRun += 4;
            if (currNode->getItem() > maxVal) {
                this->totalLinesRun++;
                idx = i;
            }
            currNode = currNode->getNext();
        }
        this->totalLinesRun += 1;
        return idx;
    } else {
        this->totalLinesRun += 1;
        throw std::out_of_range("Index out of range"); // throws out of range exception
    }
}

std::string LinkedList::toString() {
    this->totalLinesRun +=3;
    std::string newStr = "{"; // starts string with {
    LinkedNode* currNode = this->start;
    for (int i = 0; i < this->currItemCount; ++i) {
        this->totalLinesRun +=3;
        if (i > 0) {
            this->totalLinesRun++;
            newStr += " "; //ensures proper space formatting
        }
        this->totalLinesRun +=3;
        newStr += std::to_string(currNode->getItem()); // convert int to string
        if (i != this->currItemCount - 1) {
            this->totalLinesRun++;
            newStr += ",";
        }
        currNode = currNode->getNext();
    }
    this->totalLinesRun +=2;
    newStr += "}"; // end string with }
    return newStr;
}

long LinkedList::getTotalLinesRun() {
    return this->totalLinesRun;
}

void LinkedList::resetTotalLinesRun() {
    this->totalLinesRun = 0;
}

int LinkedList::calcSizeOf() {
    int totalSize = sizeof(start) + sizeof(end) //start and end
                    + sizeof(this->currItemCount) + sizeof(this->totalLinesRun);
    LinkedNode* currNode = this->start;
    while (currNode != nullptr) {
        totalSize += sizeof(currNode);
        currNode = currNode->getNext();
    }
    return totalSize;
}