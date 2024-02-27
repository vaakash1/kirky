from kirky import Kirchhoff
import numpy as np
from fractions import Fraction
from kirky.imagine import draw

"""
To generate the Kirchhoff Graph for the matrix
1 0 2 1
0 1 1 2
"""
matrix = np.array([[Fraction(2),Fraction(1)], [Fraction(1),Fraction(2)]])
k = Kirchhoff(matrix)
#k.find()
#draw(k, 'drawings/kirchhoff1.png')
l = Kirchhoff(matrix)
l.find_scipy()
draw(l, 'drawings/kirchhoff1_scipy.png')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -1 1 1
0 1  1 2 1
"""
matrix = np.array([[Fraction(-1),Fraction(1),Fraction(1)],[Fraction(1),Fraction(2),Fraction(1)]])
k = Kirchhoff(matrix)
#k.find()
#draw(k, 'drawings/kirchhoff2.png')
l = Kirchhoff(matrix)
l.find_scipy()
draw(l, 'drawings/kirchhoff2_scipy.png')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -1 1  3
0 1  1 2 -1
"""
matrix = np.array([[Fraction(-1),Fraction(1), Fraction(3)],[Fraction(1),Fraction(2), Fraction(-1)]])
k = Kirchhoff(matrix)
#k.find()
#draw(k, 'drawings/kirchhoff3.png')
l = Kirchhoff(matrix)
l.find_scipy()
draw(l, 'drawings/kirchhoff3_scipy.png')

"""
To generate the Kirchhoff Graph for the matrix
1 0 -3/2 1/2
0 1  1/2 1/2
"""
matrix = np.array([[Fraction(-3,2),Fraction(1,2)], [Fraction(1,2),Fraction(1,2)]])
k = Kirchhoff(matrix)
#k.find()
#draw(k, 'drawings/kirchhoff4.png')
l = Kirchhoff(matrix)
l.find_scipy()
draw(l, 'drawings/kirchhoff4_scipy.png')

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
#k.find()
#draw(k, 'drawings/kirchhoff5.png', x=[0.5, 0, 1], y=[-0.5, 1, 0])

l = Kirchhoff(matrix)
l.find_scipy()
draw(l, 'drawings/kirchhoff5_scipy.png', x=[0.5, 0, 1], y=[-0.5, 1, 0])
draw(l, 'drawings/kirchhoff5_rot_scipy.png', x=[0.6, 0, 1], y=[-0.4, 1, 0])