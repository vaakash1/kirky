from kirky import Kirchhoff
import numpy as np
from fractions import Fraction
from kirky.imagine import draw, draw3d

"""
To generate the Kirchhoff Graph for the matrix
1 0 2 1
0 1 1 2
"""
matrix = np.array([[Fraction(2),Fraction(1)], [Fraction(1),Fraction(2)]])
k = Kirchhoff(matrix)
k.find()
draw(k, 'drawings/kirchhoff1.png')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -1 1 1
0 1  1 2 1
"""
matrix = np.array([[Fraction(-1),Fraction(1),Fraction(1)],[Fraction(1),Fraction(2),Fraction(1)]])
k = Kirchhoff(matrix)
k.find()
draw(k, 'drawings/kirchhoff2.png')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -1 1  3
0 1  1 2 -1
"""
matrix = np.array([[Fraction(-1),Fraction(1), Fraction(3)],[Fraction(1),Fraction(2), Fraction(-1)]])
k = Kirchhoff(matrix)
k.find()
draw(k, 'drawings/kirchhoff3.png')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -3/2 1/2
0 1  1/2 1/2
"""
matrix = np.array([[Fraction(-3,2),Fraction(1,2)], [Fraction(1,2),Fraction(1,2)]])
k = Kirchhoff(matrix)
k.find()
draw(k, 'drawings/kirchhoff4.png')

"""
To generate the Kirchhoff Graph for the matrix
1 0 0 2 1 1
0 1 0 1 2 1
0 0 1 2 1 2
"""
matrix = np.array([[Fraction(2),Fraction(1), Fraction(1)], 
				   [Fraction(1),Fraction(2), Fraction(1)],
				   [Fraction(1),Fraction(1), Fraction(2)]])
k = Kirchhoff(matrix)
k.find()
#draw(k, 'drawings/kirchhoff5.png', x=[0.5, 0, 1], y=[-0.5, 1, 0])
draw3d(k, 'drawings/kirchhoff5_3d.png')