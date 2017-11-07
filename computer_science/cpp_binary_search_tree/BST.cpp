//
//  BST.cpp
//  TreeProject
//
//  Created by Toby Dragon on 11/13/14.
//  Copyright (c) 2014 Toby Dragon. All rights reserved.
//
//  Completed by Kenneth Potts as course project work
//

#include "BST.h"
#include <iostream>

BST::BST(){
    root = nullptr;
}

void BST::deleteSubTree(BTNode* current){
    if (current != nullptr) {
        deleteSubTree(current->getLeft());
        deleteSubTree(current->getRight());
        delete current;
    }
}

BST::~BST(){
    deleteSubTree(root);
}

int BST::countNodes(BTNode *current) {
    if (current != nullptr) {
        return 1 + countNodes(current->getRight()) + countNodes(current->getLeft());
    } else {
        return 0;
    }
}

int BST::countNodes() {
    return countNodes(root);
}

int BST::getHeight(BTNode *current){
    if (current != nullptr) {
        int rightHeight = getHeight(current->getRight());
        int leftHeight = getHeight(current->getLeft());
        if (rightHeight > leftHeight) {
            return 1 + rightHeight;
        } else {
            return 1 + leftHeight;
        }
    } else {
        return 0;
    }
}

int BST::getHeight() {
    return getHeight(root);
}


bool BST::find(BTNode *current, int itemToFind) {
    if (current == nullptr){
        return false;
    }
    else if (current->getItem() == itemToFind){
        return true;
    }
    else if(current->getItem() > itemToFind){
        return find(current->getLeft(), itemToFind);
    }
    else { //less than
        return find(current->getRight(), itemToFind);
    }

    return false;
}

bool BST::find(int itemToFind) {
    return find(root, itemToFind);
}

void BST::add(int newValue){
    if (root == nullptr){
        root = new BTNode(newValue);
    }
    else {
        add(root, newValue);
    }
}
void BST::add(BTNode* current,  int newValue){
    if (newValue == current->getItem()){
        throw DuplicateValueException();
    }
    else if (newValue < current->getItem()){
        BTNode* child = current->getLeft();
        if (child != nullptr){
            add(child, newValue);
        }
        else {
            current->setLeft(new BTNode(newValue));
        }
    }
    else { //newValue > current->getItem()
        BTNode* child = current->getRight();
        if (child != nullptr){
            add(child, newValue);
        }
        else {
            current->setRight(new BTNode(newValue));
        }
    }
}

std::string BST::sidewaysTreeStr(){
    std::string str = "----------\n";
    str += sidewaysTreeStr(root, "");
    str+= "----------";
    return str;
}

std::string BST::sidewaysTreeStr(BTNode* const current, const std::string indent){
    if (current != nullptr){
        const std::string right = sidewaysTreeStr(current->getRight(), indent+"\t");
        const std::string thisNode = indent + std::to_string(current->getItem()) + "\n";
        const std::string left = sidewaysTreeStr(current->getLeft(), indent+"\t");
        return right + thisNode + left;
    }
    else {
        return "";
    }
}

void BST::printInOrderList(BTNode *currNode) {
    if (currNode->getLeft() != nullptr) {
        printInOrderList(currNode->getLeft());
    }
    std::cout << currNode->getItem() << ", ";
    if (currNode->getRight() != nullptr) {
        printInOrderList(currNode->getRight());
    }
}

void BST::printInOrderList(){
    if (this != nullptr) {
        printInOrderList(this->root);
    }
}


