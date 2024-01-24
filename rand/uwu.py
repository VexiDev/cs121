# Let's first define the adjacency list for each vertex based on the given graph G.
# This will allow us to reason about the number of walks of length 2 and 3.
import numpy as np
adjacency_list = {
    'v1': ['v2', 'v3'],
    'v2': ['v1', 'v3'],
    'v3': ['v1', 'v2', 'v4'],
    'v4': ['v3', 'v5'],
    'v5': ['v4']
}

# We map vertex labels to indices (0-based)
vertex_indices = {vertex: index for index, vertex in enumerate(adjacency_list)}

# Initialize matrices for A^2 and A^3 with zeros
A_squared = np.zeros((5, 5), dtype=int)
A_cubed = np.zeros((5, 5), dtype=int)

# Helper function to find common neighbors
def common_neighbors(v1, v2):
    return len(set(adjacency_list[v1]).intersection(adjacency_list[v2]))

# Compute A^2
for i in adjacency_list:
    for j in adjacency_list:
        if i == j:
            # Diagonal entries are the sum of 2-step paths from i to each of its neighbors and back
            A_squared[vertex_indices[i], vertex_indices[j]] = sum(common_neighbors(i, k) for k in adjacency_list[i])
        else:
            # Off-diagonal entries are the direct common neighbors
            A_squared[vertex_indices[i], vertex_indices[j]] = common_neighbors(i, j)

# Compute A^3 by checking all 3-step paths that go through an intermediate vertex k
for i in adjacency_list:
    for j in adjacency_list:
        for k in adjacency_list:
            if k != i and k != j:
                A_cubed[vertex_indices[i], vertex_indices[j]] += common_neighbors(i, k) * common_neighbors(k, j)

print(A_squared, "\n\n",A_cubed)
