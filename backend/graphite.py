import pickle

#helpers 
def indent(s,num_spaces = 4):
    spaces = " " * num_spaces
    return "\n".join(map(lambda line: spaces + line, s.split("\n")))
class NameGenerator:
    def __init__(self,variable_name):
        self.id = 0
        self.variable_name = variable_name
    def next(self):
        self.id += 1
        return self.id
variable_name_generator = {}
def variable_name(var_type):
    if var_type not in variable_name_generator:
        variable_name_generator[var_type] = NameGenerator(var_type)
    return variable_name_generator[var_type].next()

class Graph:
    def new():
        return Graph([],[])
    def __init__(self,nodes,edges):
        self.id = variable_name('graph')
        self.nodes = []
        self.edges = set()
        self.parent_node = None
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)
    def add_node(self,node):
        self.nodes.append(node)
        node.parent_graph = self
        self.refresh_node_completion()
    def get_node(self, id,name=None):
        if name is not None:
            for node in self.nodes:
                if node.name == name:
                    return node
                if node.has_structure():
                    deep_get = node.structure.get_node(id, name=name)
                    if deep_get is not None:
                        return deep_get
        for node in self.nodes:
            if node.id == id:
                return node
            if node.has_structure():
                deep_get = node.structure.get_node(id)
                if deep_get is not None:
                    return deep_get
        return None
    def refresh_node_completion(self):
        for node in self.nodes:
            node.refresh_completion()
    def delete_node(self,node):
        node.parent_graph = None
        self.nodes.remove(node)
    def add_edge(self, edge, allow_external_nodes=False):
        #TODO: reject unless start and end are both in self.nodes (by default)
        if not allow_external_nodes and (edge.start.parent_graph != self or edge.end.parent_graph != self):
            print(f"hey, you can't connect {edge.start.name} and {edge.end.name} because they are not both part of graph {self.id}")
            return
        #TODO: reject if edge creates cycle (by default)
        self.edges.add(edge)
        self.refresh_node_completion()
    def remove_edge(self, edge):
        self.edges.remove(edge)
    def get_incoming_nodes(self, node):
        return set(map(lambda edge: edge.start,self.get_incoming_edges(node)))
    def get_incoming_edges(self, node):
        result = set(filter(lambda edge: edge.end == node,self.edges))
        #TODO: nodes should be dependent on their containing nodes' dependencies
        #TODO: parent nodes should be dependent on children nodes
        return result
    def get_outgoing_nodes(self, node):
        return set(map(lambda edge: edge.end,self.get_outgoing_edges(node)))
    def get_outgoing_edges(self, node):
        return set(filter(lambda edge: edge.start.id == node.id,self.edges))
    def get_workable_nodes(self):
        #TODO: make it not O(n^2)
        return list(filter(lambda node: (not node.completed) and node.is_workable(), self.nodes))
    def get_num_completed(self):
        return len(list(filter(lambda n: n.completed,self.nodes)))
    def get_progress(self):
        return f"{self.get_num_completed()} / {len(self.nodes)}"
    def describe(self, show_structure=True, show_edges = False):
        desc_items = []
        if len(self.nodes) > 0:
            desc_items.append("\n".join(map(lambda n: n.describe(show_structure, show_edges),self.nodes)))
        if len(self.edges) > 0 and show_edges:
            desc_items.append("\n".join(map(lambda e: e.describe(),self.edges)))
        return "\n".join(desc_items)
    def is_completed(self):
        return all([node.completed for node in self.nodes])

class Node:
    def __init__(self,name:str,desc:str="",structure:Graph = Graph.new()):
        self.id = variable_name('node')
        self.template_id = variable_name('node template')
        self.name = name
        self.desc = desc
        self.completed = False
        self.parent_graph = None
        self.start = None
        self.end = None
        self.structure = None
        if len(structure.nodes) > 0:
            self.add_structure(structure)
    def check_invariants(self):
        if not self.has_structure():
            return
        # print(f"checking invariants for {self.name}")
        #if graph has structure, enforce the following invariants:
        assert(self.start.completed == self.is_workable())
        assert(self.end.completed == self.end.is_workable())
        assert(self.completed == (self.is_workable() and self.end.completed))
    def refresh_completion(self):
        if not self.has_structure():
            return
        self.start.set_completed(self.is_workable())
        self.end.set_completed(self.end.is_workable())
        self.set_completed(self.end.completed and self.is_workable())
        self.check_invariants()
    def init_endpoints(self):
        self.start = Node(f"{self.name} start", f"node indicating that {self.name} has been started")
        self.end = Node(f"{self.name} end", f"node indicating that {self.name} has been completed")
        self.start.parent_graph = self.structure
        self.end.parent_graph = self.structure
    def add_structure(self,structure: Graph = Graph.new()):
        self.structure = Graph.new()
        self.structure.parent_node = self
        self.init_endpoints()
        self.encapsulate_nodes(structure.nodes)
        self.refresh_completion()
    def is_workable(self):
        if self.parent_graph is None:
            return False #shouldn't happen
        return all([node.completed for node in self.parent_graph.get_incoming_nodes(self)])
    def has_structure(self):
        return self.structure is not None and len(self.structure.nodes) > 0
    def has_parent_graph(self):
        return self.parent_graph is not None 
    def has_parent_node(self):
        return self.parent_graph is not None and self.parent_graph.parent_node is not None
    def edges(self):
        if self.parent_graph == None:
            return []
        return self.parent_graph.get_incoming_edges(self).union(self.parent_graph.get_outgoing_edges(self))
    def move_nodes_up(nodes):
        nodes = list(filter(lambda node: node.has_parent_node(), nodes)) #nodes at top level cannot be moved
        for node in nodes:
            print(f"removing {node.name}'s structure edges")
            parent_node = node.parent_graph.parent_node
            edges = node.edges()
            #break edges between node and structure start/end nodes
            for edge in edges:
                if edge.start == parent_node.start or edge.end == parent_node.end:
                    print(f"removing edge {edge.describe()}")
                    node.parent_graph.remove_edge(edge)
                else:
                    print(f"leaving edge {edge.describe()}")
        for node in nodes:
            print(f"moving {node.name} up")
            parent_node = node.parent_graph.parent_node
            edges = node.edges()
            has_endpoint_outside_set = lambda edge: (edge.start not in nodes) or (edge.end not in nodes)
            incoming_edges = list(filter(has_endpoint_outside_set,node.parent_graph.get_incoming_edges(node)))
            outgoing_edges = list(filter(has_endpoint_outside_set,node.parent_graph.get_outgoing_edges(node)))
            has_incoming_edges = len(incoming_edges) > 0
            has_outgoing_edges = len(outgoing_edges) > 0
            #if node has incoming and outgoing edges that remain in parent,
            #break both (for now)
            #TODO: prompt user to choose which way dependency should go
            for edge in edges:
                node.parent_graph.remove_edge(edge)
                if edge.start not in nodes and not has_outgoing_edges:
                    #remap edge through parent
                    print("doing this")
                    node.parent_graph.add_edge(Edge(edge.start, parent_node.end),allow_external_nodes=True)
                    parent_node.parent_graph.add_edge(Edge(parent_node,node),allow_external_nodes=True)
                    continue
                if edge.end not in nodes and not has_incoming_edges:
                    #remap edge through parent
                    print("doing that")
                    node.parent_graph.add_edge(Edge(parent_node.start, edge.end),allow_external_nodes=True)
                    parent_node.parent_graph.add_edge(Edge(node,parent_node),allow_external_nodes=True)
                    continue
                if has_incoming_edges and has_outgoing_edges:
                    continue
                print(f"adding edge {edge.describe()} to parent graph")
                parent_node.parent_graph.add_edge(edge, allow_external_nodes=True)
            node.parent_graph.delete_node(node)
            parent_node.parent_graph.add_node(node)
    def encapsulate_nodes(self, nodes):
        assert(self not in nodes) #can't move into yourself
        if self.structure is None:
            self.add_structure()
        for node in nodes:
            edges = node.edges()
            self.structure.add_edge(Edge(self.start, node),allow_external_nodes=True)
            self.structure.add_edge(Edge(node, self.end),allow_external_nodes=True)
            for edge in edges:
                if edge.start not in nodes:
                    #remap edge through self
                    node.parent_graph.add_edge(Edge(edge.start, self))
                if edge.end not in nodes:
                    #remap edge through self
                    node.parent_graph.add_edge(Edge(self, edge.end))
                node.parent_graph.remove_edge(edge)
                self.structure.add_edge(edge, allow_external_nodes=True)
        for node in nodes:
            if node.has_parent_graph():
                node.parent_graph.delete_node(node)
            self.structure.add_node(node)
        if not self.is_workable():
            self.start.set_completed(False, apply_to_children=True)
    def set_completed(self,completed:bool,apply_to_children=False):
        if not self.completed and completed:
            self.completed = True
            if not self.is_workable():
                print(f"hey, you can't set {self.name} to completed because not all its dependencies are satisfied")
                dependencies = self.parent_graph.get_incoming_nodes(self)
                unsat_deps = filter(lambda n: not n.completed, dependencies)
                print(f"unsatisfied dependencies: {list(map(lambda n: n.name, unsat_deps))}")
                return
            #TODO: warn if things this task depends on are not complete
            #TODO: set things this task depends on to complete
            has_parent_node = self.has_parent_node()
            if has_parent_node and self == self.parent_graph.parent_node.end and self.parent_graph.parent_node.is_workable():
                self.parent_graph.parent_node.set_completed(True)
            for node in self.parent_graph.get_outgoing_nodes(self):
                if node.is_workable():
                    self.refresh_completion()
                    if has_parent_node and node == self.parent_graph.parent_node.end:
                        node.set_completed(True)
                    if node.has_structure():
                        node.refresh_completion()
        if self.completed and not completed:
            self.completed = False
            if self.has_structure():
                if apply_to_children:
                    for node in self.structure.nodes:
                        node.set_completed(False,apply_to_children=True)
                self.refresh_completion() #enforces invariants
            if self.has_parent_graph():
                for node in self.parent_graph.get_outgoing_nodes(self):
                    node.set_completed(False)
            if self.has_parent_node() and self == self.parent_graph.parent_node.end:
                self.parent_graph.parent_node.set_completed(False)
    def describe(self, show_structure = True, show_edges=False):
        checkbox = "☑" if self.completed else " "
        status = "☐" if self.is_workable() and not self.completed else checkbox
        has_structure = self.has_structure()
        desc = f"{status} {self.name}"
        if has_structure and self.is_workable() and not self.completed:
            progress = f' ({self.structure.get_progress()})'
            desc += progress
        if self.desc != "":
            desc += f" - {self.desc}"
        if show_structure and has_structure:
            desc += '\n' + indent(self.structure.describe(show_structure, show_edges))
        return desc

class Edge:
    def __init__(self, start:Node, end:Node):
        self.start = start
        self.end = end
    def describe(self):
        return f"{self.start.name} -> {self.end.name}"
    
class Examples:
    def widgets():
        design_pr = Node("Design Pull Request","merge the pull request")
        design_qa = Node("Design QA","check to make sure the widget design is good")
        design_deploy = Node("Design Deploy","publish the final widget design")
        design = Node("Design","design process for the widgets")
        # TODO why doesn't this method work?
        # design = Node("Design","design process for the widgets", structure=Graph([design_pr,design_qa,design_deploy],[Edge(design_pr,design_qa),Edge(design_qa,design_deploy)]))
        design_steps = Graph([design,design_pr,design_qa,design_deploy],[Edge(design_pr,design_qa),Edge(design_qa,design_deploy)])
        design.encapsulate_nodes([design_pr,design_qa,design_deploy])
        produce_pr = Node("Produce Pull Request","merge the pull request")
        produce_qa = Node("Produce QA","check to make sure widgets are being produced")
        produce_deploy = Node("Produce Deploy","finish widget production")
        produce = Node("Produce","manufacturing the widgets")
        produce_steps = Graph([produce,produce_pr,produce_qa,produce_deploy],[Edge(produce_pr,produce_qa),Edge(produce_qa,produce_deploy)])
        produce.encapsulate_nodes([produce_pr,produce_qa,produce_deploy])
        get_groceries = Node("Get Groceries","eggs, milk, other widget materials")
        widgets = Node("Widgets","create 10,000 widgets")
        prep = Node("prep work")
        g = Graph([prep,widgets,design,produce,get_groceries],[Edge(design,produce),Edge(get_groceries, produce)])
        wash_dishes = Node("Wash Dishes", "wash some dishes (forgot this step originally)")
        g.add_node(wash_dishes)
        print(g.describe())
        input('press enter to encapsulate widget steps inside Widgets node')
        widgets.encapsulate_nodes([design, produce, get_groceries, wash_dishes])
        print(g.describe())
        input('press enter to add dependency prep work -> Widgets')
        g.add_edge(Edge(prep, widgets))
        completion_order = [prep,design_pr,get_groceries,design_qa,design_deploy,produce_pr,produce_qa,produce_deploy,wash_dishes]
        for node in completion_order:
            print(g.describe())
            input(f'press enter to complete {node.name}')
            node.set_completed(True)
            node.check_invariants()
            if g.is_completed():
                print(g.describe())
                print("you finished the project! yay!")
                break
        input("oh no, we actually didn't design the widgets right, that step will have to be redone")
        design.set_completed(False, apply_to_children=True)
        return g
    def abcd():
        g = Graph.new()
        a = Node("A")
        b = Node("B")
        c = Node("C")
        d = Node("D")
        d.encapsulate_nodes([a,b,c])
        d.structure.add_edge(Edge(a,b))
        d.structure.add_edge(Edge(b,c))
        g.add_node(d)
        Node.move_nodes_up([a,c])
        a.set_completed(True)
        return g

print(Examples.abcd().describe())