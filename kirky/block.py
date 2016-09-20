from fractions import Fraction


class Edge(object):

    def __init__(self, tail, head, id, pin=-1):
        self.head = tuple(head)
        self.tail = tuple(tail)
        self.weight = None
        self.id = id
        self.pin = pin

    def __eq__(self, other):
        if self.head == self.head and self.tail == other.tail:
            return True
        return False

    def __hash__(self):
        return hash(tuple(self.tail + self.head))


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

    def __init__(self, dimensions, num_vectors, steps):
        self.num_vectors = num_vectors
        self.dimensions = dimensions
        self.steps = steps
        self.shape = (0 for i in range(dimensions))
        self.interior = set()
        self.frame = set()
        self.vertices = {}
        self.current_pin = 0

    def welcome_edge(self, edge):
        edge.pin = self.current_pin
        self.update_vertices(edge)
        self.current_pin += 1

    def fill_vertex_frame(self):
        # for each kind of of independent vector
        for dimension in range(self.dimensions):
            base_vector = [Fraction(0) for i in range(self.dimensions)]
            base_vector[dimension] = Fraction(1)
            # run through all of the vertices
            for position in self.vertices:
                # find the position of the appropriate head vertex
                head_position = tuple([position[i] + base_vector[i] for i in range(self.dimensions)])
                # see if the vertex exists
                if head_position in self.vertices:
                    # create the edge
                    edge = Edge(position, head_position, dimension)
                    # check to see if the edge already exists
                    if edge not in self.frame:
                        self.welcome_edge(edge)
                        self.frame.add(edge)

    def create_vertex_frame(self):
        # we first create the vertex at the origin
        origin = tuple([Fraction(0) for i in range(self.dimensions)])
        vertex = Vertex(origin, self.num_vectors)
        # we then seed our vertices with this vertex
        self.vertices[origin] = vertex
        # now for each dimension we get step[dimension] copies of each vertex 1/step[dimension] apart
        # from the old vertices in the direction of the dimension
        for dimension in range(self.dimensions):
            old_positions = [position for position in self.vertices]
            new_positions = []
            steps = self.steps[dimension]
            distance = Fraction(1, steps)
            for position in old_positions:
                for i in range(steps):
                    # create the new position
                    new_position = [e for e in position]
                    new_position[dimension] += (i + 1) * distance
                    # add the new position
                    new_positions.append(tuple(new_position))
            # now create vertex's using the new positions and add them to self.vertices
            for position in new_positions:
                vertex = Vertex(position, self.num_vectors)
                self.vertices[position] = vertex

    def create_hyper_cube(self):
        # first we create the frame of vertices
        self.create_vertex_frame()
        # then we fill that vertex frame
        self.fill_vertex_frame()

    def seed_frame(self, shape):
        # this just creates a rectangular lattice of unit size one tha fills a space
        # of sizes given by the elements of shape
        # we start by creating a single unit - a side length 1 hypercube
        self.create_hyper_cube()
        # now that we have our hyper cube we copy_and_add we will extend it to meet the size needs
        for i in range(self.dimensions):
            for j in range(int((shape[i] - 1) * self.steps[i])):
                self.copy_and_add(self.frame, i, Fraction(1, self.steps[i]))
        self.shape = shape

    def populate_interior(self, edge):
        # this takes in an example edge, and fills the interior with every such edge that could
        # possibly fit inside the frame (should be called right after seed_frame
        edge_dif = [edge.head[i] - edge.tail[i] for i in range(self.dimensions)]
        # this works be running through the vertices and seeing which vertices could have one of these
        # edges poking out of them
        for position in self.vertices:
            needed_position = tuple([position[i] + edge_dif[i] for i in range(self.dimensions)])
            if needed_position in self.vertices:
                # okay cool we can add in the edge!
                new_edge = Edge(position, needed_position, edge.id)
                self.welcome_edge(new_edge)
                self.interior.add(new_edge)

    def copy_and_add(self, edges, dimension, distance):
        new_edges = []
        for edge in edges:
            # first we grab the edge head and tail as lists so we can modify it
            tail, head = [e for e in edge.tail], [e for e in edge.head]
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
            if new_edge in edges:
                continue
            # okay so we have a new edge that we are going to keep
            # first we add it to the new_edges list
            new_edges.append(new_edge)
            # then we need to update vertices and create new ones if needed
            self.welcome_edge(new_edge)
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

        for i in range(int(self.shape[dimension] * self.steps[dimension])):
            self.copy_and_add(self.interior, dimension, Fraction(1, self.steps[dimension]))
            self.copy_and_add(self.frame, dimension, Fraction(1, self.steps[dimension]))
        # and then we update the new shape
        self.shape[dimension] += self.shape[dimension]


