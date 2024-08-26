import numpy as np
from .block_q import Frame
from scipy.optimize import linprog
from .imagine import draw_graph, draw_graph_slider
"""
The Kirchhoff class represents a Kirchhoff matrix and provides methods for matrix manipulation.

Attributes:
    q (int): The value of q used for matrix augmentation.
    dimensions (int): The number of dimensions in the matrix.
    num_vectors (int): The total number of vectors in the matrix.
    matrix (ndarray): The Kirchhoff matrix.

Methods:
    __init__(self, matrix, q=1): Initializes a Kirchhoff object with the given matrix and q value.
    parse_matrix(self, matrix): Parses the given matrix and performs matrix operations.
    augment_identity(self): Augments the matrix with an identity matrix.
    reduce_matrix(self): Reduces the matrix by dividing all elements by their greatest common divisor.
"""
import numpy as np

class Kirchhoff(object):
    """
    A class representing Kirchhoff matrices and their operations.
    """

    def __init__(self, matrix, q=1):
        """
        Initializes a Kirchhoff object.

        Parameters:
        - matrix (numpy.ndarray): The input matrix.
        - q (int): The value of q (default is 1).
        """
        self.q = q
        self.dimensions = matrix.shape[0]
        self.num_vectors = self.dimensions + matrix.shape[1]
        self.parse_matrix(matrix)
        self.frame = Frame(self.matrix, q=q)

    def parse_matrix(self, matrix):
        """
        Parses the input matrix and performs necessary operations.

        Parameters:
        - matrix (numpy.ndarray): The input matrix.
        """
        self.matrix = np.array(matrix, dtype=np.int16)
        self.augment_identity()
        self.reduce_matrix()

    def augment_identity(self):
        """
        Augments the input matrix with an identity matrix.

        The augmented matrix has dimensions (dimensions x num_vectors).
        """
        new_matrix = np.zeros((self.dimensions, self.num_vectors))
        for (i, row) in enumerate(self.matrix):
            new_matrix[i] = np.append(np.zeros(self.dimensions), row)
            new_matrix[i][i] = self.q
        self.matrix = new_matrix

    def reduce_matrix(self):
        """
        Reduces the matrix by dividing all elements by their greatest common divisor.
        """
        b = self.matrix.flatten().astype(np.int16)
        gcd = np.gcd.reduce(b)
        self.matrix = self.matrix / gcd
    
    def generate_linear_system(self):
        # generate null matrix
        null_matrix = np.copy(self.matrix)
        null_matrix = np.vstack([null_matrix, np.zeros((self.num_vectors - self.dimensions, self.num_vectors))])
        for i in range(self.num_vectors):
            null_matrix[i][i] = -self.q
        null_matrix = np.delete(null_matrix, np.s_[:self.dimensions], 1)
        null_matrix = np.transpose(null_matrix)                
        system = []
        for (i, edge) in enumerate(self.frame.edges):
            edge.pin = i
        num_edges = len(self.frame.edges)
        for position in self.frame.vertices:
            vertex = self.frame.vertices[position]
            for null_row in null_matrix:
                system_row = [0 for _ in range(num_edges)]
                for edge in vertex.incoming:
                    if edge != None:
                        system_row[edge.pin] -= null_row[edge.id]
                for edge in vertex.outgoing:
                    if edge != None:
                        system_row[edge.pin] += null_row[edge.id]
                system.append(system_row)
        return system

                        
    def get_random_objective_vector(self, num_dims):
        """
        Generates a random objective vector of length num_weights.
        """
        return [num_dims * np.random.random() for _ in range(num_dims)]

    def solve(self, random_objective_vector = True):
        E = self.generate_linear_system()
        num_weights = len(E[0])
        sum_condition_row = [1] * num_weights + [-1]
        sum_condition_value = 1
        for row in E:
            row.append(0)
        E.append(sum_condition_row)
        b = [0] * (len(E) - 1) + [sum_condition_value]
        if(random_objective_vector == False):
            c = [1 for i in range(num_weights + 1)]
        else:
            c = self.get_random_objective_vector(num_weights + 1)
        result = linprog(c, A_eq=E, b_eq=b, integrality=1)
        print(result.x)

        status = result.status
        print(status)
        if(status == 0 ):
            intSolution = np.array([round(x) for x in result.x])
            toCheck = intSolution * E
            if(np.sum(toCheck[:-1]) == 0):
                return intSolution
        return None
    
    def draw_solution(self, x, y):
        A = self.generate_linear_system()
        print(np.shape(A))
        solution = self.solve(A)
        if(solution is None):
            self.frame.expand()
            self.draw_solution(x, y)
            print("No solution found")
            return
        
        # update the weights
        for edge in self.frame.edges:
            edge.weight = solution[edge.pin]
        print(solution)
        # draw the graph
        draw_graph_slider(self, x, y)
