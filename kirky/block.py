

class Edge(object):

    def __init__(self, tail, head, id):
        self.head = tuple(head)
        self.tail = tuple(tail)
        self.weight = None
        self.id = id

    def __hash__(self):
        return tuple(self.tail + self.head)


class Vertex(object):

    def __init__(self, position, num_vectors):
        self.position = tuple(position)
        # first positition in each inner list is head poking in, second position is tail leading off
        self.cut = [[None, None] for i in range(num_vectors)]

    def add_edge(self, edge, id, tail):
        if tail:
            self.cut[id][1] = edge
        else:
            self.cut[id][0] = edge


class Block(object):

    def __init__(self, dimensions, num_vectors):
        self.num_vectors = num_vectors
        self.dimensions = dimensions
        self.shape = (0 for i in range(dimensions))
        self.interior = set()
        self.frame = set()
        self.vertices = {}

    def seed_frame(self, shape):
        # this just creates a rectangular lattice of unit size one tha fills a space
        # of sizes given by the elements of shape
        # we start by creating a single unit - a side length 1 hypercube
        for i in range(self.dimensions):
            tail = [0 for j in range(self.dimensions)]
            head = [0 for j in range(self.dimensions)]
            head[i] = 1
            edge = Edge(tail, head, i)
            self.update_vertices(edge)
            self.frame.add(edge)
        # now that we have our hyper cube we copy_and_add we will extend it to meet the size needs
        for i in range(self.dimensions):
            for j in range(shape[i]):
                self.copy_and_add(self.frame, i, 1)

    def populate_interior(self, edge, id):
        # this takes in an example edge, and fills the interior with every such edge that could
        # possibly fit inside the frame (should be called right after seed_frame
        edge_dif = [edge.head[i] - edge.tail[i] for i in range(self.dimensions)]
        # this works be running through the vertices and seeing which vertices could have one of these
        # edges poking out of them
        for position in self.vertices:
            needed_position = [position[i] + edge_dif[i] for i in range(self.dimensions)]
            if needed_position in self.vertices:
                # okay cool we can add in the edge!
                new_edge = Edge(position, needed_position, id)
                self.interior.add(new_edge)
                tail_vertex = self.vertices[position]
                head_vertex = self.vertices[needed_position]
                tail_vertex.add_edge(new_edge, id, tail=True)
                head_vertex.add_edge(new_edge, id, tail=False)

    def copy_and_add(self, edges, dimension, distance):
        new_edges = []
        for edge in edges:
            # first we grab the edge head and tail as lists so we can modify it
            tail, head = [e for e in edge.tail], [e for e in edge.tail]
            # next we move the edge in the specified dimension by the specified distance
            # by altering its head and tail values
            # modify tail:
            tail[dimension] += distance
            # modify head:
            head[dimension] += distance
            # now we create the edge
            new_edge = Edge(tail, head, edge.id)
            # now we look to see if the edge is already in our edges
            # and if it isn't we take it down as an edge to add
            if new_edge in edges: continue
            # okay so we have a new edge that we are going to keep
            # first we add it to the new_edges list
            new_edges.add(new_edge)
            # then we need to update vertices and create new ones if needed
            self.update_vertices(new_edge)
        # finally we update edges by the new_edges
        edges.update(new_edges)

    def update_vertices(self, new_edge):
        # this function lets us update or add vertices as needed for a new edge
        # edge must not be a duplicate!!!
        # we start with the tail
        if new_edge.tail in self.vertices:
            vertex = self.vertices[new_edge.tail]
            vertex.add_edge(new_edge, new_edge.id, tail=True)
        else:
            new_vertex = Vertex(new_edge.tail, self.num_vectors)
            new_vertex.add_edge(new_edge, new_edge.id, tail=True)
            # and now we want to add our new vertex to the vertex pool
            self.vertices[new_vertex.position] = new_vertex
        # we then do the head
        if new_edge.head in self.vertices:
            vertex = self.vertices[new_edge.head]
            vertex.add_edge(new_edge, new_edge.id, tail=False)
        else:
            new_vertex = Vertex(new_edge.head, self.num_vectors)
            new_vertex.add_edge(new_edge, new_edge.id, tail=False)
            # and now we want to add our new vertex to the vertex pool
            self.vertices[new_vertex.position] = new_vertex

    def double(self, dimension):
        # here we have to grow first the frame and then the interior
        # we do so by copy_and_adding the frame by the shape size along the input dimension
        # Then we grow the interior by copy_and_adding it one step at a time up to the shape size
        # aforementioned. Then we set the shape size along the input dimension to its new
        # value and we are done

        # first we tackle the frame
        self.copy_and_add(self.frame, dimension, self.shape[dimension])
        # then we tackle the interior
        for i in range(self.shape[dimension]):
            self.copy_and_add(self.frame, dimension, 1)
        # and then we update the new shape
        self.shape[dimension] += self.shape[dimension]


