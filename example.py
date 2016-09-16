from kirky import Kirchhoff
import numpy as np

"""
To generate the Kirchhoff Graph for the matrix
1 0 2 1
0 1 1 2
"""
matrix = np.array([[2,1], [1,2]])
k = Kirchhoff(matrix)
k.find('drawings/kirchhoff1')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -1 1 1
0 1  1 2 1
"""
matrix = np.array([[-1,1,1],[1,2,1]])
k = Kirchhoff(matrix)
k.find('drawings/kirchhoff2')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -1 1  3
0 1  1 2 -1
"""
matrix = np.array([[-1,1, 3],[1,2, -1]])
k = Kirchhoff(matrix)
k.find('drawings/kirchhoff3')
