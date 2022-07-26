# MPT-report

# 实现初期
# 字典树
是一种树形结构，是一种哈希树的变种。典型应用是用于统计，排序和保存大量的字符串（但不仅限于字符串），所以经常被搜索引擎系统用于文本词频统计。它的优点是：利用字符串的公共前缀来减少查询时间，最大限度地减少无谓的字符串比较，查询效率比哈希树高。

![image](https://user-images.githubusercontent.com/75195549/181054317-e6b56936-666f-4799-9834-ab7e7eb6152b.png)


# Merkle 树


Merkle Tree是一种数据结构，用来验证计算机之间存储和传输数据的一致性，

首先如果使用朴素的方法进行一致性的验证需要消耗大量的存储和网络资源，如比对计算机之间的所有数据；

使用Merkle Tree，只需要比对merkle root（根节点）就可以达到相同的效果。整个过程，简单的描述如下：

将数据通过哈希之后放置在叶子节点之中；

将相邻两个数据的哈希值组合在一起，得出一个新的哈希值；

依次类推，直到只有一个节点也就是根节点；

在验证另外的计算机拥有和本机相同的数据时，只需验证其提供的根节点和自己的根节点一致即可。

换句话说这棵树的hash值作为节点，是自下而上构建的。

Merke Tree使用了加密哈希算法来快速验证数据一致性，常用的加密哈希算法有SHA-256，SHA-3，Blake2等，

该加密算法可以保持对任意的输入数据可以进行高效计算，对于相同的输入有相同的输出的同时兼具了单向性（从哈希值无法推断出原信息）抗碰撞性。

对于整棵树的输入即使只有很小的改变，输出的树节点也会有极大不同。

Merkel tree示例如图所示：




![image](https://user-images.githubusercontent.com/75195549/181054743-877eb96e-a5f6-475e-bf12-e318cf02b98b.png)



Merkle Patricia Trie（下面简称MPT），在Trie的基础上，给每个节点计算了一个哈希值，在Substrate（一种规格的树结构，每个节点最多有16个子节点：）中，该值通过对节点内容进行加密hash算法如Blake2运算取得，用来索引数据库和计算merkle root。也就是说，MPT用到了两种key的类型。
# key 类型
一种是Trie路径所对应的key，由runtime模块的存储单元决定。使用Substrate开发的应用链，它所拥有的各个模块的存储单元会通过交易进行修改，成为链上状态（简称为state）。每个存储单元的状态都是通过键值对以trie节点的形式进行索引或者保存的，这里键值对的value是原始数据（如数值、布尔）的SCALE编码结果，并作为MPT节点内容的一部分进行保存；key是模块、存储单元等的哈希组合，且和存储数据类型紧密相关，如：

单值类型（即Storage Value），它的key是Twox128(module_prefix) ++ Twox128(storage_prefix)；

简单映射类型（即map），可以表示一系列的键值数据，它的存储位置和map中的键相关，即Twox128(module_prefix) + Twox128(storage_prefix) + hasher(encode(map_key))；

链接映射类型（即linked_map），和map类似，key是Twox128(module_prefix) + Twox128(storage_prefix) + hasher(encode(map_key))；它的head存储在Twox128(module) + Twox128("HeadOf" + storage_prefix)；

双键映射类型（即double_map），key是twox128(module_prefix) + twox128(storage_prefix) + hasher1(encode(map_key1)) + hasher2(encode(map_key2))。




# 节点分类
叶子节点（Leaf）、有值分支节点（BranchWithValue）和无值分支节点（BranchNoValue）；有一个特例，当trie本身为空的时候存在唯一的空节点（Empty）。


为了解决下图严重存储空间浪费的情况：


![image](https://user-images.githubusercontent.com/75195549/181057053-ed970204-3a63-45ef-b1dd-4599a6a1ee7d.png)



MPT的解决方法是：
当MPT试图插入一个节点，插入过程中发现目前没有与该节点Key拥有相同前缀的路径。此时MPT把剩余的Key存储在叶子／扩展节点的Key字段中，充当一个”Shortcut“。



# 基本结构



![image](https://user-images.githubusercontent.com/75195549/181058779-77805773-c887-4067-bbab-4d379def6cf3.png)




# 代码运行结果


