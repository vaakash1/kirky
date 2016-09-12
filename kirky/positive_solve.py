from sklearn.svm import SVC
from issue import Issue
from fractions import Fraction, gcd
import numpy as np
from numpy.linalg import svd
from math import sqrt


def reflect(_list):
    return [-a for a in _list]


def dot(vector1, vector2):
    return sum([vector1[i] * vector2[i] for i in range(len(vector1))])


def normalize(vector):
    length = sqrt(sum([element ** 2 for element in vector]))
    if length == 0.0:
        return [element for element in vector]
    else:
        return [element / length for element in vector]


def divider(vectors, C=1000.0, max_iter=-1):
    """
    divider(vectors) - this function takes a list of vectors (iterables
    with number elements) and tries to find a hyperplane, passing through
    the origin that divides the space the vectors lie in into two pieces
    - one piece having all the vectors and the other piece being empty.

    It does the splitting using a linear kernel support vector machine.
    Of course svm's require two classes of data points to split. One class
    is the input vectors. The other class is all of the vector reflections
    that aren't equal to one of the input vectors.

    It RETURNS the vector that is both normal to the splitting hyperplane
    and also on the same side as the vectors that were split. If no such vector
    exists (i.e. the hyperplane doesn't exist) then None is returned.
    """
    # first we normalize the vectors
    vectors = [normalize(vector) for vector in vectors]
    # next we create a set out of these vectors (for easy lookup when we need to
    # check that reflections are not also equal to an input vector)
    vectors = set(vectors)
    # now we create the reflections
    reflections = [reflect(vector) for vector in vectors if reflect(vector) not in vectors]
    # now that we have our two classes, we can create our training data for the SVM
    data = [vector for vector in vectors] + reflections
    # and of course we need the classifications list as well (for the svm)
    classifications = [0] * len(vectors) + [1] * len(reflections)
    # now if all of the vectors had their reflection as another input vector. Then all vectors
    # if they can be split by a plane, all lie in that plane. Now because we are splitting
    # to get a norm that will give us a positive for the matrix defined by these vectors (as columns)
    # we call this a failure case because the resultant norm would only give us a zero vector
    # when multiplied by the matrix because it is pi/2 radians from all column vectors in M
    if 1 not in classifications:
        return None
    # now we create and fit our svm. Note I use a large C by default
    svm = SVC(kernel='linear', C=C, max_iter=max_iter)
    svm.fit(data, classifications)
    # next we grab the normal the svm has found
    norm = svm.coef_[0].tolist()
    # okay, so we have our expected norm, time to see if it actually divides the two
    # it is possible that the norm is the wrong way around, so we will reserve a single flip
    # the following boolean lets us know if the flip has happened.
    has_flipped = False
    for vector in vectors:
        product = dot(vector, norm)
        if product == 0:
            continue
        if product > 0 and not has_flipped:
            # our norm must be on the right side in this case
            has_flipped = True
        elif product < 0 and not has_flipped:
            # we need to flip our norm
            norm = reflect(norm)
            has_flipped = True
        elif product < 0 and has_flipped:
            # we found a vector that's on the wrong side of the plane - game over
            return None
    # if we've gotten to this point, then all has passed! so we return the norm
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
        new_row = [float(Fraction(element).limit_denominator(int(1.0/tol))) for element in row]
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
        'empty nullspace found'
        return None
    print 'found non-empty nullspace'
    n = shave(n)
    try:
        'positive found for nullspace'
        return np.transpose(positive(n))
    except Issue:
        print 'no positive found for nullspace'
        return None


