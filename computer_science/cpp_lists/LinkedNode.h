//
// Created by Toby Dragon on 10/24/16.
//
//  Completed by Kenneth Potts as course project work
//

#ifndef LINKEDNODE_H
#define LINKEDNODE_H


class LinkedNode {

private:
    int item;
    LinkedNode* next;

public:

    LinkedNode(int item){
        this->item = item;
        next = nullptr;
    }

    int getItem(){
        return item;
    }

    LinkedNode* getNext(){
        return next;
    }

    void setItem(int newItem){
        item = newItem;
    }

    void setNext(LinkedNode* newNext){
        next = newNext;
    }
};


#endif //LINKEDNODE_H
