# Copyright 2020 University of Groningen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Collection of useful functions for performing operations based
on graphs.
"""
from collections import defaultdict
import networkx as nx

def neighborhood(graph, source, max_length, min_length=1):
    """
    Returns all neighbours of `source` that are less or equal
    to `cutoff` nodes away and more or equal to `start` away
    within a graph excluding the node itself.

    Parameters
    ----------
    graph: :class:`networkx.Graph`
        A networkx graph definintion
    source:
        A node key matching one in the graph
    max_length: :type:`int`
        The maxdistance between the node and its
        neighbours.
    min_length: :type:`int`
        The minimum length of a path. Default
        is zero

    Returns
    --------
    list
       list of all nodes distance away from reference
    """
    paths = nx.single_source_shortest_path(G=graph, source=source, cutoff=max_length)
    neighbours = [node for node, path in paths.items() if min_length <= len(path)]
    return neighbours

def find_nodes_with_attributes(graph, **attrs):
    """
    Yields all nodes in graph, which have all
    attributes in attrs set to value.

    Parameters:
    -----------
    graph: nx.Graph
    **attrs: collections.abc.Mapping
        The attributes and their desired values.

    Yields:
    --------
    collections.abc.Hashable
    """
    for node in graph.nodes:
        for attr, value in attrs.items():
            if attr not in graph.nodes[node] or graph.nodes[node][attr] != value:
                break
        else:
            yield node

def is_branched(graph):
    """
    Check if any node has a degree larger than 2

    Parameters:
    -----------
    graph: :class:`networkx.Graph`
        A networkx graph definintion

    Returns:
    --------
    bool
       is branched
    """
    for _, deg in graph.degree:
        if deg > 2:
            return True
    return False

def find_connecting_edges(res_graph, molecule, nodes):
    """
    Given a list of `nodes` referring to specific nodes in a
    molecule residue graph (`res_graph`) find all edges in the
    molecule graph, which connect the two residues. This function
    avoids looping over all edges in the molecule graph, so it
    scales well.

    Parameters
    ----------
    res_graph: :class:`nx.Graph`
        residue graph; must have the attribute "graph" and
        "resid", where graph is the fragment the node describes
        in the mol_graph
    molecule: :class:`vermouth.molecule.Molecule`
        vermouth molecule underlying the residue graph
    nodes: (node_key, node_key)
        tuple of node-keys specifing a residue in residue graph

    Returns
    ----------
    list
       list of edges found
    """
    # first find all nodes in the residue graph fragments,
    # whose degree is unequal in thegraph, residues, weights, attribute residue graph fragment
    # and molecule. This is an efficent way to filter which
    # atoms are involved in a potential link, without having
    # to check all edges for all atoms in a residue.
    allowed_nodes = defaultdict(list)
    for res_node in nodes:
        for node in res_graph.nodes[res_node]["graph"].nodes:
            deg = res_graph.nodes[res_node]["graph"].degree(node)
            if deg != molecule.degree(node):
                allowed_nodes[res_node].append(node)

    # given all nodes, which potentially have a connecting edge
    # we only need to check generate all possible edges and check
    # if they exist
    edges = []
    for high_res_node_a in allowed_nodes[nodes[0]]:
        for high_res_node_b in allowed_nodes[nodes[1]]:
            if molecule.has_edge(high_res_node_a, high_res_node_b):
                edges.append((high_res_node_a, high_res_node_b))

    return edges
