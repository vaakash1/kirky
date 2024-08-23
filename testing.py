from kirky import Kirchhoff
from kirky.block_q import *
from kirky.imagine import draw_graph, draw3d
import numpy as np
matrix = np.array([[1, 1, 3], [1, 2, -1]])
k = Kirchhoff(matrix, q = 3, search_depth=2)
k.draw_solution(np.array([1, 0]), np.array([0, 1]))
