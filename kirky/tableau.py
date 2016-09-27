def add_vectors(v1, v2):
    i = 0
    result = []
    for e1 in v1:
        e2 = v2[i]
        result.append(e1 + e2)
        i += 1
    return result


class Tableau(object):

    def __init__(self, c, d, A, b, exact=False):
        self.exact = exact
        # setup the object vector (first row of tableau as written)
        self.objective_vector = [-e for e in c]
        # get the objective value (to make the matrix augmented)
        self.objective_value = [d]
        # setup the constraint vectors as values
        self.constraint_vectors = []
        self.constraint_values = []
        # we will find the pivot row while we are at it
        for i in range(A.shape[0]):
            constraint_vector = [e for e in A[i, :]]
            self.constraint_vectors.append(constraint_vector)
            self.constraint_values.append(b[i])
        # and finally find the basis
        self.basis = []
        self.find_basis()
        self.pivot_column = None
        self.pivot_row = None
        self.find_pivot()

    def find_basis(self, given=None):
        if given:
            self.basis = [given]
        else:
            self.basis = []
        for j in range(len(self.objective_vector)):
            if len(self.basis) == len(self.constraint_vectors):
                break
            if j == given:
                continue
            found_one = False
            just_one = True
            for i in range(len(self.constraint_vectors)):
                if self.constraint_vectors[i][j] == 1:
                    if not found_one:
                        found_one = True
                    else:
                        just_one = False
            if just_one:
                self.basis.append(j)

    def find_pivot(self):
        self.pivot_column = None
        i = 0
        smallest_value = 1
        for value in self.objective_vector:
            if i in self.basis:
                continue
            if value < 0 and value < smallest_value:
                smallest_value = value
                self.pivot_column = i
                if self.exact:
                    break
            i += 1
        self.pivot_row = None
        if self.pivot_column is None:
            return
        smallest_ratio = 10**16
        i = 0
        for constraint_vector in self.constraint_vectors:
            constraint_value = self.constraint_values[i]
            column_value = constraint_vector[self.pivot_column]
            if column_value < 0:
                continue
            ratio = constraint_value / column_value
            if ratio < smallest_ratio:
                smallest_ratio = ratio
                self.pivot_row = i
            i += 1

    def is_solved(self):
        if self.pivot_column is None and self.pivot_row is None:
            return True
        return False

    def is_unbounded(self):
        if self.pivot_column is not None and self.pivot_row is None:
            return True
        return False

    def pivot(self):
        divisor = self.constraint_vectors[self.pivot_row][self.pivot_column]
        pivot_vector = [e / divisor for e in self.constraint_vectors[self.pivot_row]]
        self.constraint_vectors[self.pivot_row] = pivot_vector
        pivot_value = self.constraint_values[self.pivot_row] / divisor
        self.constraint_values[self.pivot_row] = pivot_value
        for i in range(len(self.constraint_vectors)):
            vector = self.constraint_vectors[i]
            if vector == pivot_vector:
                continue
            coefficient = -1 * vector[self.pivot_column]
            adjustment_vector = [e * coefficient for e in pivot_vector]
            new_vector = add_vectors(vector, adjustment_vector)
            self.constraint_vectors[i] = new_vector
            self.constraint_values[i] += pivot_value * coefficient
        coefficient = -1 * self.objective_vector[self.pivot_column]
        adjustment_vector = [e * coefficient for e in pivot_vector]
        self.objective_vector = add_vectors(self.objective_vector, adjustment_vector)
        self.objective_value += pivot_value * coefficient
        # last but not least we find the new basis and pivot
        self.find_basis(self.pivot_column)
        self.find_pivot()



