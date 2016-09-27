from fractions import Fraction


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
        for i in range(len(A)):
            constraint_vector = [e for e in A[i][:]]
            self.constraint_vectors.append(constraint_vector)
            self.constraint_values.append(b[i])
        # and finally find the basis
        self.basis = []
        self.find_basis()
        self.pivot_column = None
        self.pivot_row = None
        self.find_pivot()
        self.solution = []

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

    def get_solution(self):
        self.solution = []
        i = 0
        for element in self.constraint_values:
            if i in self.basis:
                self.solution.append(element)
            else:
                if self.exact:
                    self.solution.append(Fraction(0,1))
                else:
                    self.solution.append(0.0)
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


class Simplex(object):

    def __init__(self, c, d, A, b, exact=False):
        self.c = c
        self.A = A
        self.d = d
        self.b = b
        self.exact = exact
        self.is_feasible = True
        self.solution = None
        self.unbounded = None

    def create_auxilary_tableau(self):
        j = len(self.A[0])
        aux_A = []
        if self.exact:
            one = Fraction(1,1)
            zero = Fraction(0,1)
        else:
            one = 1.0
            zero = 0.0
        for i in range(len(self.A)):
            if self.b[i] < 0:
                row = [-e for e in self.A[i][:]] + [zero] * len(self.A)
            else:
                row = [e for e in self.A[i][:]] + [zero] * len(self.A)
            row[j] = one
            aux_A.append(row)
            j += 1
        aux_c = []
        for j in range(len(self.A[0])):
            total = 0.0
            for i in range(len(self.A)):
                if self.b[i] < 0:
                    total -= self.A[i][j]
                else:
                    total += self.A[i][j]
            aux_c.append(total)
        aux_d = -1 * sum([abs(e) for e in self.b])
        aux_b = [abs(e) for e in self.b]
        return Tableau(aux_c, aux_d, aux_A, aux_b)

    def run(self, tableau):
        while not tableau.is_unbounded() and not tableau.is_solved():
            tableau.pivot()

    def prep(self):
        aux_tableau = self.create_auxilary_tableau()
        self.run(aux_tableau)
        # now we check to see if there is a feasible solution
        if aux_tableau.objective_value == 0.0:
            self.is_feasible = True
            self.solution = aux_tableau.solution[:len(self.A[0])]
            new_A = []
            for i in range(len(self.A)):
                row = aux_tableau.constraint_vectors[i][:len(self.A[0])]
                new_A.append(row)
            new_b = aux_tableau.constraint_values
            self.A = new_A
            self.b = new_b
        else:
            self.is_feasible = False

    def solve(self):
        if not self.is_feasible:
            return None
        tableau = Tableau(self.c, self.d, self.A, self.b)
        self.run(tableau)
        if tableau.is_unbounded():
            self.unbounded = True
        else:
            self.unbounded = False






