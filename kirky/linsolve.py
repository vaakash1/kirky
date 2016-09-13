from sklearn.svm import SVC
from fractions import Fraction
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


def divider(vectors, C=1000.0, max_iter=10000, tol=10.0**-13):
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
    vectors = [tuple(normalize(vector)) for vector in vectors]
    # next we create a set out of these vectors (for easy lookup when we need to
    # check that reflections are not also equal to an input vector)
    vectors = set(vectors)
    # now we create the reflections
    reflections = [reflect(vector) for vector in vectors if tuple(reflect(vector)) not in vectors]
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
    svm = SVC(kernel='linear', C=C, max_iter=max_iter, tol=tol)
    svm.fit(data, classifications)
    # next we grab the normal the svm has found
    norm = svm.coef_[0].tolist()
    # okay, so we have our expected norm, time to see if it actually divides the two
    # it is possible that the norm is the wrong way around, so we will reserve a single flip
    # the following boolean lets us know if the flip has happened.
    has_flipped = False
    for vector in vectors:
        product = dot(vector, norm)
        # the norm isn't going to be perfect, so we allow for some leeway in what a zero is
        # if it passes this and is negative, then we know its too negative to ignore
        if abs(product) < tol:
            continue
        if product > 0 and not has_flipped:
            # our norm must be on the right side in this case
            has_flipped = True
        elif product < 0 and not has_flipped:
            # we don't want to be tripped up by little errors
            # we need to flip our norm
            norm = reflect(norm)
            has_flipped = True
        elif product < 0 and has_flipped:
            print product
            # we found a vector that's on the wrong side of the plane - game over
            return None
    # if we've gotten to this point, then all has passed! so we return the norm
    return norm


def nullspace(matrix, atol=10**-13, rtol=0):
    """
    nullspace(matrix, atol=10**-14, rtol=0) - This function takes a numpy matrix and returns the nullspace
    matrix for the input. The code was copied from http://scipy-cookbook.readthedocs.io/items/RankNullspace.html
    Check that site out if you want to know more.

    But just in case the site disappears, this is what the site says:
        matrix should be at most 2-D.  A 1-D array with length k will be treated
            as a 2-D with shape (1, k)
        atol : float
            The absolute tolerance for a zero singular value.  Singular values
            smaller than `atol` are considered to be zero.
        rtol : float
            The relative tolerance.  Singular values less than rtol*smax are
            considered to be zero, where smax is the largest singular value.
    """
    matrix = np.atleast_2d(matrix)
    u, s, vh = svd(matrix)
    tol = max(atol, rtol * s[0])
    nnz = (s >= tol).sum()
    ns = vh[nnz:].conj().T
    return ns


def shave(matrix, tol=10**-13):
    """
    shave(matrix, tol=10**-13) - This function takes a matrix and goes through each of its elements
    using python's Fraction to find the closes number that does not have any part smaller than the
    input tolerance (tol). It does this by converting the element to a Fraction where the denominator
    is limited to being no greater than 1 / tol. It then spits out the resulting matrix.
    """
    rows = []
    max_denominator = int(1.0 / tol)
    for row in matrix:
        new_row = [float(Fraction(element).limit_denominator(max_denominator)) for element in row]
        rows.append(new_row)
    return np.array(rows)


def positive(matrix):
    """
    positive(matrix) - Given a numpy matrix, this function returns its positive if it exists and None otherwise
    """
    # we transpose the matrix so we can easily grab its columns
    trans = np.transpose(matrix)
    # then we grab the columns
    columns = [row for row in trans]
    # next we use the divider to try to divide the columns
    norm = divider(columns)
    # we check to make sure the norm exists and thereby division was successful
    if norm is None:
        return None
    # if it was we then create a numpy row vector from the norm
    norm = np.array([[element for element in norm]])
    # and we dot it with the original matrix
    positive = np.dot(norm, matrix)
    # finally we shave the error from the positive and return it
    return shave(positive)


def positive_nullspace_vector(matrix, verbose=True):
    """
    positive_nullspace_vector(matrix) - This function takes a matrix and tries to find
    a nullspace vector that has only positive entries. If it finds one it returns that
    vector, if it doesn't it returns None. (The vector is returned as a column vector)
    """
    # first we get the nullspace of the matrix
    N = nullspace(matrix)
    # we check to see if the nullspace is empty
    if N.shape[0] == 0:
        # no positive to be found here
        if verbose: print 'nullspace is empty'
        return None
    # we shave off any error
    N = shave(N)
    # now to generate the positive we need to transpose N, because right not the nullspace vectors
    # are its columns and we need them to be rows for this to work properly
    N = np.transpose(N)
    # now we can try to get the positive for this matrix
    pos = positive(N)
    # we check to see if a positive was found
    if pos is not None:
        # we found it! but it's gonna be a row vectors and nullspace vectors should be columns
        # so we'll transpose it before we send it on its merry way
        pos = np.transpose(pos)
        if verbose: print 'positive found'
        return pos
    else:
        # in this case no positive was found
        if verbose: print 'no positive found'
        return None
