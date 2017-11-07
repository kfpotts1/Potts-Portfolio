//
//  BSTNode.h
//  TreeProject
//
//  Created by Toby Dragon on 11/13/14.
//  Copyright (c) 2014 Toby Dragon. All rights reserved.
//
//  Completed by Kenneth Potts as course project work
//

#ifndef __TreeProject__BSTNode__
#define __TreeProject__BSTNode__

class BTNode{
private:
    int item;
    BTNode* left;
    BTNode* right;
    
public:
    BTNode(int itemIn){
        item = itemIn;
        left = nullptr;
        right = nullptr;
    }
    int getItem(){
        return item;
    }
    BTNode* getLeft(){
        return left;
    }
    BTNode* getRight(){
        return right;
    }
    void setLeft(BTNode* leftIn){
        left = leftIn;
    }
    void setRight(BTNode* rightIn){
        right = rightIn;
    }
};

#endif /* __TreeProject__BSTNode__ */
