import copy

class Tree():

    def __init__(self):
        self.root = Node()

    def process_path(self, path):
        path_list = str(path).split('/')[1:]
        parent = self.root
        for item in path_list:
            child_list = parent.get_child_data()
            if item not in child_list:
                child = Node(data=item)
                child.add_parent(parent)
            else:
                loc = [i for (i, x) in enumerate(child_list) if x == item][0]
                child = parent.child[loc]
            parent = child
                # parent.add_child(new_child)
                # parent[item] = {}



            # parent = parent[item]

    @staticmethod
    def get_path(node):
        return node.get_full_path(node)

    def get_node(self, path):
        path_list = str(path).split('/')[1:]
        current_node = self.root
        for item in path_list:
            child_list = current_node.get_child_data()
            if item in child_list:
                loc = [i for (i, x) in enumerate(child_list) if x == item][0]
                current_node = current_node.child[loc]
            else:
                return current_node
        return current_node

    def get_dict(self):
        visited, queue = set(), [self.root]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                queue += vertex.child
        return visited


class Node:
    def __init__(self, parent=None, child=None, data=None):
        # if parent is not Node and parent is not None:
        #     raise AttributeError("parent type not correct")
        # if child is not Node and child is not None:
        #     raise AttributeError("child type not correct")
        if child is None:
            self.child = []
        else:
            self.child.append(child)
        if parent is None:
            self.level = 0
        else:
            self.level = self.parent.level + 1
        self.data = data
        self.parent = parent


    def add_parent(self, parent):
        self.parent = parent
        parent.child.append(self)
        parent.level = copy.copy(self.level)
        self.level = self.level + 1

    def add_child(self, child):
        self.child.append(child)
        child.parent = self
        child.level = self.level + 1

    def get_full_path(self, node, path=""):
        path = "/{}{}".format(node.data, path)
        if node.parent is None:
            return path
        else:
            return self.get_full_path(node.parent, path)

    def is_root(cls, node):
        return node.parent is None

    def get_child_data(self):
        list = []
        for child in self.child:
            list.append(child.data)
        return list


if __name__ == "__main__":
    t = Tree()
    # print [x.data for x in t.root.child]
    # print [x.data for x in t.root.child[0].child]

    print t.get_dict()
    # print n.child
    # for item in n.child:
    #     print item.data
    # print t.tree

    # a = []
    # n0 = Node(data="0")
    # n1 = Node(data="1")
    # #
    # n2 = Node(data="2")
    # n3 = Node(data="3")
    # n4 = Node(data="4")
    # n5 = Node(data="5")
    # n6 = Node(data="6")
    # n7 = Node(data="7")
    #
    # n1.add_parent(n0)
    # n0.add_child(n2)
    # n3.add_parent(n0)
    # n4.add_parent(n2)
    # n6.add_parent(n2)
    # n5.add_parent(n4)
    # n7.add_parent(n3)
    # print n5.get_full_path(n4)
    # print n1.data, Node.get_ancestor(n1).data, n1.level
    # print n2.data, Node.get_ancestor(n2).data, n2.level
    # print n4.data, Node.get_ancestor(n4).data, n4.level
    # print n5.data, Node.get_ancestor(n5).data, n5.level
    # print n6.data, Node.get_ancestor(n6).data, n6.level
    # print n3.data, Node.get_ancestor(n3).data, n3.level
    # print n7.data, Node.get_ancestor(n7).data, n7.level
