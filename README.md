# Installing Kirky

Installing kirky is as simple as cloning this repo, moving into it, and running:

```bash
python setup.py install
```

# Using Kirky

There are three steps to building and drawing a Kirchhoff graph. 

1. First we must take our matrix of interest and transform it into an [I|B] form. We will use the `B` as the input to our Kirchhoff building process. Now because we require the linear algebra used to be exact we'll need to specify the elements of `B` as python Fraction objects. 
2. Second we instantiate a Kirchhoff object, passing `B` as input and call the `find` method on that object. This will find and build the Kirchhoff graph corresponding to our matrix if one exists.
3. Third, we call draw on the object to get a picture of our new Kirchhoff graph. This draw function will do its best to find a good perspective from which to view the graph but if you want you can specify a projection yourself. (To see this in action see the last example in example.py).

All together this looks like:

```python
"""
To generate the Kirchhoff Graph for the matrix
1 0 2 1
0 1 1 2
"""
matrix = np.array([[Fraction(2),Fraction(1)], [Fraction(1),Fraction(2)]])
k = Kirchhoff(matrix)
k.find()
draw(k, 'drawings/kirchhoff1.png')
``` 

You can see more of these examples in examples.py. You can also run the examples with:

```bash
python example.py
```

### A Few Notes on the Drawings
You'll notice in the drawings that each edge has a label. These labels are composed of two parts. The sN portion tells you which column in your original matrix this edge corresponds to (with 0 being the first). The other portion is the weight of that edge. 

Another thing to be aware of is that as the Kirchhoff graphs get more complex there is no guarantee that some part of them will not be obscured. For example edges could be hidden by other edges or vertices tucked away behind other drawn elements. So it's usually good practice to view the graph from multiple perspectives (see the last example in example.py). Alternatively you can get a complete description of the Kirchhoff graph using the incidence method of your Kirchhoff object.

```python
matrix = np.array([[Fraction(2),Fraction(1)], [Fraction(1),Fraction(2)]])
k = Kirchhoff(matrix)
k.find()
incidence_matrix, label_matrix, positions = k.incidence()
```