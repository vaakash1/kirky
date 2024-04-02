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
		weight = int(edge.weight)
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
				edge_labels[(tail_id, head_id)] = '%s' % (int(weight))
			elif weight < 0:
				weighted_edges.append((head_id, tail_id, weight))
				edge_labels[(head_id, tail_id)] = '%s' % (int(-weight))
	DG = nx.DiGraph()
	DG.add_weighted_edges_from(weighted_edges)
	return DG, edge_labels


def draw(k, file_path, x=[1, 0], y=[0, 1]):
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
	nodes = nx.draw_networkx_edge_labels(graph, pos=projected_vertices, font_size=12,
										 edge_labels=edge_labels, label_pos=0.38)
	plt.scatter(projected_vertices[:, 0], projected_vertices[:, 1], color='blue', s=100)
	plt.savefig(file_path)

def draw3d(k, file_path):
	edges = list(k.frame.coordinate_vectors) + list(k.frame.cross_vectors)
	edges = [edge for edge in edges if edge.weight != 0]
	tail_coordinates = [[int(coord) for coord in edge.tail] for edge in edges]
	head_coordinates = [[int(coord) for coord in edge.head] for edge in edges]
	text_coordinates = np.divide(np.add(tail_coordinates, head_coordinates), 2)
	edge_components = np.subtract(head_coordinates, tail_coordinates)
	X, Y, Z= zip(*(tail_coordinates))
	U, V, W = zip(*edge_components)
	x_lim = [min(X+U), max(X+U)]
	y_lim = (min(Y+V), max(Y+V))
	z_lim = (min(Z+W), max(Z+W))
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.set_xlim(x_lim)
	ax.set_ylim(y_lim)
	ax.set_zlim(z_lim)
	ax.quiver(X, Y, Z, U, V, W, arrow_length_ratio=0.1, pivot='tail', color='brown')
	for i, edge in enumerate(edges):
		ax.text(text_coordinates[i][0], text_coordinates[i][1], text_coordinates[i][2], f'{int(edge.weight)}', color='black', fontsize=10, fontweight='bold', fontname='Arial')
	ax.scatter(X, Y, Z, color='blue')
	ax.set_xticks(np.arange(min(X), max(X)+1, 1))
	ax.set_yticks(np.arange(min(Y), max(Y)+1, 1))
	ax.set_zticks(np.arange(min(Z), max(Z)+1, 1))
	plt.savefig(file_path, format='png')
	plt.show()
	plt.close()