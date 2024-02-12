import networkx as nx
from sympy import Matrix, Point, zeros


def add_restriction_from_edge(G, M, edge, d):
    row = []
    diff = edge[0] - edge[1]
    for vertex in G.nodes:
        if vertex == edge[0]:
            for dimension in range(d): row.extend([diff[dimension]])
        elif vertex == edge[1]:
            for dimension in range(d): row.extend([-diff[dimension]])
        else: row.extend(d*[0])
    return Matrix([M,row])
        

def graph_to_rigidity_matrix(G, d = 2):
    M = Matrix()
    for edge in G.edges:
        M = add_restriction_from_edge(G, M, edge, d)

    M = M.rref()[0]
    rank = M.rank()
    while M.rows > rank: M.del_row(rank)

    return M


def rigid_subgraph_from_pinning(M, pins, d = 2):
    if type(pins) is int: pins = [pins]
    assert(len(pins) >= d)

    for pin in pins:
        for dimension in range(d):
            row = zeros(1, M.cols)
            row[d*pin + dimension] = 1
            M = Matrix([M, row])

    N = M.nullspace()
    rigid_subgraph = set(pins)

    for node_index in range(M.cols // d):
        if node_index in pins: continue
        # check if no movement is possible
        if all([all([vec[d*node_index + dimension] == 0 for dimension in range(d)]) for vec in N]):
            rigid_subgraph.add(node_index)

    return rigid_subgraph


def merge_rigid_subgraphs(G, subgraphs, d):
    M = graph_to_rigidity_matrix(G, d)
    dof = M.rank()
    nodes = list(G.nodes)
    node_indices = {}
    for i in range(len(nodes)): node_indices[nodes[i]] = i
    merges = []

    containing_subgraphs = len(nodes) * [set()]
    for subgraph_index in range(len(subgraphs)):
        for node_index in subgraphs[subgraph_index]:
            containing_subgraphs[node_index].add(subgraph_index)

    for subgraph_index in range(len(subgraphs)):
        # find all neighboring subgraphs
        neighbor_subgraphs = set()
        for node_index in subgraphs[subgraph_index]:
            neighbor_subgraphs = neighbor_subgraphs.union(containing_subgraphs[node_index])

        for neighbor_subgraph_index in neighbor_subgraphs:
            # skip the current subgraph and avoid handling pairs twice
            if neighbor_subgraph_index <= subgraph_index: continue

            rigidity_matrix = M.copy()
            # find unconnected pairs of nodes across the subgraphs
            for node_index_1 in subgraphs[subgraph_index]:
                for node_index_2 in subgraphs[neighbor_subgraph_index]:
                    if node_index_1 == node_index_2: continue
                    if nodes[node_index_2] not in G.adj[nodes[node_index_1]]:
                        # add a new edge between these nodes
                        rigidity_matrix = add_restriction_from_edge(G, M, [nodes[node_index_1], nodes[node_index_2]], d)

            # If the additional restrictions do not change the graph's degrees of freedom,
            # the two subgraphs can be merged to a rigid subgraph
            if rigidity_matrix.rank() == dof:
                merges.append([subgraph_index, neighbor_subgraph_index])

    for merge in merges:
        subgraphs[merge[1]] = subgraphs[merge[1]].union(subgraphs[merge[0]])
        subgraphs[merge[0]] = set()

    return [subgraph for subgraph in subgraphs if not subgraph == set()]


def max_rigid_subgraphs_2D(G, as_index_set = False):
    M = graph_to_rigidity_matrix(G, 2)
    rigid_subgraphs = []
    nodes = list(G.nodes)
    node_indices = {}
    for node_index in range(len(nodes)): node_indices[nodes[node_index]] = node_index

    for edge in G.edges:
        node_index_1 = node_indices[edge[0]]
        node_index_2 = node_indices[edge[1]]
        # If the edge is already in a maximum rigid subgraph, it can be skipped
        if any([node_index_1 in subgraph and node_index_2 in subgraph
                for subgraph in rigid_subgraphs]): continue

        rigid_subgraphs.append(rigid_subgraph_from_pinning(M, [node_index_1, node_index_2], 2))

    if as_index_set: return rigid_subgraphs
    # convert representation as sets of nodes to actual subgraphs
    return [G.subgraph([nodes[node_index] for node_index in subgraph]) for subgraph in rigid_subgraphs]


def max_rigid_subgraphs_3D(G, assume_triangles = True, as_index_set = False):
    M = graph_to_rigidity_matrix(G, 3)
    rigid_subgraphs = []
    nodes = list(G.nodes)
    node_indices = {}
    for i in range(len(nodes)): node_indices[nodes[i]] = i

    for edge in G.edges:
        shared_neighbors = set(G.adj[edge[0]]).intersection(G.adj[edge[1]])
        # Iterate over all triangles containing this edge
        for neighbor in shared_neighbors:
            if Point.is_collinear(edge[0], edge[1], neighbor): continue
            node_index_1 = node_indices[edge[0]]
            node_index_2 = node_indices[edge[1]]
            node_index_3 = node_indices[neighbor]
            # If the triangle is already in a maximum rigid subgraph, it can be skipped
            if any([node_index_1 in subgraph and node_index_2 in subgraph and node_index_3 in subgraph
                    for subgraph in rigid_subgraphs]): continue

            rigid_subgraphs.append(rigid_subgraph_from_pinning(M, [node_index_1, node_index_2, node_index_3], 3))

    if not assume_triangles:
        dof = M.rank()
        for edge in G.edges:
            # iterate over points that have exactly one neighbor in the edge
            for neighbor in set(G.adj[edge[0]]).symmetric_difference(G.adj[edge[1]]):
                if Point.is_collinear(edge[0], edge[1], neighbor): continue
                node_index_1 = node_indices[edge[0]]
                node_index_2 = node_indices[edge[1]]
                node_index_3 = node_indices[neighbor]
                # skip if the nodes are already in a subgraph
                if any([node_index_1 in subgraph and node_index_2 in subgraph and node_index_3 in subgraph
                        for subgraph in rigid_subgraphs]): continue
                # Add a new edge between the unconnected nodes
                # That should reduce the degrees of freedom of the graph
                # If the degrees of freedom do not change, the nodes belong to a rigid subgraph
                rigidity_matrix = M.copy()
                if neighbor in G.adj[edge[0]]:
                    rigidity_matrix = add_restriction_from_edge(G, M, [edge[1], neighbor], 3)
                else:
                    rigidity_matrix = add_restriction_from_edge(G, M, [edge[0], neighbor], 3)
                if rigidity_matrix.rank() == dof:
                    rigid_subgraphs.append(rigid_subgraph_from_pinning(M, [node_index_1, node_index_2, node_index_3], 3))

    # Add all edges that are not in any rigid subgraph
    for edge in G.edges:
        node_index_1 = node_indices[edge[0]]
        node_index_2 = node_indices[edge[1]]
        if any([node_index_1 in subgraph and node_index_2 in subgraph
                for subgraph in rigid_subgraphs]): continue
        rigid_subgraphs.append({node_index_1, node_index_2})

    if as_index_set: return rigid_subgraphs
    # convert representation as sets of nodes to actual subgraphs
    return [G.subgraph([nodes[node_index] for node_index in subgraph]) for subgraph in rigid_subgraphs]
