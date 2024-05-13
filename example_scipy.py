from kirky import Kirchhoff
from kirky.imagine import draw, draw3d
import numpy as np
from fractions import Fraction

def run():
	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 2 1
	0 1 1 2
	"""
	matrix = np.array([[2,1], [1,2]])
	k = Kirchhoff(matrix)
	k.draw_solutions_scipy('drawings2', 'kirchhoff0')

	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 -1 1 1
	0 1  1 2 1
	"""
	matrix = np.array([[-1,1,1],[1,2,1]])
	k = Kirchhoff(matrix)
	k.draw_solutions_scipy('drawings2', 'kirchhoff1')

	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 -1 1  3
	0 1  1 2 -1
	"""
	matrix = np.array([[-1,1, 3],[1,2, -1]])
	k = Kirchhoff(matrix)
	k.draw_solutions_scipy('drawings2', 'kirchhoff2')

	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 -3/2 1/2
	0 1  1/2 1/2
	"""
	matrix = np.array([[-3,1], [1,1]])
	k = Kirchhoff(matrix, q=2)
	k.draw_solutions_scipy('drawings2', 'kirchhoff3')


	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 0 2 1 1
	0 1 0 1 2 1
	0 0 1 2 1 2
	"""
	matrix = np.array([[2,1, 1], 
					[1,2, 1],
					[1,1, 2]])
	k = Kirchhoff(matrix)
	k.draw_solutions_scipy('drawings2', 'kirchhoff4')
run()