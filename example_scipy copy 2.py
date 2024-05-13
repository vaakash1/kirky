from kirky import Kirchhoff
from kirky.imagine import draw, draw3d
import numpy as np
from fractions import Fraction

def run():
	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 1 1 
    0 1 1 -3
	"""
	for i in range(100):
     # Fehribach example
		matrix = np.array([[1,0, 1], [2, -1, 1], [-1,1, -1]])
		k = Kirchhoff(matrix)
		k.find_scipy(random_objective_vector=True)
		draw3d(k, 'drawingsTestInf2.png')
	k.draw_solutions_scipy('drawingsTestInf', '1,0,1,1;-,1,1,-3')
 
	"""
	To generate the Kirchhoff Graph for the matrix
	1 0 0 2 1 1
	0 1 0 1 2 1
	0 0 1 2 1 2
	"""
	matrix = np.array([[2,1, 1], [1,2, 1], [2, 1, 2]])
	k = Kirchhoff(matrix)
	k.draw_solutions_scipy('drawingsTestInf', '1,0,0,2,1,1;0,1,0,1,2,1;0,0,1,2,1,2')
run()