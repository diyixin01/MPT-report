from Node import node
from LeafNode import LeafNode
from ethereum import utils
#说明这个文件构建的是一个trie的分支节点类
#用于后续功能实现的调用！

rlp_encode = encode_optimized


# 节点类，将之前写的节点之间的操作在集成一下
class node(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def printNode():
        return NotImplemented

    @abc.abstractmethod
    def Addnode():
        return NotImplemented

    @abc.abstractmethod
    def UpdateValue():
        return NotImplemented

    @abc.abstractmethod
    def checkExist():
        return NotImplemented

    def encode_node(self, node):
        rlpnode = rlp_encode(node)
        if len(rlpnode) < 32:
            return node
        hashkey = utils.sha3(rlpnode)
        return hashkey

    # 判定是否超过节点数据的最大长度
    def longest(self, a, b):
        sub = ""
        for i in range(len(a)):
            if a[i] == b[i]:
                sub += a[i]
            else:
                break
        return sub

    # node中将the rest of key级联到data部分的最后
    def rest(self, sub, origin):
        temp = ""
        for i in range(len(sub), len(origin)):
            temp += origin[i]
        return
class LeafNode(node):

    def __init__(self, k, v):
        self.hash = ""
        self.keyEnd = ""
        self.value = ""
        self.Addnode(k, v)

    def printNode(self, Level):
        space = "    " * Level
        print(space, "LeafNode : ")
        if self.prefix == 2:
            print(space, ["20" + self.keyEnd, self.value])

        elif self.prefix == 3:
            print(space, ["3" + self.keyEnd, self.value])

    def Addnode(self, k, v):
        if len(k) % 2 == 0:
            # 以奇数结尾的key标记的叶子节点！
            self.prefix = 2
        else:
            # 以偶数结尾的key标记的叶子节点！
            self.prefix = 3
        self.keyEnd = k
        self.value = v
        self.HashNode()
        return self.hash

    def HashNode(self):
        if self.prefix == 2:
            self.hash = self.encode_node([bytes.fromhex("20" + self.keyEnd), bytes(self.value, 'utf-8')])  # 偶數

        elif self.prefix == 3:
            self.hash = self.encode_node([bytes.fromhex("3" + self.keyEnd), bytes(self.value, 'utf-8')])  # 奇數
        return self.hash

    def UpdateValue(self, address, value):
        if address == self.keyEnd:
            self.value = value
            self.HashNode()
            return True
        else:
            return False

    def checkExist(self, address):
        if self.keyEnd == address:
            return True
        else:
            return False

    def UpdateKeyEnd(self, k):
        self.keyEnd = k
        self.HashNode()

    def gethash(self):
        return self.hash


class ExtensionNode(node):

    def __init__(self, shared):
        self.prefix = ""
        self.sharedNibble = ""
        self.hash = ""
        # 首先设定 sharedNibble & prefix，作为初始化
        self.ChangeShared(shared)
        self.nextNode = BranchNode()

    def printNode(self, Level):
        space = "    " * Level
        print(space, "ExtensionNode : ")
        if self.prefix == 0:
            print(space, ["00" + self.sharedNibble])

        elif self.prefix == 1:
            print(space, ["1" + self.sharedNibble])
        self.nextNode.printNode(Level + 1)

    def Addnode(self, k, v):
        # 如果输入的地址和sharedNibble 一致 => 添加node 在 branchNode下
        if self.longest(self.sharedNibble, k) == self.sharedNibble:
            self.nextNode.Addnode(self.rest(self.sharedNibble, k), v)
        # 如果输入的地址和sharedNibble 不一致 => 扩展节点重置（清空）同时调用之前node值恢复
        else:
            # 重置Extension Node
            currentNode = self
            # newExtensionNode作为保留current node的功能
            # (sharedNibble会再进行更新)
            newExtensionNode = ExtensionNode(self.sharedNibble)
            newExtensionNode.nextNode = currentNode.nextNode
            #当前节点就会更新成新的sharednibble, 以及接上新的分支
            self.ChangeShared(self.longest(self.sharedNibble, k))
            self.nextNode = BranchNode()
            # newExtensionNode置换为sharednibble，即换成current node sharedNibble 剩下的部分
            # ex. old cur.share = "34679", new cur.share = "12679" => newExtensionNode.share = "679"
            newExtensionNode.ChangeShared(self.rest(self.sharedNibble, newExtensionNode.sharedNibble))
            # 但"679"并不是真正的sharednibble, 因为6会是放在branch node的index（索引）
            indexFornewExtensionNode = int(newExtensionNode.sharedNibble[0], 16)
            # sharedNibble去除index "6" => "79"
            newExtensionNode.ChangeShared(newExtensionNode.sharedNibble[1:len(newExtensionNode.sharedNibble)])
            # branch node下面接上extension node
            self.nextNode.HexArray[indexFornewExtensionNode] = newExtensionNode
            # node都接上了再接要加入的新node
            self.nextNode.Addnode(self.rest(self.sharedNibble, k), v)

        self.HashNode()
        return self.hash

    def HashNode(self):
        if self.prefix == 0:
            self.hash = self.encode_node([bytes.fromhex("00" + self.sharedNibble), self.nextNode.HashNode()])

        elif self.prefix == 1:
            self.hash = self.encode_node([bytes.fromhex("1" + self.sharedNibble), self.nextNode.HashNode()])
        return self.hash

    def UpdateValue(self, address, value):
        if len(self.longest(self.sharedNibble, address)) >= 0:
            return self.nextNode.UpdateValue(self.rest(self.sharedNibble, address), value)

        else:
            return False

    def checkExist(self, address):
        if self.longest(self.sharedNibble, address) == self.sharedNibble:
            return self.nextNode.checkExist(self.rest(self.sharedNibble, address))
        else:
            return False

    def ChangeShared(self, shared):
        self.sharedNibble = shared
        if len(self.sharedNibble) % 2 == 0:
            # 以奇数结尾的key标记的叶子节点！
            self.prefix = 0

        else:
            # 以偶数结尾的key标记的叶子节点！
            self.prefix = 1

class BranchNode(node):

    def __init__(self):
        self.HexArray = [""] * 16
        self.value = ""
        self.hash = ""

    def printNode(self, Level):
        space = "    " * Level
        print(space, "BranchNode : ")

        for index in range(16):
            if self.HexArray[index] != "":
                print(space, index)
                self.HexArray[index].printNode(Level + 1)
        print(space, self.value)

    def Addnode(self, k, v):
        # 若 k = ""，表示是到 extension node address就沒了
        # 该extension node value可以记录在 branch node 下
        if k == "":
            self.value = v
            return
        index = int(k[0], 16)
        # 延迟import 防止circular import死循环或者溢出
        from ExtensionNodeClass import ExtensionNode
        if self.HexArray[index] != "":
            # 如果目前处于leaf的状态
            if self.HexArray[index].__class__ == LeafNode:
                # 先把目前leaf存下來
                Leaf = self.HexArray[index]
                # 找出目前leaf和新增node之间最长的substring
                subaddress = self.longest(Leaf.keyEnd, k[1:len(k)])
                # 创建扩展节点
                tempExtension = ExtensionNode(subaddress[0:len(subaddress)])
                # 扩展节点下的Branch Node加入新增node
                tempExtension.Addnode(k[1:len(k)], v)
                # 扩展节点下的Branch Node加入已存在的leaf
                # 注意此处不用做substring
                tempExtension.Addnode(Leaf.keyEnd[0:len(Leaf.keyEnd)], Leaf.value)
                # HexArray临时数组其中存储的节点从leaf节点变成了我们刚创建的扩展节点
                self.HexArray[index] = tempExtension
            # 若目前是扩展节点
            elif self.HexArray[index].__class__ == ExtensionNode:
                self.HexArray[index].Addnode(k[1:len(k)], v)


        else:
            self.HexArray[index] = LeafNode(k[1:len(k)], v)

        # 这里不确定要不要hash，决定最终再一起哈希吧
        self.HashNode()
        return self.hash

    def HashNode(self):
        arr = [b""] * 17
        for index in range(16):
            if self.HexArray[index] != "":
                arr[index] = self.HexArray[index].HashNode()

        if self.value != "":
            arr[16] = bytes(self.value, 'utf-8')

        self.hash = self.encode_node(arr)
        return self.hash

    def UpdateValue(self, address, value):
        index = int(address[0], 16)
        if self.HexArray[index] != "":
            return self.HexArray[index].UpdateValue(address[1:len(address)], value)
        else:
            return False

    def checkExist(self, address):
        index = int(address[0], 16)
        if self.HexArray[index] != "":
            return self.HexArray[index].checkExist(address[1:len(address)])
        else:
            return False
