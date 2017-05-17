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
        self.cut = [[None, None] for i in range(num_vectors)]

    def add_edge(self, edge, id, tail):
        if tail:
            self.cut[id][1] = edge
        else:
            self.cut[id][0] = edge


class Frame(object):

    def __init__(self, dimensions, num_vectors, steps):
        self.num_vectors = num_vectors
        self.dimensions = dimensions
        self.steps = steps
        self.shape = list(0 for i in range(dimensions))
        self.cross_vectors = set()
        self.coordinate_vectors = set()
        self.vertices = {}
        self.current_pin = 0

    def update_vertices(self, edge):
        """
        Input:
            edge - an edge

        This method takes an edge (which is really just a head and tail position) and adds it
        into the frame by attaching it the vertices in the frame at the head and tail positions.
        If a vertex does not exist for either of those positions, it creates that vertex as
        well.

        IMPORTANT: DO NOT ADD THE SAME EDGE TWICE. if you add the same edge twice you will
        have a problem as vertices can only have two of each kind of edge, one leaving and one
        entering the vertex. You cannot have two of the same leaving (weighting is handled by the
        edge itself).

        NOTES:
            (a) we grab the vertex at the tail position, creating it if we need to
            (b) we add the edge as leaving the vertex
            (c) if we created a new vertex we add it to the vertices in our frame now
            (d) we do the same for the head of the edge
        """
        tail_vertex = self.vertices.get(edge.tail, None) or Vertex(edge.tail, self.num_vectors)         # (a)
        tail_vertex.add_edge(edge, edge.id, tail=True)                                                  # (b)
        if not self.vertices.get(edge.tail, None): self.vertices[edge.tail] = tail_vertex               # (c)
        head_vertex = self.vertices.get(edge.head, None) or Vertex(edge.head, self.num_vectors)         # (d)
        head_vertex.add_edge(edge, edge.id, tail=False)
        if not self.vertices.get(edge.head, None): self.vertices[edge.head] = head_vertex

    def welcome_edge(self, edge):
        """
        Input:
            edge - an edge

        This method is how we add an edge (vector) to our frame. It assigns a unique pin number
        to the edge to be added (so we can keep track of it later), updates the vertices to take
        note of this new edge, and then increments the pin in anticipation of the next edge.
        """
        edge.pin = self.current_pin
        self.update_vertices(edge)
        self.current_pin += 1

    def fill_vertex_frame_with_coordinate_vectors(self):
        """
        This method takes a the set of vertices in self.vertices and adds coordinate vectors
        as edges wherever possible amongst those vertices.

        NOTES:
            (a) with these two lines we create the coordinate vector lying along this
                dimension
            (b) we will run through each of the vertices we have so far and calculate where
                another vertex would need to be for the current coordinate vector we are
                working with to have it's base at the current vertex. If that calculated
                vertex exists we will add the coordinate vector to extend from the
                current vertex to that calculated one.
                (c) calculate the position of the needed vertex
                (d) check to see if the vertex exists
                (e) create the new edge
                (f) see if it's already in the frame, and if it isn't then add it!
        """
        for dimension in range(self.dimensions):
            coordinate_vector = [Fraction(0) for _ in range(self.dimensions)]                           # (a)
            coordinate_vector[dimension] = Fraction(1)
            for position in self.vertices:                                                              # (b)
                head_position = tuple([position[i] + coordinate_vector[i]
                                       for i in range(self.dimensions)])                                # (c)
                if head_position in self.vertices:                                                      # (d)
                    edge = Edge(position, head_position, dimension)                                     # (e)
                    if edge not in self.coordinate_vectors:                                             # (f)
                        self.welcome_edge(edge)
                        self.coordinate_vectors.add(edge)

    def create_unit_vertex_frame(self):
        """
        This method looks at the minimum distances determined per each dimension of the
        frame and creates a unit hypercube filled with all the vertices possible given
        those distances. These vertices are saved in self.vertices indexed by their
        positions.

        NOTES:
            (a) we create a vertex at the origin
            (b) we start our collection of vertices with this one
            (c) for each dimension we will take the current set of vertices and add an
                identical sets of vertices in layers 1/step[dimension] apart and stacked
                along this new dimension. We will add enough layers so that we go from 0
                in that dimension to 1 (i.e. step[dimension] layers).
                (d) distance between the layers
                (e) we go ahead and generate all the positions taken up by the new vertices.
                    We do this by taking each vertex and finding its new position in each
                    layer and adding all these positions to a new position list
                (f) then we use these positions to create new vertices and add them to our
                    self.vertices
        """
        origin = tuple([Fraction(0) for _ in range(self.dimensions)])                                   # (a)
        vertex = Vertex(origin, self.num_vectors)
        self.vertices[origin] = vertex                                                                  # (b)
        for dimension in range(self.dimensions):                                                        # (c)
            old_positions = [position for position in self.vertices]
            new_positions = []
            num_layers = self.steps[dimension]
            distance = Fraction(1, num_layers)                                                          # (d)
            for position in old_positions:                                                              # (e)
                for i in range(num_layers):
                    new_position = [e for e in position]
                    new_position[dimension] += (i + 1) * distance
                    new_positions.append(tuple(new_position))
            for position in new_positions:                                                              # (f)
                vertex = Vertex(position, self.num_vectors)
                self.vertices[position] = vertex

    def create_hyper_cube(self):
        """
        This method creates a unit frame filled completely with coordinate vectors. A unit
        frame is just a frame extended a distance of 1 along every dimension from the origin.
        """
        self.create_unit_vertex_frame()
        self.fill_vertex_frame_with_coordinate_vectors()

    def copy_and_add(self, edges, dimension, distance):
        """
        Input:
            edges - a set of edges
            dimension - the index of the dimension along which to move before creating the copy
            distance - the distance to move before pasting the copy

        This method takes a series of edges, copies them, and then pastes them the specified
        distance along the specified dimension. It updates the input list of edges with the
        edges added.

        NOTES:
            (a) we create these lists so that we can modify the tail and head positions without
                screwing up the old edge's position.
            (b) we get the position of the new edge's tail and head
            (c) we create the new edge
            (d) if the edge we intend to paste already exists in our frame we just move onto the
                next edge
            (e) if it doesn't exist we add it to the list of new edges and update the vertices
            (f) finally we update the original list with the new edges
        """
        new_edges = []
        for edge in edges:
            tail, head = [e for e in edge.tail], [e for e in edge.head]                                 # (a)
            tail[dimension] += distance                                                                 # (b)
            head[dimension] += distance
            new_edge = Edge(tail, head, edge.id)                                                        # (c)
            if new_edge in edges: continue                                                              # (d)
            new_edges.append(new_edge)                                                                  # (e)
            self.welcome_edge(new_edge)
        edges.update(new_edges)                                                                         # (f)

    def seed_frame(self, shape):
        """
        Input:
            shape - a list specifying for each dimension how far the frame should extend

        This method creates a frame with the input shape populated ONLY with coordinate vectors.

        NOTES:
            (a) we create a unit frame filled with coordinate vectors
            (b) we take the current frame and for each dimension copy and paste it in increments of
                the smallest distance between vertices along that dimension (as specified in steps)
                enough times to extend it along that dimension enough to match the distance specified
                in the shape
            (c) we set the shape of this frame
        """
        self.create_hyper_cube()                                                                        # (a)
        for i in range(self.dimensions):                                                                # (b)
            for j in range(int((shape[i] - 1) * self.steps[i])):
                self.copy_and_add(self.coordinate_vectors, i, Fraction(1, self.steps[i]))
        self.shape = shape                                                                              # (c)

    def populate(self, cross_vector):
        """
        Input:
            cross_vector - an Edge corresponding to a cross vector

        This method takes an example cross vector, figures out what the vector difference is between
        it's head and tail, and then adds every possible edge of the same kind that can fit between
        the vertices currently in the frame.

        This method works by taking each vertex and the vector dif between head and tail of the input
        vector and determining what vertex must exist for the vector to extend from the vertex at
        hand. If that vertex exists an edge corresponding to the cross vector is added.

        NOTES:
            (a) get the position of the vertex we would need if this cross vector were to extend
                from the current vertex
            (b) check if the vertex exists and if it does create and add the edge!
        """
        edge_dif = [cross_vector.head[i] - cross_vector.tail[i] for i in range(self.dimensions)]
        for position in self.vertices:
            needed_position = tuple([position[i] + edge_dif[i] for i in range(self.dimensions)])        # (a)
            if needed_position in self.vertices:                                                        # (b)
                new_edge = Edge(position, needed_position, cross_vector.id)
                self.welcome_edge(new_edge)
                self.cross_vectors.add(new_edge)

    def double(self, dimension):
        """
        Input:
            dimension - the index of the dimension to grow along

        This method doubles the size of the frame along the specified dimension.

        NOTES:
            (a) we simply copy and paste the current frame (cross and coordinate vectors) by
                the smallest distance between vertices specified by steps[dimension]
        """
        for i in range(int(self.shape[dimension] * self.steps[dimension])):                             # (a)
            self.copy_and_add(self.cross_vectors, dimension, Fraction(1, self.steps[dimension]))
            self.copy_and_add(self.coordinate_vectors, dimension, Fraction(1, self.steps[dimension]))
        self.shape[dimension] += self.shape[dimension]

    def grow_to_size(self, block_shape):
        deltas = [block_shape[i] - self.shape[i] for i in range(len(self.shape))]
        negatives = [i for i in range(len(deltas)) if deltas[i] < 0]
        if negatives:
            print 'cannot grow to size: block is already bigger along dimensions %s' % negatives
            return False
        for i in range(len(deltas)):
            for j in range(int(deltas[i] * self.steps[i])):
                self.copy_and_add(self.cross_vectors, i, Fraction(1, self.steps[i]))
                self.copy_and_add(self.coordinate_vectors, i, Fraction(1, self.steps[i]))
        self.shape = block_shape
        return True



