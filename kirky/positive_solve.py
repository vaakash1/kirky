from sklearn.svm import LinearSVC
from issue import Issue


def reflect(_list):
    return [-a for a in _list]


def dot(vector1, vector2):
    return sum([vector1[i] * vector2[i] for i in range(len(vector1))])


class Divider(object):

    def __init__(self):
        self.vectors= []
        self.training_data = []
        self.classifications = []
        self.svm = LinearSVC(loss='hinge')

    def add(self, vector):
        self.vectors.append(vector)

    def _prepare(self):
        num_vectors = len(self.vectors)
        self.training_data = [vector for vector in self.vectors] + [reflect(vector) for vector in self.vectors]
        self.classifications = [0] * num_vectors + [1] * num_vectors

    def _fit(self):
        self.svm.fit(self.training_data, self.classifications)

    def _try(self):
        norm = self.svm._coef
        product = 0
        i = 0
        while product == 0:
            product = dot(norm, self.vectors[i])
            i += 1
        if product < 0:
            norm = reflect(norm)
        for vector in self.vectors:
            if dot(norm, vector) < 0:
                return False
        return True

    def divide(self):
        self._prepare()
        self._fit()
        if not self._try():
            raise Issue('vectors cannot be divided')
        else:
            return self.svm._coef


def positive(matrix):
    num_columns = matrix.shape[1]
    divider = Divider()
    for i in range(num_columns):
        divider.add(matrix[,i])
    try:
        norm = divider.divide()
    except Issue:
        raise Issue('no positive exists for this matrix')
    return norm * matrix

