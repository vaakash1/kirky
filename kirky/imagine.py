import numpy as np
import networkx as nx
from sklearn.decomposition import PCA
from collections import defaultdict
import matplotlib.pyplot as plt


class Indexer(object):

	def __init__(self):
		self.id = 0

	def __call__(self):
		self.id += 1
		return self.id - 1


def create_tables(edges):
	vertices = defaultdict(Indexer())
	adjacencies_dict = defaultdict(dict)
	for edge in edges:
		head = tuple([float(e) for e in edge.head])
		tail = tuple([float(e) for e in edge.tail])
		weight = float(edge.weight)
		if weight != 0:
			head_id = vertices[head]
			tail_id = vertices[tail]
			adjacencies_dict[tail_id][head_id] = weight
			adjacencies_dict[head_id][tail_id] = -weight
	vertices_list = [tuple()] * len(vertices)
	for vertex, index in vertices.items():
		vertices_list[index] = vertex
	vertices = np.asarray(vertices_list)
	adjacencies = np.zeros((len(vertices_list), len(vertices_list)))
	for tail_id, _dict in adjacencies_dict.items():
		for head_id, weight in _dict.items():
			adjacencies[tail_id][head_id] = weight
	return vertices, adjacencies


def pca_projection(vertices):
	pca = PCA(n_components=2)
	vertices = pca.fit_transform(vertices)
	return vertices, pca


def build_nx_graph(adjacencies):
	weighted_edges = []
	weights = {}
	for tail_id in range(adjacencies.shape[0]):
		for head_id in range(tail_id):
			weight = adjacencies[tail_id][head_id]
			if weight > 0:
				weighted_edges.append((tail_id, head_id, weight))
				weights[(tail_id, head_id)] = weight
			elif weight < 0:
				weighted_edges.append((head_id, tail_id, weight))
				weights[(head_id, tail_id)] = -weight
	DG = nx.DiGraph()
	DG.add_weighted_edges_from(weighted_edges)
	return DG, weights


def draw(k, file_path):
	edges = list(k.frame.coordinate_vectors) + list(k.frame.cross_vectors)
	vertices, adjacencies = create_tables(edges)
	projected_vertices, _ = pca_projection(vertices)
	graph, weights = build_nx_graph(adjacencies)
	plt.clf()
	plt.figure()
	x = nx.draw_networkx_edges(graph, pos=projected_vertices)
	nodes = nx.draw_networkx_edge_labels(graph, pos=projected_vertices,
										 edge_labels=weights)
	plt.savefig(file_path)
