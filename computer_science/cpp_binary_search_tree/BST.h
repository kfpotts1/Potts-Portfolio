//
//  BST.h
//  TreeProject
//
//  Created by Toby Dragon on 11/13/14.
//  Copyright (c) 2014 Toby Dragon. All rights reserved.
//
//  Completed by Kenneth Potts as course project work
//

#ifndef __TreeProject__BST__
#define __TreeProject__BST__

#include <string>
#include "BTNode.h"

class DuplicateValueException : std::exception{};

class BST{
private:
    BTNode* root;

    void deleteSubTree(BTNode* current);
    bool find(BTNode* current, int itemToFind);

    void add(BTNode* current, int newItem);
    std::string sidewaysTreeStr(BTNode*  current, std::string indent);

    void printInOrderList(BTNode *currNode);

    int countNodes(BTNode *current);

    int getHeight(BTNode *current);

public:
    BST();
    ~BST();
    bool find(int itemToFind);

    int countNodes();

    int getHeight();

    void add(int newItem);
    std::string sidewaysTreeStr();

    void printInOrderList();
};

#endif /* defined(__TreeProject__BST__) */
