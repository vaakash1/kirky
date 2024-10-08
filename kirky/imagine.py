import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as pe
from matplotlib.widgets import Button,Slider
import time

def draw_graph(k, x, y):    

    # transformation matrix for projecting from n-dimensional space to 2D
    transformation_matrix = np.array([x, y])
        
    # constants
    LABEL_POSITION = 0.618
    SPACE_OFFSET = 0.02
    TEXT_OFFSET = 0.025
    HEAD_SIZE = 5

    
    vectors = []
    vector_text = []
    vector_text_positions = []
    
    for edge in k.frame.edges:
        if edge.weight != 0:
            # project coordinates
            head_vertex = np.dot(transformation_matrix, edge.head.position)
            tail_vertex = np.dot(transformation_matrix, edge.tail.position)
            
            # compute coordinates
            vector = head_vertex - tail_vertex
            normalized = vector / np.linalg.norm(vector)
            tail_position = tail_vertex + SPACE_OFFSET * normalized
            components = vector - 2 * SPACE_OFFSET * normalized
            text_position = np.subtract(tail_vertex + vector * LABEL_POSITION, TEXT_OFFSET)
            
            # store the information
            vectors.append((tail_position[0], tail_position[1], components[0], components[1]))
            vector_text.append(f'{edge.weight}, {edge.id + 1}')
            vector_text_positions.append((text_position[0], text_position[1]))
    
    # retrieve the vertices
    vertices = [np.dot(transformation_matrix, vertex.position) for vertex in k.frame.vertices.values() if vertex.is_connected()]
    print(vertices)
    verticesX, verticesY = zip(*vertices)


    
    # draw everything
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.quiver(*zip(*vectors), angles='xy', scale_units='xy', scale=1, width=0.003, color='black', headwidth = HEAD_SIZE, headlength = HEAD_SIZE, headaxislength = HEAD_SIZE)
    ax.scatter(verticesX, verticesY, color='blue')
    ax.set_xticks(np.arange(min(verticesX), max(verticesX) + 1, 1))
    ax.set_yticks(np.arange(min(verticesY), max(verticesY) + 1, 1))
    for i, text in enumerate(vector_text):
        ax.text(vector_text_positions[i][0], vector_text_positions[i][1], text, color='black', fontsize=8, fontweight='bold', fontname='Arial', path_effects=[pe.withStroke(linewidth=6, foreground="white")])
    
    plt.show()
def draw_graph_slider(k, x, y):
    
    # transformation matrix for projecting from n-dimensional space to 2D
    transformation_matrix = np.array([x, y])
        
    # constants
    LABEL_POSITION = 0.618
    SPACE_OFFSET = 0.05
    TEXT_OFFSET = 0.025
    HEAD_SIZE = 5

    
    vectors = []
    vector_text = []
    vector_text_positions = []
    
    for edge in k.frame.edges:
        if edge.weight != 0:
            # project coordinates
            head_vertex = np.dot(transformation_matrix, edge.head.position)
            tail_vertex = np.dot(transformation_matrix, edge.tail.position)
            
            # compute coordinates
            vector = head_vertex - tail_vertex
            normalized = vector / np.linalg.norm(vector)
            tail_position = tail_vertex + SPACE_OFFSET * normalized
            components = vector - 2 * SPACE_OFFSET * normalized
            text_position = np.subtract(tail_vertex + vector * LABEL_POSITION, TEXT_OFFSET)
            
            # store the information
            vectors.append((tail_position[0], tail_position[1], components[0], components[1]))
            vector_text.append(f'{edge.weight}, {edge.id + 1}')
            vector_text_positions.append((text_position[0], text_position[1]))
    
    # retrieve the vertices
    vertices = [np.dot(transformation_matrix, vertex.position) for vertex in k.frame.vertices.values() if vertex.is_connected()]
    print(vertices)
    verticesX, verticesY = zip(*vertices)


    
    # draw everything
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.quiver(*zip(*vectors), angles='xy', scale_units='xy', scale=1, width=0.003, color='black', headwidth = HEAD_SIZE, headlength = HEAD_SIZE, headaxislength = HEAD_SIZE)
    ax.scatter(verticesX, verticesY, color='blue')
    ax.set_xticks(np.arange(np.floor(min(verticesX)), np.ceil(max(verticesX)) + 1, 1))
    ax.set_yticks(np.arange(min(verticesY), max(verticesY) + 1, 1))
    for i, text in enumerate(vector_text):
        ax.text(vector_text_positions[i][0], vector_text_positions[i][1], text, color='black', fontsize=8, fontweight='bold', fontname='Arial', path_effects=[pe.withStroke(linewidth=6, foreground="white")])
    num_dims = k.dimensions
    num_sliders = num_dims - 2
    initial_angles = np.linspace(0, np.pi, num_dims)
    initial_angles = initial_angles[1 : ]
    # make a list of sliders, each corresponding to a dimension
    sliders = []
    for i in range(num_sliders):
        axslider = fig.add_axes([0.25, 0.1 + 0.03 * i, 0.65, 0.03])
        slider = Slider(
            ax=axslider,
            label=f'Angle {i + 1}',
            valmin=0,
            valmax=2 * np.pi,
            valinit=initial_angles[i]
        )
        sliders.append(slider)
    # calculate how much to adjust the subplot to make room for the sliders
    fig.subplots_adjust(bottom=0.25 + 0.03 * num_sliders)
    def update(val):
        time.sleep(0.05)
        angles = [0, np.pi / 2] + [slider.val for slider in sliders]
        transformation_matrix = np.array([[np.cos(angle) for angle in angles], [np.sin(angle) for angle in angles]])
        print(np.round(transformation_matrix, decimals=2))
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.clear()
        vectors = []
        vector_text = []
        vector_text_positions = []
        for edge in k.frame.edges:
            if edge.weight != 0:
                # project coordinates
                head_vertex = np.dot(transformation_matrix, edge.head.position)
                tail_vertex = np.dot(transformation_matrix, edge.tail.position)
                
                # compute coordinates
                vector = head_vertex - tail_vertex
                normalized = vector / np.linalg.norm(vector)
                tail_position = tail_vertex + SPACE_OFFSET * normalized
                components = vector - 2 * SPACE_OFFSET * normalized
                text_position = np.subtract(tail_vertex + vector * LABEL_POSITION, TEXT_OFFSET)
                
                # store the information
                vectors.append((tail_position[0], tail_position[1], components[0], components[1]))
                vector_text.append(f'{edge.weight}, {edge.id + 1}')
                vector_text_positions.append((text_position[0], text_position[1]))
        # retrieve the vertices
        vertices = [np.dot(transformation_matrix, vertex.position) for vertex in k.frame.vertices.values() if vertex.is_connected()]
        verticesX, verticesY = zip(*vertices)
        ax.quiver(*zip(*vectors), angles='xy', scale_units='xy', scale=1, width=0.003, color='black', headwidth = HEAD_SIZE, headlength = HEAD_SIZE, headaxislength = HEAD_SIZE)
        ax.scatter(verticesX, verticesY, color='blue')
        ax.set_xticks(np.arange(np.floor(min(verticesX)), np.ceil(max(verticesX)) + 1, 1))
        ax.set_yticks(np.arange(min(verticesY), max(verticesY) + 1, 1))
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        for i, text in enumerate(vector_text):
            ax.text(vector_text_positions[i][0], vector_text_positions[i][1], text, color='black', fontsize=8, fontweight='bold', fontname='Arial', path_effects=[pe.withStroke(linewidth=6, foreground="white")])
        plt.show()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
    for slider in sliders:
        slider.on_changed(update)
    plt.show()
    
def draw3d(k):
	plt.clf()
	print("The current plt figure number is", plt.gcf().number)
	edges = list(k.frame.edges)
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
	ax.quiver(X, Y, Z, U, V, W, arrow_length_ratio=0.1, pivot='tail', color='blue')
	for i, edge in enumerate(edges):
		ax.text(text_coordinates[i][0], text_coordinates[i][1], text_coordinates[i][2], f'{int(edge.weight)}', color='black', fontsize=10, fontweight='bold', fontname='Arial')
	ax.scatter(X, Y, Z, color='brown')
	ax.set_xticks(np.arange(min(X), max(X)+1, 1))
	ax.set_yticks(np.arange(min(Y), max(Y)+1, 1))
	ax.set_zticks(np.arange(min(Z), max(Z)+1, 1))
	plt.show()
	plt.close()
