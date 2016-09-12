from sympy import Matrix
from positive_solve import divider, dot, positive, normalize
import numpy as np


def backout_matrix(vectors):
    """
    backout_matrix(vectors) - this function takes a series of vectors
    which are assumed to comprise the nullspace of some matrix M. It
    then finds A for you and returns it. It should be noted that uses
    sympy so all solutions are exact (or as exact as your input vectors)
    """
    # first we create a matrix from these vectors
    N = Matrix(vectors)
    # next we grab a series of vectors that comprise the nullspace of N
    nullspace_vectors = []
    for column_vector in N.nullspace():
        nullspace_vectors.append([element for element in column_vector])
    # we create a matrix from these vectors, and this matrix will be A
    A = Matrix(nullspace_vectors)
    return A


def test_backout_matrix():
    vectors = [[2, 1, -1, 0], [1, 2, 0, -1]]
    A = backout_matrix(vectors)
    expected_A = Matrix([[1, 0, 2, 1], [0, 1, 1, 2]])
    assert A.rref()[0] == expected_A


# ------------------ DIVIDER TESTS ------------------


def test_easy_pass_divider():
    vectors = [[1, 0], [0, -1]]
    norm = divider(vectors)
    all_pass = True
    for vector in vectors:
        if dot(vector, norm) < 0:
            all_pass = False
    assert all_pass


def test_hard_pass_divider():
    vectors = [[1, 1], [-1, -1], [1, -1]]
    norm = divider(vectors)
    all_pass = True
    for vector in vectors:
        product = dot(vector, norm)
        # remember there might be a tad bit of error
        if abs(product) < 10.0 ** -13:
            continue
        if product < 0:
            all_pass = False
    assert all_pass


def test_input_only_reflections_fail_divider():
    vectors = [[1, 1], [-1, -1]]
    norm = divider(vectors)
    assert norm is None


def test_unsplittable_fail_divider():
    vectors = [[-1, 0], [0, 1], [1, -1]]
    norm = divider(vectors)
    assert norm is None


def test_3d_pass_divider():
    vectors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    norm = divider(vectors)
    all_pass = True
    for vector in vectors:
        if dot(vector, norm) < 0:
            all_pass = False
    assert all_pass


# ------------------ ------------- ------------------


# ------------------ POSITIVE TESTS ------------------


def test_positive_pass():
    matrix = np.array([[1, 1, -1], [-1, 1, -1]])
    pos = positive(matrix)
    pos = normalize(pos[0].tolist())
    assert pos == [1.0, 0.0, 0.0]


def test_positive_fail():
    matrix = np.array([[1, 0, -1], [-1, 1, 0]])
    pos = positive(matrix)
    assert pos is None


# ------------------ ------------- ------------------
