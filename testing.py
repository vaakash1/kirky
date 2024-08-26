from kirky import Kirchhoff
from kirky.block_q import *
from kirky.imagine import draw_graph, draw3d
import numpy as np
matrix = np.array([[0, 1], [1, 0], [1, 2], [2, 1]])
k = Kirchhoff(matrix)
k.draw_solution(np.array([1, 0, 1.414, 0.618]), np.array([0, 1, 0.618, 1.414]))
