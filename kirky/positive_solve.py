from sklearn.svm import SVC
from issue import Issue
from fractions import Fraction, gcd
import numpy as np
from numpy.linalg import svd


def reflect(_list):
    return [-a for a in _list]


def dot(vector1, vector2):
    return sum([vector1[i] * vector2[i] for i in range(len(vector1))])


class Divider(object):
    # the svm calculator works well until one vector belongs to both classes

    def __init__(self):
        self.vectors = set()
        self.training_data = []
        self.classifications = []
        self.svm = SVC(kernel='linear')

    def add(self, vector):
        size = abs(sum(vector))
        if size == 0: size = 1.0
        normed_vector = [element / size for element in vector]
        tup = tuple(normed_vector)
        if tup not in self.vectors:
            self.vectors.add(tup)

    def _create_training_data(self):
        """
        In this step, we take all of our vectors and reflect them. The normal vectors will be one
        group and the reflected vectors will be the second group. We do this because if we can split
        these two groups, then we can find a hyperplane through the origin that divides the space into
        two where all of the input vectors are on one side.
        """
        # we create the training data from our normal vectors and the reflected vectors
        # svm doesn't like when one vector belongs to two classes so we are avoiding that here
        # by only taking reflections that aren't in the vectors set
        reflections = []
        for vector in self.vectors:
            reflection = tuple(reflect(vector))
            if reflection not in self.vectors:
                reflections.append(reflection)
        self.training_data = [vector for vector in self.vectors] + reflections
        # we create their classifications
        self.classifications = [0] * len(self.vectors) + [1] * len(reflections)
        # now we check to see if we have one of class 1. If we don't we know all the vectors have their reflection
        # present, so either all of these vectors lie in the same plane (in which case we need to choose a side)
        # or they don't (and this is going to fail regardless
        # so we create that extra vector to pick a side
        for arb_vector in self.vectors:
            break
        refl_vector = reflect(arb_vector)
        new_vector = [(arb_vector[i] + refl_vector[i])/2.0 for i in range(len(arb_vector))]
        self.training_data.append(new_vector)
        self.classifications.append(1)

    def divide(self):
        self._create_training_data()
        self.svm.fit(self.training_data, self.classifications)
        # we get the norm to the plane that our model thinks divides the two sets
        # I know this looks weird, but the coefficients are an array in a list so its weird...
        norm = self.svm.coef_[0].tolist()
        # next we run through the vectors and see if their dot product with the norm is all
        # positive, if the norm is the wrong way on the first dot product that isn't zero we flip it once
        has_flipped = False
        for vector in self.vectors:
            product = dot(norm, vector)
            if product < 0 and not has_flipped:
                norm = reflect(norm)
                product = dot(norm, vector)
                has_flipped = True
            if product < 0:
                raise Issue('vectors cannot be divided')
        # now we remove everything from the elements of the norm that are as small as or smaller than the margin
        # now we can return the norm
        return norm


# this gets the null space
def null(matrix, atol=10**-14, rtol=0):
    matrix = np.atleast_2d(matrix)
    u, s, vh = svd(matrix)
    tol = max(atol, rtol * s[0])
    nnz = (s >= tol).sum()
    ns = vh[nnz:].conj().T
    return ns


# this gets rid of anything on the order of 10**-14
def shave(matrix, tol=10**-14):
    rows = []
    for row in matrix:
        new_row = [Fraction(element).limit_denominator(int(1.0/tol)) for element in row]
        rows.append(new_row)
    return np.array(rows)


# this gets the positive of the matrix if it exists
def positive(matrix):
    trans = np.transpose(matrix)
    vectors = [row for row in trans]
    divider = Divider()
    for vector in vectors:
        divider.add(vector)
    try:
        norm = divider.divide()
    except Issue:
        raise Issue('no positive exists')
    norm = np.array([[element for element in norm]])
    return np.dot(norm, matrix)


def positive_null(matrix):
    n = np.transpose(null(matrix))
    if n.shape[0] == 0:
        return None
    n = shave(n)
    try:
        return np.transpose(positive(n))
    except Issue:
        return None


