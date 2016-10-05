import copy

class Tree():

    def __init__(self):
        self.tree = {}

    def process_path(self, path):
        path_list = str(path).split('/')[1:]
        parent = self.tree
        for item in path_list:
            if item not in parent:
                parent[item] = {}
            parent = parent[item]

    def add_node(self, node):
        parent = Node.get_ancestor_node(node)

    # def get_path(self, item):


# class Node(QStandardItem):
class Node:
    def __init__(self, parent=None, child=None, data=None):
        # super(QStandardItem, self).__init__()
        if parent is not Node and parent is not None:
            raise AttributeError("parent type not correct")
        if child is not Node and child is not None:
            raise AttributeError("child type not correct")
        if child is None:
            self.child = []
        else:
            self.child.append(child)
        if parent is None:
            self.level = 0
        else:
            self.level = self.parent.level + 1
        self.data = data
        # self.data = QStandardItem(data)
        self.parent = parent


    def add_parent(self, parent):

        self.parent = parent
        parent.child.append(self)
        parent.level = copy.copy(self.level)
        self.level = self.level + 1

    def add_child(self, child):
        self.child = child
        child.parent = self
        child.level = self.level + 1

    @classmethod
    def get_ancestor(cls, node):
        print node.data
        if node.parent is None:
            return node
        else:
            return cls.get_ancestor(node.parent)

    # def get_path(self, item):


if __name__ == "__main__":
    t = Tree()
    t.process_path("/folder/dscn0026.jpg")
    t.process_path("/folder/123.jpg")
    t.process_path("/123.jpg")

    # a = []
    # n = Node(data="0")
    # n1 = Node(data="1")
    # n2 = Node(data="2")
    # n3 = Node(data="3")
    # n4 = Node(data="4")
    # n5 = Node(data="5")
    # n6 = Node(data="6")
    # n7 = Node(data="7")
    #
    # n1.add_parent(n)
    # # n.add_child(n2)
    # n3.add_parent(n)
    # n4.add_parent(n2)
    # n6.add_parent(n2)
    # n5.add_parent(n4)
    # n7.add_parent(n3)
    #
    # print n1.data, Node.get_ancestor(n1).data, n1.level
    # print n2.data, Node.get_ancestor(n2).data, n2.level
    # print n4.data, Node.get_ancestor(n4).data, n4.level
    # print n5.data, Node.get_ancestor(n5).data, n5.level
    # print n6.data, Node.get_ancestor(n6).data, n6.level
    # print n3.data, Node.get_ancestor(n3).data, n3.level
    # print n7.data, Node.get_ancestor(n7).data, n7.level
