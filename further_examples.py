from kirky import Kirchhoff
from sympy import Matrix

"""
For the matrix
1 0 -1 1 1
0 1  1 2 1
"""
m = Matrix([[-1,1, 1],[1,2, 1]])
k = Kirchhoff(m, m.T, [1,1,1])
k.Find('drawings/kirchhoff1')

"""
For the matrix
1 0 -1 1  3
0 1  1 2 -1
"""
m = Matrix([[-1,1, 3],[1,2, -1]])
k = Kirchhoff(m, m.T, [1,1,1])
k.Find('drawings/kirchhoff2')

"""
For the matrix
1 0 -1 3 1 2
0 1  1 2 1 1
"""
m = Matrix([[-1,3, 1, 2],[1,2, 1, 1]])
k = Kirchhoff(m, m.T, [1,1,1,1])
k.Find('drawings/kirchhoff3')

"""
For the matrix
1 0 -1   1
0 1  1 -10
"""
m = Matrix([[-1,1],[1,-10]])
k = Kirchhoff(m, m.T, [1,1])
k.Find('drawings/kirchhoff4')


