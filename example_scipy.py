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
	k.find_scipy()
	draw(k, 'drawings/kirchhoff1_scipy.png')

	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 -1 1 1
	0 1  1 2 1
	"""
	matrix = np.array([[-1,1,1],[1,2,1]])
	k = Kirchhoff(matrix)
	k.find_scipy()
	draw(k, 'drawings/kirchhoff2_scipy.png')

	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 -1 1  3
	0 1  1 2 -1
	"""
	matrix = np.array([[-1,1, 3],[1,2, -1]])
	k = Kirchhoff(matrix)
	k.find_scipy()
	draw(k, 'drawings/kirchhoff3_scipy.png')

	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 -3/2 1/2
	0 1  1/2 1/2
	"""
	matrix = np.array([[-3,1], [1,1]])
	k = Kirchhoff(matrix, q=2)
	k.find_scipy()
	draw(k, 'drawings/kirchhoff4_scipy.png')


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
	k.find_scipy()
	draw(k, 'drawings/kirchhoff5_scipy.png')
	#draw3d(k, 'drawings/kirchhoff5_3d_scipy.png')
run()