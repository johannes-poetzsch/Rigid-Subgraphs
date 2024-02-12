# Rigid Subgraphs
Python implementation of a method to find all maximum infinitesimal rigid subgraphs of 2 and 3 dimensional graphs.

## Algorithm to find maximum infinitesimal rigid subgraphs in 2D
*For simplicity, infinitesimal rigidity will be refered to as rigidity in the description of the algothims.*

In 2D, fixing two points in a rigid graph fixes the whole graph. Our algorithm exploits this property to find maximum rigid subgraphs:
Since any non-trivial rigid graph contains at least one edge, all maximum rigid subgraphs can be found by fixing a single edge and then detecting all points that can not move as a consequence.

To do that, we first create the rigidity matrix of the graph. To fix an edge, we set the possible movement of both points to 0 by adding a row for each dimension of the points.
We can then search through the nullspace of the matrix to find all points that have been fixed and add these to the subgraph. Since exactly the points that can not move relative to the edge are added, the found points form a maximum rigid subgraph.

By iterating through all edges while skipping those that are already in a maximum rigid subgraph, all maximum rigid subgraphs are found.
