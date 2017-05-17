from fractions import Fraction


class Tableau(object):

    def __init__(self, objective_vector, objective_value, constraint_matrix, constraint_values):
        """
        Input:
            objective_vector - a list representing your objective vector
            objective_value - a number
            constraint_matrix - a matrix like object containing your constraints
            constraint_values - the values corresponding to each of your constraint rows (right hand side
                    of the matrix equation Ax=b)

        NOTES:
            (a) setup the objective vector (first row in a written tableau)
            (b) setup the constraint rows. These rows are the original rows from the constraint matrix
                augmented by the corresponding constraint value
            (c) find the basis of our current tableau (it's assumed there is one)
            (d) make sure the objective vector reflects the basis
            (e) find the first pivot
            (f) we initialize the solution to None so that we can indicate whether the tableau has been
                solved at any point in time
        """
        self.objective_row = list(objective_vector) + [-objective_value]                                # (a)
        self.constraint_rows = []                                                                       # (b)
        for i in range(len(constraint_matrix)):
            constraint_vector = [e for e in constraint_matrix[i][:]] + [constraint_values[i]]
            self.constraint_rows.append(constraint_vector)
        self.basis_dict = {}                                                                            # (c)
        self.find_basis()
        self.prepare()                                                                                  # (d)
        self.pivot_column_index = None                                                                  # (e)
        self.pivot_row = None
        self.pivot_row_index = None
        self.find_pivot()
        self.solution = None                                                                            # (f)

    def find_pivot(self):
        """
        This method finds the new pivot row and pivot column and sets the pivot_row, pivot_row_index, and
        and pivot_column_index attributes of this class to reflect that.

        IMPORTANT: If after calling find_pivot self.pivot_row, self.pivot_row_index, and self.pivot_column_index
        are None, then no new pivot was found.

        NOTES:
            (a) we set the two attributes to None to begin with. If they stay like this it indicates
                that there was no new pivot
            (b) for our pivot column we choose the first negative value in the objective row (ignoring
                of course the augmented portion at the end of this row **
            (c) if we found a pivot column we move on to grab the pivot row
            (d) a pivot row must have a positive value at the pivot column index **
            (e) if we have no candidate rows then we simply return, this will leave pivot_row as
                None
            (f) from the candidate rows we choose the row that has the smallest ratio between the last
                value in the row (the augmented portion) and the value at the pivot column index. If
                two rows have this smallest ratio we select the one with the smaller value at the
                pivot column index. The rest of the code in this method implements this choice. **

        ** These choices come from Bland's rule https://en.wikipedia.org/wiki/Bland%27s_rule
        """
        self.pivot_row = None                                                                           # (a)
        self.pivot_row_index = None
        self.pivot_column_index = None
        for i in range(len(self.objective_row) - 1):                                                    # (b)
            if self.objective_row[i] < 0:
                self.pivot_column_index = i
                break
        if self.pivot_column_index is not None:                                                         # (c)
            candidate_rows = [(self.constraint_rows[i], i) for i in range(len(self.constraint_rows))    # (d)
                              if self.constraint_rows[i][self.pivot_column_index] > 0]
            if len(candidate_rows) == 0:                                                                # (e)
                return
            self.pivot_row, self.pivot_row_index = candidate_rows[0]                                    # (f)
            current_ratio = self.pivot_row[-1] / self.pivot_row[self.pivot_column_index]
            for row, index in candidate_rows[1:]:
                new_ratio = row[-1] / row[self.pivot_column_index]
                if new_ratio < current_ratio or \
                        (new_ratio == current_ratio and
                         row[self.pivot_column_index] < self.pivot_row[self.pivot_column_index]):
                    self.pivot_row = row
                    self.pivot_row_index = index
                    current_ratio = new_ratio

    def pivot(self):
        """
        This method performs the pivot operation for the tableau given the current pivot row and
        column. It will then call find_pivot to update the pivot for you.

        NOTES:
            (a) we get the value at the pivot column in the pivot row to be one
            (b) we set this new pivot row into the constraint_rows
            (c) we zero out the pivot column in all of the other constraint_rows
            (d) we zero out the pivot column in the objective row as well
            (e) find the new pivot
        """
        pivot_element = self.pivot_row[self.pivot_column_index]                                         # (a)
        self.pivot_row = [element / pivot_element for element in self.pivot_row]
        self.constraint_rows[self.pivot_row_index] = self.pivot_row                                     # (b)
        for i in range(len(self.constraint_rows)):                                                      # (c)
            if not i == self.pivot_row_index:
                old_row = self.constraint_rows[i]
                coefficient = old_row[self.pivot_column_index] / self.pivot_row[self.pivot_column_index]
                self.constraint_rows[i] = [old_row[k] - coefficient * self.pivot_row[k]
                                           for k in range(len(old_row))]
        coefficient = (self.objective_row[self.pivot_column_index] /                                    # (d)
                       self.pivot_row[self.pivot_column_index])
        self.objective_row = [self.objective_row[k] - coefficient * self.pivot_row[k]
                              for k in range(len(self.objective_row))]
        self.find_pivot()                                                                               # (e)

    def find_basis(self):
        """
        Given that our constraint rows are like the following:

        [ 1 0 4 0 | 2 ]
        [ 0 1 2 0 | 8 ]
        [ 0 0 1 1 | 2 ]

        we want to grab the basis of our current tableau by finding the columns in which we
        have all zeroes besides a single one. We also want to know in which row the one occurs
        so that we can use this basis to find the solution to our problem (as defined in the
        simplex method).

        Therefore this function sets the self.basis_dict to have as keys the columns indices we
        are looking for and as values the corresponding row index in which the one exists within
        that column.

        NOTES:
            (a) we begin by setting our basis_dict to consider all columns (except the final
                augmented column of course) and set the row index to None because we do not
                know where the one exists if the column is good at all.
            (b) for each row we will march through the columns that are still candidates and
                determine which remain candidates and which go
            (c) we grab the current value for the row index that holds the one because depending
                on whether this is None or not, we have to handle the question of keeping this
                column differently
            (d) if we do not have a row index for this column yet and we just found a one than
                if this is a good column this is our one and only one, so we set the row index
            (e) if we didn't just set the row index (by finding the first one) then anything
                besides a zero means that this column is no good. So we remove it from the
                candidates in basis_dict
        """
        self.basis_dict = {i: None for i in range(len(self.objective_row) - 1)}                         # (a)
        for i in range(len(self.constraint_rows)):
            row = self.constraint_rows[i]
            current_columns = self.basis_dict.keys()                                                    # (b)
            for column in current_columns:
                row_with_one = self.basis_dict[column]                                                  # (c)
                if row_with_one is None and row[column] == 1:
                    self.basis_dict[column] = i                                                         # (d)
                elif row[column] != 0:
                    del self.basis_dict[column]                                                         # (e)

    def is_solved(self):
        """
        A tableau is solved when we did not find a pivot at all.
        """
        if self.pivot_column_index is None and self.pivot_row is None:
            return True
        return False

    def is_unbounded(self):
        """
        A tableau is unbounded (i.e. has no solution) when we can find a pivot column but
        no pivot row.
        """
        if self.pivot_column_index is not None and self.pivot_row is None:
            return True
        return False

    def prepare(self):
        """
        At the beginning of a problem the objective vector may not reflect the basis that
        we have chosen. I.e. the objective vector does not have zeroes at the basis columns.
        So this is just a preparatory step to ensure that is the case before we get started
        solving the tableau.
        """
        for column, row_with_one in self.basis_dict.iteritems():
            coefficient = self.objective_row[column]
            self.objective_row = [self.objective_row[i] - coefficient * self.constraint_rows[row_with_one][i]
                                  for i in range(len(self.objective_row))]

    def get_solution(self):
        """
        This function calls find_basis() and then grabs the solution vector (as a list) using that
        information.

        Once the basis is known, finding the solution is incredibly easy. It is a vector of the same
        length as all the rows in our tableau (minus the augmented portion) containing
        zeroes everywhere but the basis columns. And for these basis columns the value is simply the
        augmented portion (last element) of the row having the 1 for that basis column.

        NOTES:
            (a) make sure the basis is fresh
            (b) by getting zero this way, we ensure it keeps the type that was input into the
                tableau in the first place
            (c) easiest to just make a vector of zeroes and then just change the appropriate
                columns afterwards
            (d) setting the nonzero parts of the solution
        """
        self.find_basis()                                                                               # (a)
        zero = self.objective_row[0] - self.objective_row[0]                                            # (b)
        self.solution = [zero] * (len(self.objective_row) - 1)                                          # (c)
        for column, row_with_one in self.basis_dict.iteritems():                                        # (d)
            self.solution[column] = self.constraint_rows[row_with_one][-1]

    def solve(self):
        """
        This method calls pivot until either a solution has been found or the problem is determined
        to be unbounded. It returns True in the first case and False in the second
        """
        while not self.is_solved() and not self.is_unbounded():
            self.pivot()
        return self.is_solved()


def solve_kirky(E):
    """
    Inputs:
        E - the matrix corresponding to the conditions the frame vector weights must satisfy in
            order to be Kirchhoff. Note that it does not contain the conditions for those
            weights to be positive or their sum to be greater than one.

    Outputs:
        if there is no solution the output is None. If there is a solution that solution is returned
        as a list

    In this function our aim is to take these constraints, add our conditions for
    nontrivial weights and then setup a phase I simplex step which we then try to solve. (Note that
    simply by this being simplex our weights will be guaranteed to be positive).

    NOTES:
        (a) we create the condition for our weights to have a positive sum.
        (b) in taking the above step we added in an addition variable to our problem so we have
            to add a new row (all zeroes) to E
        (c) we add our sum condition row to E
        (d) the right hand side of the equation Ex=b is now going to be all zeroes except for the last
            value which will be our sum_condition value. So we create that vector now as it will be needed
            for the simplex method
        (e) now we setup our phase I tableau. This tableau adds as many auxiliary variables as we have rows
            to form a basis that our simplex method will then try to zero out. To see what we are doing in
            the next few lines refer to:
        (f) we form the objective function for this phase I step
        (g) we form the objective value for this phase I step
        (h) create the Tableau given all of this information
        (i) the failure conditions for this phase I step are that we simply cannot solve the tableau
            or that the objective_value once solved (which is the last row in the augmented objective
            vector the tableau has created) is not zero.
        (j) the solution will contain all those extra variables we created, but because we don't care
            about them we just throw them away.
    """
    num_weights = len(E[0])
    sum_condition_row = [Fraction(1)] * num_weights + [Fraction(-1)]                                # (a)
    sum_condition_value = Fraction(1)
    for row in E:                                                                                   # (b)
        row.append(Fraction(0))
    E.append(sum_condition_row)                                                                     # (c)
    b = [Fraction(0)] * (len(E) - 1) + [sum_condition_value]                                        # (d)
    num_auxiliary_variables = len(E)                                                                # (e)
    i = 0
    for row in E:
        addition = [Fraction(0)] * num_auxiliary_variables
        addition[i] = Fraction(1)
        row.extend(addition)
        i += 1
    objective_vector = [Fraction(0)] * (len(E[0]) - num_auxiliary_variables) + \
        [Fraction(1)] * num_auxiliary_variables                                                     # (f)
    objective_value = Fraction(0)                                                                   # (g)
    tableau = Tableau(objective_vector, objective_value, E, b)                                      # (h)
    if not tableau.solve() or tableau.objective_row[-1] != 0:
        return None
    else:
        return tableau.solution[:num_weights]                                                       # (j)
