import numpy as np
from .block import Edge, Block
from .linsolve import exact_positive_null_space_vector
from .draw import DrawEdge
from pyx import canvas
from .helpers import common_denominator
from fractions import Fraction
from sympy import Matrix, fraction, Rational
from .linsolve import nullspace


class Kirchhoff(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.dimensions = matrix.shape[0]
        self.num_vectors = self.dimensions + matrix.shape[1]
        self.steps = self.get_steps()
        # setup the block
        self.block = Block(self.dimensions, self.num_vectors, self.steps)
        first_frame_shape = self.get_first_frame_shape()
        self.block.seed_frame(first_frame_shape)
        interior_edges = self.get_interior_edges()
        for edge in interior_edges:
            self.block.populate_interior(edge)
        # and we're all set to go

    def get_steps(self):
        # we run through each of the dimensions (rows) of our input matrix
        steps = []
        for row in self.matrix:
            # we want to find the least common denominator and add it to steps
            steps.append(common_denominator([fraction for fraction in row]))
        return steps

    def get_first_frame_shape(self):
        # this gets how big the seed frame will need to be
        shape = []
        for row in self.matrix:
            max_element = max([abs(element) for element in row])
            shape.append(max_element)
        altered_shape = []
        for element in shape:
            if element < 1:
                altered_shape.append(Fraction(1))
            else:
                altered_shape.append(element)
        return [e for e in altered_shape]

    def get_interior_edges(self):
        edges = []
        trans = np.transpose(self.matrix)
        id = self.dimensions
        for row in trans:
            # each row is just the vector we're looking for given our construction
            head = [element for element in row]
            tail = [Fraction(0) for i in range(self.dimensions)]
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
                row = [Rational(0,1) for k in range(len(self.block.frame) + len(self.block.interior))]
                # first we add in the independent vectors to this row
                for j in range(self.dimensions):
                    # we get the multipler for this independent vector
                    multiplier = self.matrix[j, i]
                    # now we can add in our independents into the row
                    in_edge, out_edge = vertex.cut[j]
                    if in_edge:
                        row[in_edge.pin] = Rational(-1 * multiplier.numerator, multiplier.denominator)
                    if out_edge:
                        row[out_edge.pin] = Rational(1 * multiplier.numerator, multiplier.denominator)
                # and now we add in the negative of our dependents so that we can solve
                # for the nullspace later
                in_edge, out_edge = vertex.cut[self.dimensions + i]
                if in_edge:
                    row[in_edge.pin] = Rational(1,1)
                if out_edge:
                    row[out_edge.pin] = Rational(-1,1)
                # and now we can add our row to rows
                rows.append(row)
        return Matrix(rows)

    def solve(self, linear_system):
        vector_solution = exact_positive_null_space_vector(linear_system)
        return vector_solution

    def normalize_solution(self, vector_solution):
        # turn the solution to a list for ease of use
        solution = [vector_solution[i, 0] for i in range(vector_solution.shape[0])]
        min_element = 0
        for element in solution:
            if min_element == 0 or min_element > element and element != 0:
                min_element = element
        return [element / min_element for element in solution]

    def set_edge_weights(self, solution):
        edges = [edge for edge in self.block.frame] + [edge for edge in self.block.interior]
        edges = sorted(edges, key=lambda edge: edge.pin)
        for i in range(len(edges)):
            edges[i].weight = solution[i]

    def draw_edges(self, canvas):
        count = 1
        print 'DRAWING FRAME'
        for edge in self.block.frame:
            print 'drawing edge %s/%s' % (count, len(self.block.frame))
            DrawEdge(edge, canvas)
            count += 1
        count = 1
        print 'DRAWING INTERIOR'
        for edge in self.block.interior:
            print 'drawing edge %s/%s' % (count, len(self.block.interior))
            DrawEdge(edge, canvas)
            count += 1

    def find(self, file=''):
        dimension = 0
        while True:
            print '--> generating linear system'
            linear_system = self.generate_linear_system()
            print '     size is %s' % (linear_system.shape,)
            print '--> trying to find a solution'
            vector_solution = self.solve(linear_system)
            if vector_solution is None:
                print '--> solution not found'
                print '--> doubling along dimension %s' % dimension
                self.block.double(dimension)
                dimension = (dimension + 1) % self.dimensions
            else:
                break
        solution = self.normalize_solution(vector_solution)
        self.set_edge_weights(solution)
        if file:
            c = canvas.canvas()
            self.draw_edges(c)
            c.writePDFfile(file)

    def see_block(self, file):
        for edge in self.block.frame:
            edge.weight = edge.pin
        for edge in self.block.interior:
            edge.weight = edge.pin
        c = canvas.canvas()
        self.draw_edges(c)
        c.writePDFfile(file)





