from sympy import Matrix, Rational
from issue import Issue

class DividerBroken(Exception):

    def __str__(self):
        return 'Divider was broken by input vector'


# this takes a sympy vector (a matrix with either one column or one row) and returns
# a sympy vector that is normal to the vector
def normal(vector):
    # get this in row vector form
    column_vector = False
    if vector.shape[0] != 1:
        column_vector = True
        vector = vector.T
    # find an index with a nonzero value
    index = 0
    for i in range(vector.shape[1]):
        if vector[i] != 0:
            index = i
            break
    # add together all of the first columns - 1 values
    to_negate = sum([Rational(vector[i]) for i in range(vector.shape[1]) if i != index])
    # get what needs to multiply the last element of the vector in order to give to_negate
    multiplier = (-1) * to_negate / Rational(vector[index])
    # throw together the elements of the normal vector
    new_elements = [1] * index + [multiplier] + [1] * (vector.shape[1] - index - 1)
    # return either a column or row vector as appropriate
    if not column_vector:
        return Matrix(new_elements)
    else:
        return Matrix([new_elements])


class Divider(object):

    def __init__(self):
        self.vector = None
        self.norms = []
        self.need_side_select = False

    def add(self, vector):
        vector = self.canonical(vector)
        if sum([element for element in vector]) == 0:
            return
        if not self.norms and not self.vector:
            self.vector = vector
        if not self.norms and self.vector:
            if self.vector == vector:
                return
            elif self.vector == -vector:
                self.need_side_select = True
            else:
                if self.need_side_select:
                    norm = normal(self.vector)
                    if (vector * norm)[0] < 0: norm = -norm
                    self.norms = [norm, norm]
                else:
                    norm1 = normal(self.vector)
                    if (vector * norm1)[0] < 0: norm1 = -norm1
                    norm2 = normal(vector)
                    if (self.vector * norm2)[0] < 0: norm2 = -norm2
                    self.norms = [norm1, norm2]
        else:
            print vector
            first_product = (vector * self.norms[0])[0]
            second_product = (vector * self.norms[1])[0]
            if first_product < 0 and second_product < 0:
                raise DividerBroken()
            elif first_product >= 0 and second_product >= 0:
                return
            new_norm = normal(vector)
            if first_product < 0:
                reference_norm = normal(self.norms[0])
                if (reference_norm * self.norms[1])[0] < 0: reference_norm = -reference_norm
                if (reference_norm * new_norm)[0] < 0: new_norm = -new_norm
                self.norms[0] = new_norm
            else:
                reference_norm = normal(self.norms[1])
                if (reference_norm * self.norms[0])[0] < 0: reference_norm = -reference_norm
                if (reference_norm * new_norm)[0] < 0: new_norm = -new_norm
                self.norms[1] = new_norm

    def canonical(self, vector):
        rows, columns = vector.shape
        if rows != 1 and columns != 1:
            raise Issue('matrix entered into Divider is not a vector!')
        if rows != 1:
            vector = vector.T
        if vector.shape[1] != 2:
            raise Issue('vector entered into Divider does not have exactly 2 elements')
        return vector

