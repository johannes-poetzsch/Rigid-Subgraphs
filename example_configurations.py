import networkx as nx
from sympy import Point

# example from https://github.com/HassoPlattnerInstituteHCI/Algorithmic-Folding/blob/Rigidity/01/linkages.py
# bracing adds a diagonal
def parallel_4_bar(braced=False):
    graph = nx.Graph()
    p1 = Point(0,0)
    p2 = Point(5,0)
    p3 = Point(5,5)
    p4 = Point(0,5)
    graph.add_edges_from([(p1,p2),(p2,p3),(p3,p4),(p4,p1)])
    if braced: graph.add_edge(p4,p2)
    return graph

# example from https://github.com/HassoPlattnerInstituteHCI/Algorithmic-Folding/blob/Rigidity/01/linkages.py
# bracing adds a bracing bar
def jansen_walker(braced=False):
    graph = nx.Graph()
    p1 = Point(0,6)
    p2 = Point(4,10)
    p3 = Point(9,6)
    p4 = Point(5,3)
    p5 = Point(3,0)
    p6 = Point(1,3)
    p7 = Point(4,6)
    graph.add_edges_from([(p1,p2),(p2,p3),(p3,p4),(p4,p5),(p5,p6),(p6,p1),(p6,p4),(p4,p7),(p1,p7),(p2,p7)])
    if braced: graph.add_edge(p7,p3)
    return graph

def dumbbell():
    graph = nx.Graph()
    p1 = Point(0, 0, 0)
    p2 = Point(2, -1, 2)
    p3 = Point(2, -1, -2)
    p4 = Point(2, 2, 0)
    p5 = Point(4, 0, 0)
    graph.add_edges_from([(p1,p2),(p1,p3),(p1,p4)])
    graph.add_edges_from([(p2,p3),(p3,p4),(p4,p2)])
    graph.add_edges_from([(p5,p2),(p5,p3),(p5,p4)])

    diff = Point(10, 1, 1)
    p11 = p1 + diff
    p12 = p2 + diff
    p13 = p3 + diff
    p14 = p4 + diff
    p15 = p5 + diff
    graph.add_edges_from([(p11,p12),(p11,p13),(p11,p14)])
    graph.add_edges_from([(p12,p13),(p13,p14),(p14,p12)])
    graph.add_edges_from([(p15,p12),(p15,p13),(p15,p14)])

    graph.add_edges_from([(p5, p11)])
    return graph
