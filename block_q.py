import numpy as np

class Edge(object):
    def __init__(self, head, tail, id):
        self.head = head
        self.tail = tail
        self.pin = 0
        self.id = id # index of the edge in the column of the matrix
        self.weight = 0
        self.update_vertices()
        
    def update_vertices(self):
        if self.head is not None:
            self.head.add_edge(self)
        if self.tail is not None:
            self.tail.add_edge(self)
    def __eq__(self, other):
        if other == None:
            return self.head == None
        if self.head == self.head and self.tail == other.tail:
            return True
        return False
    def __str__(self):
        return 'None' if self.head == None else "Edge from " + str(self.tail.position) + " to " + str(self.head.position) + " with weight " + str(self.weight) + " and id " + str(self.id) + " and pin " + str(self.pin)
    def __hash__(self):
        return int(hash(self.tail) * (hash(self.head) ** 2 ))

class Vertex(object):
    def __init__(self, position, num_vectors):
        self.position = np.array(position)
        self.num_vectors = num_vectors
        self.incoming = [Edge(None, None, -1) for i in range(num_vectors)]
        self.outgoing = [Edge(None, None, -1) for i in range(num_vectors)]
        
    def add_edge(self, edge):
        if edge.head == self:
            self.incoming[edge.id] = edge
        elif edge.tail == self:
            self.outgoing[edge.id] = edge
        else:
            raise ValueError("Edge does not connect to vertex")
    def is_connected(self):
        a = [edge.weight == 0 for edge in self.incoming] + [edge.weight == 0 for edge in self.outgoing]
        return not all(a)  
    def __hash__(self):
        return hash(self.position.tobytes())
    
    def get_vertex_cut(self):
        return [self.outgoing[i].weight - self.incoming[i].weight for i in range(self.num_vectors)]

class Frame(object):
    """
    Represents a frame in a Kirchhoff graph.

    Attributes:
        dimensions (int): The number of dimensions in the frame.
        num_vectors (int): The number of vectors in the frame.
        q (int): The value of q for the frame.
        shape (list): An array representing how many vertices are along each dimension.
        vertices (dict): A dictionary of vertices with their positions as keys.
        edges (set): The set of edges in the frame.
    """

    def __init__(self, matrix, q=1, search_depth = 1):
        self.dimensions = matrix.shape[0]
        self.num_vectors = matrix.shape[1]
        self.matrix = matrix
        self.q = q
        Edge.pin = 0
        self.shape = self.get_first_shape(search_depth = search_depth)
        self.vertices = {}
        self.populate_vertices(np.zeros(self.dimensions, dtype=np.int16),  np.array(self.shape, dtype=np.int16))
        self.edges = set()
        self.populate_edges(np.zeros(self.dimensions, dtype=np.int16),  np.array(self.shape, dtype=np.int16))
        
    def get_first_shape(self, search_depth = 1):
        self.shape = []
        for row in self.matrix:
            max_element = int(max([abs(element) for element in row]))
            self.shape.append(max_element * search_depth + 1)
        return self.shape
    
    def populate_vertices(self, start, end):
        
        for position in self.iterate_vertices(start, end):
            self.vertices[tuple(position)] = Vertex(position, self.num_vectors)
    
    def iterate_vertices(self, start, end):
        start = np.array(start)
        end = np.array(end)
        for i in range(np.product(end - start)):
            position = np.zeros(self.dimensions)
            for j, dim in enumerate(end - start):
                position[j] = i % dim
                i = i // dim
            position += start
            yield position

    def populate_edges(self, start, end):
        vectors = np.transpose(self.matrix)
        for (vector_id, vector) in enumerate(vectors):
            min_position, max_position = self.get_bounds(vector, start, end)
            valid_tail_positions = self.iterate_vertices(min_position, max_position)
            for tail_position in valid_tail_positions:
                tail = self.vertices[tuple(tail_position)]
                head_position = tail_position + vector
                head = self.vertices[tuple(head_position)]
                edge = Edge(head, tail, vector_id)
                self.edges.add(edge)

    def get_bounds(self, vector, start, end):
        shape = end - start
        min_position = np.zeros(self.dimensions, dtype=np.int16)
        max_position = np.copy(shape)
        for (i, component) in enumerate(vector):
            if component < 0:
                min_position[i] = abs(component)
            elif component > 0:
                max_position[i] = shape[i] - component
        return min_position + start, max_position + start

    # a function to increase the size of the frame along 1 dimension by 1 and add the new vertices and edges
    def expand(self, dimension):
        start = np.zeros(self.dimensions, dtype=np.int16)
        start[dimension] = self.shape[dimension]
        self.shape[dimension] += 1
        self.populate_vertices(start, self.shape)
        self.populate_edges(start, self.shape)
    
    def add_new_edges(self, start):
        vectors = np.transpose(self.matrix)
        for (vector_id, vector) in enumerate(vectors):
            added_positions = self.iterate_vertices(start, self.shape)
            for head_position in added_positions:
                tail_position = head_position - vector
                if(tuple(tail_position) in self.vertices):
                    tail = self.vertices[tuple(tail_position)]
                    head = self.vertices[tuple(head_position)]
                    edge = Edge(head, tail, vector_id)
                    self.edges.add(edge)
            added_positions = self.iterate_vertices(start, self.shape)
            for tail_position in added_positions:
                head_position = tail_position + vector
                if(tuple(head_position) in self.vertices):
                    tail = self.vertices[tuple(tail_position)]
                    head = self.vertices[tuple(head_position)]
                    edge = Edge(head, tail, vector_id)
                    self.edges.add(edge)
