import numpy as np
from block import Edge, Block
from linsolve import positive_nullspace_vector
from draw import DrawEdge
from pyx import canvas


class Kirchhoff(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.dimensions = matrix.shape[0]
        self.num_vectors = self.dimensions + matrix.shape[1]
        # setup the block
        self.block = Block(self.dimensions, self.num_vectors)
        first_frame_shape = self.get_first_frame_shape()
        self.block.seed_frame(first_frame_shape)
        interior_edges = self.get_interior_edges()
        for edge in interior_edges:
            self.block.populate_interior(edge)
        # and we're all set to go

    def get_first_frame_shape(self):
        # this gets how big the seed frame will need to be
        shape = []
        for row in self.matrix:
            max_element = max([abs(element) for element in row])
            shape.append(max_element)
        return shape

    def get_interior_edges(self):
        edges = []
        trans = np.transpose(self.matrix)
        id = self.dimensions
        for row in trans:
            # each row is just the vector we're looking for given our construction
            head = [element for element in row]
            tail = [0 for i in range(self.dimensions)]
            edge = Edge(tail, head, id)
            edges.append(edge)
            id += 1
        return edges

    def generate_linear_system(self):
        rows = []
        for position in self.block.vertices:
            vertex = self.block.vertices[position]
            # for each vertex we have to create as many rows as there are columns in our block
            # each row will correspond to one dependent vector
            for i in range(self.matrix.shape[1]):
                row = [0 for i in range(len(self.block.frame) + len(self.block.interior))]
                # first we add in the independent vectors to this row
                for j in range(self.dimensions):
                    # we get the multipler for this independent vector
                    multiplier = self.matrix[j,i]
                    # now we can add in our independents into the row
                    in_edge, out_edge = vertex.cut[j]
                    if in_edge:
                        row[in_edge.pin] = -1.0 * multiplier
                    if out_edge:
                        row[out_edge.pin] = 1.0 * multiplier
                # and now we add in the negative of our dependents so that we can solve
                # for the nullspace later
                in_edge, out_edge = vertex.cut[self.dimensions + i]
                if in_edge:
                    row[in_edge.pin] = 1.0
                if out_edge:
                    row[out_edge.pin] = -1.0
                # and now we can add our row to rows
                rows.append(row)
        # now we create a matrix from these rows
        return np.array(rows)

    def solve(self, linear_system):
        return positive_nullspace_vector(linear_system)

    def set_edge_weights(self, solution):
        edges = [edge for edge in self.block.frame] + [edge for edge in self.block.interior]
        edges = sorted(edges, key=lambda edge: edge.pin)
        for i in range(len(edges)):
            edges[i].weight = solution[i, 0]

    def draw_edges(self, canvas):
        for edge in self.block.frame:
            DrawEdge(edge, canvas)
        for edge in self.block.interior:
            DrawEdge(edge, canvas)

    def find(self, file=''):
        dimension = 0
        while True:
            linear_system = self.generate_linear_system()
            solution = self.solve(linear_system)
            if not solution:
                self.block.double(dimension)
                dimension = (dimension + 1) % self.dimensions
            else:
                break
        self.set_edge_weights(solution)
        if file:
            c = canvas.canvas()
            self.draw_edges(c)
            c.writePDFfile(file)





