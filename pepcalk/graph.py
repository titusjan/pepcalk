import logging
from pepcalk.utils import check_class

class CircularDependencyError(ValueError):
    """ Raised if the graph contains a circular dependency """
    def __init__(self, msg, node_id):
        " Constructor "
        super(CircularDependencyError, self).__init__(msg)
        self.node_id = node_id
        

logger = logging.getLogger(__name__)

class Node(object):
    """ Node 
    """
    
    def __init__(self, ident, edges = None):
        """ 
        """
        self._id = ident
        self._edges = edges if edges is not None else set([])

    @property
    def id(self):
        "Returns the id of the node"
        return self._id
    
    @property
    def edges(self):
        "Returns the list of edges"
        return self._edges
    
    def __str__(self):
        return "<Node: {} ({:d} edges)>".format(self.id, len(self._edges))
        
    def __repr__(self):
        return "<Node: {}>".format(self.id, len(self._edges))
        
        
    def connect(self, other):
        """ Connects self to other
        """
        check_class(other, Node)
        self._edges.add(other)
        
        
       
                
class Graph(object):
    """ A directed graph.
    
        Contains an id->Node dictionary.
    """
    def __init__(self, nodes = None):
        """ Constructor
        """
        self._nodes = dict()
        if nodes is not None:
            for node in nodes:
                self.add(node)
                
    def __str__(self):
        return "<Graph ({:d} nodes)>".format(len(self._nodes))

    
    @property
    def nodes(self):
        """ Returns the dictionary (id->Node} of nodes in the graph. 
        """
        return self._nodes
    
    
    def contains(self, node_id):
        """ Returns True if the graph contains a node with this id.
        """
        return node_id in self._nodes


    def get(self, ident):
        """ Returns the node having the identiefer named ident
        """
        return self.nodes[ident]

    
    # TODO: implement remove? This is expensive because all edges that contain
    # the node must be removed.
    def add(self, node):
        """ Adds a Node to the graph. 
        """
        check_class(node, Node)
        if node.id in self._nodes:
            raise KeyError("Node with id {!r} already exists in graph.")
        
        self._nodes[node.id] = node
        return node

    
    def connect(self, source_id, target_id):
        """ Makes a connection from the source node to the target node
        """
        source = self._nodes[source_id]
        target = self._nodes[target_id]
        source.connect(target)
        
       
    def linearize(self):
        """ Executes a topological sort of the graph using a depth first search (as described by Corman)
        
            Returns a list where for all combination of nodes A & B the following invariant holds:
                if A has a vertex to B, B will occur in the list before A
                
            For more info see: 
                http://en.wikipedia.org/w/index.php?title=Topological_sorting&oldid=559164289
        """
        result = []
        unmarked_nodes = set(self._nodes.itervalues())
        temp_marked_nodes = set()
        perm_marked_nodes = set()

        def visit(node):
            """ Visits nodes recursively and adds them to the result.
                Marks nodes to prevent duplicates.
            """
            if node in temp_marked_nodes:
                raise CircularDependencyError("Circular dependency for: {}".format(node.id), 
                                              node.id)
            
            if node not in perm_marked_nodes: 
                
                # Node is unmarked (so has not been visited yet)
                unmarked_nodes.remove(node)
                temp_marked_nodes.add(node)
                for dep_node in node.edges:
                    visit(dep_node)
                    
                temp_marked_nodes.remove(node)
                perm_marked_nodes.add(node)
                result.append(node) 
            # end of visit() function
            
        while len(unmarked_nodes) > 0:
            # Select a random node without removing it
            node = unmarked_nodes.pop()
            unmarked_nodes.add(node)
            visit(node)
            
        return result
    
    
        