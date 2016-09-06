from sklearn.svm import LinearSVC
from issue import Issue
from fractions import Fraction


def reflect(_list):
    return [-a for a in _list]


def dot(vector1, vector2):
    return sum([vector1[i] * vector2[i] for i in range(len(vector1))])


class Divider(object):

    def __init__(self, margin=10**-4):
        self.vectors = []
        self.training_data = []
        self.classifications = []
        self.svm = LinearSVC(loss='hinge')
        self.margin = margin

    def add(self, vector):
        self.vectors.append(vector)

    def _create_training_data(self):
        """
        In this step, we take all of our vectors and reflect them. The normal vectors will be one
        group and the reflected vectors will be the second group. We do this because if we can split
        these two groups, then we can find a hyperplane through the origin that divides the space into
        two where all of the input vectors are on one side.
        """
        num_vectors = len(self.vectors)
        # we create the training data from our normal vectors and the reflected vectors
        self.training_data = [vector for vector in self.vectors] + [reflect(vector) for vector in self.vectors]
        # we create their classifications
        self.classifications = [0] * num_vectors + [1] * num_vectors

    def divide(self):
        self._create_training_data()
        self.svm.fit(self.training_data, self.classifications)
        # we get the norm to the plane that our model thinks divides the two sets
        # I know this looks weird, but the coefficients are an array in a list so its weird...
        svm_norm = self.svm.coef_[0].tolist()
        # this is here because we know that we shall be dealing in integers
        norm = [Fraction(element).limit_denominator(int(1.0 / self.margin) - 1) for element in svm_norm]
        print norm
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

