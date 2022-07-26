from Node import node
from ethereum import utils
from BranchNodeClass import BranchNode
from ExtensionNodeClass import ExtensionNode
from LeafNode import LeafNode

import os
import rlp
from ethereum import utils
from ethereum.utils import to_string
from ethereum.abi import is_string
import copy
from ethereum.utils import decode_hex, ascii_chr, str_to_bytes
from ethereum.utils import encode_hex
from ethereum.fast_rlp import encode_optimized

rlp_encode = encode_optimized


class MerklePatriciaTrie:

    def __init__(self):
        self.root = None
        self.roothash = ""

    def AddNode(self, address, value):

        if self.root == None:
            self.root = LeafNode(address, value)
            return
        if self.checkExist(address):
            print("self node is already exist")
            return
        if self.root.__class__ == LeafNode:
            subaddress = self.longest(self.root.keyEnd, address)
            tempExtension = ExtensionNode(subaddress)
            tempExtension.Addnode(address, value)
            tempExtension.Addnode(self.root.keyEnd, self.root.value)
            self.root = tempExtension
        elif self.root.__class__ == BranchNode:
            self.root.Addnode(address, value)

        # 如果现在的node是 Extension node
        elif self.root.__class__ == ExtensionNode:

            if self.root.sharedNibble[0] == address[0]:
                self.root.Addnode(address, value)

            else:
                tempBranch = BranchNode()
                index = int(self.root.sharedNibble[0])
                self.root.ChangeShared(self.root.sharedNibble[1:len(self.root.sharedNibble)])
                tempBranch.HexArray[index] = self.root
                tempBranch.Addnode(address, value)
                self.root = tempBranch

    def checkExist(self, address):
        return self.root.checkExist(address)

    def UpdateValue(self, address, value):
        if not self.checkExist(address):
            print("self node is not exist")
            return

        Result = self.root.UpdateValue(address, value)
        self.root.HashNode()
        return Result

    def print(self):
        temp = self.root
        temp.printNode(0)
        if type(self.root.hash) == bytes:
            self.roothash = self.root.hash.hex()
        else:
            self.roothash = self.encode_node(self.root.HashNode())
            self.roothash = self.roothash.hex()

        print(self.roothash)

    def encode_node(self, node):
        # if node == BLANK_NODE:
        #     return BLANK_NODE
        rlpnode = rlp_encode(node)

        hashkey = utils.sha3(rlpnode)
        return hashkey

    def longest(self, a, b):
        sub = ""
        for i in range(len(a)):
            if a[i] == b[i]:
                sub += a[i]
            else:
                break
        return sub

    def rest(self, sub, origin):
        temp = ""
        for i in range(len(sub)):
            temp += origin[i]
        return temp

