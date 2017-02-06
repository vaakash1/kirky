from fractions import Fraction

class Row(object):

    def __init__(self, iterable):
        self.contents = [element for element in iterable]
        self.content_type = self.contents[0].__class__

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, item):
        return self.contents[item]

    def __add__(self, other):
        return Row([self.contents[i] + other.contents[i] for i in range(len(self.contents))])

    def __rmul__(self, other):
        return Row([element * other for element in self.contents])

    def __mul__(self, other):
        return Row([element * other for element in self.contents])

    def __div__(self, other):
        return Row([element / other for element in self.contents])

    def __eq__(self, other):
        for i in range(len(self.contents)):
            if self.contents[i] != other.contents[i]:
                return False
        return True

class DegenerateTableau(object):
    """
    NOTE: during the process of pivoting we will do addition updates only. This means
    that pivot rows in the RDD will not be multiplied by whatever coefficient is
    necessary to cause the pivot column within that row to be 1.
    """

    def __init__(self, c, d, A, b, spark_context):
        # setup the object vector (first row of tableau as written)
        self.objective_row = Row(list(c) + [-d])
        # setup the constraint vectors as values
        self.constraint_rows = []
        # we will find the pivot row while we are at it
        for i in range(len(A)):
            constraint_vector = [e for e in A[i][:]] + [b[i]]
            self.constraint_rows.append(Row(constraint_vector))
        # first we get the type being passed into the rows (for generating a solution later)
        self.element_type = self.constraint_rows[0].content_type
        # now we parallelize the constraint rows
        self.constraint_rows = spark_context.parallelize(self.constraint_rows)
        # and finally find the basis and prepare for action
        self.basis_dict = {}
        self.find_basis()
        self.prepare()
        # we set the pivot attributes to None to start with
        self.pivot_column_index = None
        self.pivot_row = None
        # and then we find the pivot
        self.find_pivot()
        # and now we're ready to go!
        self.solution = None

    def find_pivot(self):
        self.pivot_row = None
        self.pivot_column_index = None
        # first we find the pivot_column which corresponds to the first
        # negative objective value
        for i in range(len(self.objective_row) - 1):
            if self.objective_row[i] < 0:
                self.pivot_column_index = i
                break
        # if we didn't find a pivot column there is no point finding the pivot row
        if self.pivot_column_index is None:
            return
        # next we look for our pivot row
        # we will only consider rows that have a positive value in this column
        # NOTE we have to place the pivot_column_index in a local variable so we don't
        # send the whole Tableau class to spark
        pivot_column_index = self.pivot_column_index
        candidate_rows = self.constraint_rows.filter(lambda row: row[pivot_column_index] > 0)
        # if we have no candidate rows we return with self.pivot_row still set to None
        if candidate_rows.count() == 0:
            return

        # then we choose the row that would has the smallest ratio of last element (augmented portion of
        # the row over the pivot column value for this row

        def select_by_ratio(row1, row2):
            ratio1 = row1[-1] / row1[pivot_column_index]
            ratio2 = row2[-1] / row2[pivot_column_index]
            if ratio1 < ratio2:
                return row1
            elif ratio1 > ratio2:
                return row2
            elif row1[pivot_column_index] < row2[pivot_column_index]:
                return row1
            else:
                return row2

        self.pivot_row = candidate_rows.reduce(select_by_ratio)

    def pivot(self):
        # we will use the following function to update the constraint rows
        pivot_row = self.pivot_row
        pivot_column_index = self.pivot_column_index
        def update(row):
            # this function will zero out the pivot column in any rows beside the pivot row
            # and will rescale the pivot row so the element in the pivot column is one
            if row == pivot_row:
                return row / row[pivot_column_index]
            else:
                pivot_row_coefficient = -1 * row[pivot_column_index] / pivot_row[pivot_column_index]
                return row + pivot_row_coefficient * pivot_row

        self.constraint_rows = self.constraint_rows.map(lambda row: update(row))
        # next we use the pivot row to zero out the pivot column in the objective
        pivot_row_coefficient = -1 * self.objective_row[self.pivot_column_index] / self.pivot_row[self.pivot_column_index]
        self.objective_row += pivot_row_coefficient * self.pivot_row
        # now we go ahead and update the pivot
        self.find_pivot()

    def find_basis(self, given=None):
        # we want to form a pairing between the rows of our contraints and the corresponding
        # basis column in each one
        # [ 1 0 4 0 | 2 ]
        # [ 0 1 2 0 | 8 ]
        # [ 0 0 1 1 | 2 ]
        # in this case we'd have the pairings
        # row - column
        #  0  -   0
        #  1  -   1
        #  2  -   3
        # this basis will be used to generate a solution in the future

        # we will get these pairings by first finding which columns contain only a single 1
        # and then we will do another pass to grab the corresponding rows

        def there_can_only_be_one(row1, row2):
            # this function takes two rows and returns a row filled with elements derived in the following
            # way from the original rows
            # * make the resulting element 0 if both row1 and row2's elements are zero
            # * make the resulting element 1 if row1 xor row2 has a 1 and the other has a zero
            # * make it -1 otherwise
            # this way, when taking over all rows in sequence we will know which columns are basis columns
            # and which aren't
            new_list = []
            for i in range(len(row1)):
                if row1[i] == 0 and row2[i] == 0:
                    new_list.append(0)
                elif (row1[i] == 1 and row2[i] == 0) or (row1[i] == 0 and row2[i] == 1):
                    new_list.append(1)
                else:
                    new_list.append(-1)
            return Row(new_list)

        # we use the above function to generate a row that will let us know what columns are part
        # of our basis
        data = self.constraint_rows.reduce(there_can_only_be_one)
        basis_column_indices = []
        for i in range(len(data) - 1):
            # the basis columns are just the columns in our "data" that have a 1
            if data[i] == 1:
                basis_column_indices.append(i)
                if len(basis_column_indices) == self.constraint_rows.count():
                    break

        # okay now that we have our basis columns we can run through our rows to grab the basis rows

        def is_basis_row(row):
            for i in basis_column_indices:
                if row[i] == 1:
                    return True
            return False

        basis_rows = self.constraint_rows.filter(lambda row: is_basis_row(row)).collect()

        self.basis_dict = {}
        # now we finish up by pairing columns to rows
        for i in basis_column_indices:
            for row in basis_rows:
                if row[i] == 1:
                    self.basis_dict[i] = row
                    break

    def is_solved(self):
        if self.pivot_column_index is None and self.pivot_row is None:
            return True
        return False

    def is_unbounded(self):
        if self.pivot_column_index is not None and self.pivot_row is None:
            return True
        return False

    def prepare(self):
        # this just ensures that the basis is reflected in our objective
        # i.e. we're going to zero out the objective columns corresponding to our
        # basis columns
        for i in self.basis_dict:
            coefficient = -1 * self.objective_row[i]
            self.objective_row += coefficient * self.basis_dict[i]

    def get_solution(self):
        # first we update the basis
        self.find_basis()
        # then we setup a list of zeros of the right type
        self.solution = [self.element_type(0)] * (len(self.objective_row) - 1)
        # and finally we grab the non-zero elements of our solution
        for i in self.basis_dict:
            self.solution[i] = self.basis_dict[i][-1]


def solve_kirky(E, spark_context):
    num_weights = len(E[0])
    # we begin by creating the row that will represent the positive sum condition
    sum_condition_row = [Fraction(1)] * num_weights + [Fraction(-1)]
    sum_condition_value = Fraction(1)
    # we now add on the extra column for all the rows of E
    for row in E:
        row.append(Fraction(0))
    # we now augment E with the sum condition row
    E.append(sum_condition_row)
    b = [Fraction(0)] * (len(E) - 1) + [sum_condition_value]
    # now we will use a phase I approach for simplex to find a feasible solution
    # if it exists
    # we begin by adding in our auxiliary variables
    num_auxiliary_variables = len(E)
    i = 0
    for row in E:
        addition = [Fraction(0)] * num_auxiliary_variables
        addition[i] = Fraction(1)
        row.extend(addition)
        i += 1
    # we create our objective function
    c = [Fraction(0)] * (len(E[0]) - num_auxiliary_variables) + [Fraction(1)] * num_auxiliary_variables
    d = Fraction(0)
    # now we solve this phase I step
    tabby = DegenerateTableau(c, d, E, b, spark_context)
    while not tabby.is_solved():
        tabby.pivot()
    if tabby.objective_row[-1] != 0:
        return None
    else:
        tabby.get_solution()
        return tabby.solution[:num_weights]