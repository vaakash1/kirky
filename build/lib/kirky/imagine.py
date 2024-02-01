import numpy as np
import networkx as nx
from sklearn.decomposition import PCA
from collections import defaultdict
import matplotlib.pyplot as plt
from tqdm import tqdm


class Indexer(object):

	def __init__(self):
		self.id = 0

	def __call__(self):
		self.id += 1
		return self.id - 1


def create_tables(edges):
	vertices = defaultdict(Indexer())
	adjacencies_dict = defaultdict(dict)
	labels_dict = defaultdict(dict)
	for edge in edges:
		head = tuple([float(e) for e in edge.head])
		tail = tuple([float(e) for e in edge.tail])
		weight = float(edge.weight)
		if weight != 0:
			head_id = vertices[head]
			tail_id = vertices[tail]
			adjacencies_dict[tail_id][head_id] = weight
			adjacencies_dict[head_id][tail_id] = -weight
			labels_dict[tail_id][head_id] = int(edge.id)
			labels_dict[head_id][tail_id] = int(edge.id)
	vertices_list = [tuple()] * len(vertices)
	for vertex, index in vertices.items():
		vertices_list[index] = vertex
	vertices = np.asarray(vertices_list)
	adjacencies = np.zeros((len(vertices_list), len(vertices_list)))
	for tail_id, _dict in adjacencies_dict.items():
		for head_id, weight in _dict.items():
			adjacencies[tail_id][head_id] = weight
	labels = np.zeros((len(vertices_list), len(vertices_list)))
	for tail_id, _dict in labels_dict.items():
		for head_id, weight in _dict.items():
			labels[tail_id][head_id] = weight
	return vertices, adjacencies, labels


def pca_projection(vertices):
	pca = PCA(n_components=2)
	vertices = pca.fit_transform(vertices)
	return vertices, pca


def defined_projection(x, y, vertices):
	y_sqr_norm = np.linalg.norm(y) ** 2
	x_sqr_norm = np.linalg.norm(x) ** 2
	transform = np.asarray([x / x_sqr_norm, y / y_sqr_norm]).T
	return vertices.dot(transform)


def build_nx_graph(adjacencies, labels):
	weighted_edges = []
	edge_labels = {}
	for tail_id in range(adjacencies.shape[0]):
		for head_id in range(tail_id):
			weight = adjacencies[tail_id][head_id]
			label = labels[tail_id][head_id]
			if weight > 0:
				weighted_edges.append((tail_id, head_id, weight))
				edge_labels[(tail_id, head_id)] = 's%s x %s' % (int(label), weight)
			elif weight < 0:
				weighted_edges.append((head_id, tail_id, weight))
				edge_labels[(head_id, tail_id)] = 's%s x %s' % (int(label), -weight)
	DG = nx.DiGraph()
	DG.add_weighted_edges_from(weighted_edges)
	return DG, edge_labels


def draw(k, file_path, x=None, y=None):
	edges = list(k.frame.coordinate_vectors) + list(k.frame.cross_vectors)
	vertices, adjacencies, labels = create_tables(edges)
	if x is None or y is None:
		projected_vertices, _ = pca_projection(vertices)
	else:
		projected_vertices = defined_projection(x, y, vertices)
	graph, edge_labels = build_nx_graph(adjacencies, labels)
	plt.clf()
	plt.figure(figsize=(10,10))
	x = nx.draw_networkx_edges(graph, pos=projected_vertices)
	nodes = nx.draw_networkx_edge_labels(graph, pos=projected_vertices,
										 edge_labels=edge_labels, label_pos=0.2)
	plt.savefig(file_path)
