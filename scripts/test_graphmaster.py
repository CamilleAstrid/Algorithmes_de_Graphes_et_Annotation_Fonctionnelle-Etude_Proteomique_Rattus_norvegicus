#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from graphmaster import Graph
import tempfile
import os

class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph(directed=True, weighted=False)

    def test_add_node(self):
        self.graph.add_node('A')
        self.assertIn('A', self.graph.nodes)
        self.assertEqual(self.graph.nodes['A'], {})
        self.graph.add_node('B', {'color': 'red'})
        self.assertEqual(self.graph.nodes['B'], {'color': 'red'})

    def test_add_edge(self):
        self.graph.add_edge('A', 'B')
        self.assertIn('A', self.graph.edges)
        self.assertIn('B', self.graph.edges['A'])
        self.graph.add_edge('A', 'C', {'weight': 5})
        self.assertEqual(self.graph.edges['A']['C'], {'weight': 5})

    def test_nb_nodes(self):
        self.graph.add_node('A')
        self.graph.add_node('B')
        self.assertEqual(self.graph.nb_nodes(), 2)
        self.graph.add_node('C')
        self.assertEqual(self.graph.nb_nodes(), 3)

    def test_nb_edges(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('B', 'C')
        self.assertEqual(self.graph.nb_edges(), 2)
        self.graph.add_edge('C', 'D')
        self.assertEqual(self.graph.nb_edges(), 3)

    def test_neighbors(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('A', 'C')
        self.assertEqual(set(self.graph.neighbors('A')), {'B', 'C'})
        self.graph.add_edge('A', 'D')
        self.assertEqual(set(self.graph.neighbors('A')), {'B', 'C', 'D'})

    def test_bfs(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('A', 'C')
        self.graph.add_edge('B', 'D')
        state, distance, predecessor = self.graph.bfs('A')
        self.assertEqual(state['D'], 'FINISHED')
        self.assertEqual(distance['D'], 2)
        self.assertEqual(predecessor['D'], 'B')
        self.graph.add_edge('C', 'E')
        state, distance, predecessor = self.graph.bfs('A')
        self.assertEqual(distance['E'], 2)
        self.assertEqual(predecessor['E'], 'C')

    def test_shortest_path(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('B', 'C')
        self.graph.add_edge('A', 'C')
        path = self.graph.get_shortest_path('A', 'C')
        self.assertEqual(path, ['A', 'C'])
        self.graph.add_edge('C', 'D')
        path = self.graph.get_shortest_path('A', 'D')
        self.assertEqual(path, ['A', 'C', 'D'])
        path = self.graph.get_shortest_path('B', 'D')
        self.assertEqual(path, ['B', 'C', 'D'])

    def test_shortest_path_disconnected_graph(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('C', 'D')
        path = self.graph.get_shortest_path('A', 'D')
        self.assertEqual(path, [])
        path = self.graph.get_shortest_path('C', 'D')
        self.assertEqual(path, ['C', 'D'])

    def test_shortest_path_single_node(self):
        self.graph.add_node('A')
        path = self.graph.get_shortest_path('A', 'A')
        self.assertEqual(path, ['A'])

    def test_shortest_path_no_path(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('B', 'C')
        with self.assertRaises(ValueError):
            self.graph.get_shortest_path('A', 'D')
        with self.assertRaises(ValueError):
            self.graph.get_shortest_path('D', 'A')
        self.graph.add_node('D')
        self.assertEqual(self.graph.get_shortest_path('A', 'D'), [])

    def test_dfs(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('A', 'C')
        self.graph.add_edge('B', 'D')
        state, predecessor, discovered, classification, finished = self.graph.dfs()
        self.assertEqual(state['D'], 'FINISHED')
        self.assertEqual(predecessor['D'], 'B')
        self.assertIn(('A', 'B'), classification)
        self.assertIn(('B', 'D'), classification)
        self.graph.add_edge('C', 'E')
        state, predecessor, discovered, classification, finished = self.graph.dfs()
        self.assertEqual(state['E'], 'FINISHED')
        self.assertEqual(predecessor['E'], 'C')

    def test_is_acyclic(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('B', 'C')
        self.assertTrue(self.graph.is_acyclic())
        self.graph.add_edge('C', 'A')
        self.assertFalse(self.graph.is_acyclic())

    def test_max_depth(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('A', 'C')
        self.graph.add_edge('B', 'D')
        value = self.graph.max_depth()
        self.assertEqual(value, 2)

    def test_topological_sort(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('B', 'C')
        self.graph.add_edge('A', 'C')
        topo_sort = self.graph.topological_sort()
        self.assertEqual(topo_sort, ['A', 'B', 'C'])
        self.graph.add_edge('C', 'D')
        topo_sort = self.graph.topological_sort()
        self.assertEqual(topo_sort, ['A', 'B', 'C', 'D'])

    def test_topological_sort_single_node(self):
        self.graph.add_node('A')
        topo_sort = self.graph.topological_sort()
        self.assertEqual(topo_sort, ['A'])

    def test_topological_sort_disconnected_graph(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('C', 'D')
        topo_sort = self.graph.topological_sort()
        self.assertTrue(topo_sort.index('A') < topo_sort.index('B'))
        self.assertTrue(topo_sort.index('C') < topo_sort.index('D'))

    def test_topological_sort_cyclic_graph(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('B', 'C')
        self.graph.add_edge('C', 'A')
        with self.assertRaises(ValueError):
            self.graph.topological_sort()

    def test_topological_sort_with_multiple_edges(self):
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('A', 'C')
        self.graph.add_edge('B', 'D')
        self.graph.add_edge('C', 'D')
        topo_sort = self.graph.topological_sort()
        self.assertTrue(topo_sort.index('A') < topo_sort.index('B'))
        self.assertTrue(topo_sort.index('A') < topo_sort.index('C'))
        self.assertTrue(topo_sort.index('B') < topo_sort.index('D'))
        self.assertTrue(topo_sort.index('C') < topo_sort.index('D'))

    def test_read_delim(self):
        # Create a temporary file with graph data
        with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_file:
            temp_file.write("node_id1\tnode_id2\tweight\n")
            temp_file.write("A\tB\t1\n")
            temp_file.write("B\tC\t2\n")
            temp_file.write("C\tD\t3\n")
            temp_file.write("D\tA\t4\n")
            temp_file_name = temp_file.name

        # Read the graph from the temporary file
        graph = Graph(directed=True)
        graph.read_delim(temp_file_name, column_separator='\t', potential_weight_attribute='weight')

        # Check nodes
        self.assertIn('A', graph.nodes)
        self.assertIn('B', graph.nodes)
        self.assertIn('C', graph.nodes)
        self.assertIn('D', graph.nodes)

        # Check edges and weights
        self.assertIn('B', graph.edges['A'])
        self.assertEqual(graph.edges['A']['B']['weight'], '1')
        self.assertIn('C', graph.edges['B'])
        self.assertEqual(graph.edges['B']['C']['weight'], '2')
        self.assertIn('D', graph.edges['C'])
        self.assertEqual(graph.edges['C']['D']['weight'], '3')
        self.assertIn('A', graph.edges['D'])
        self.assertEqual(graph.edges['D']['A']['weight'], '4')

        # Clean up the temporary file
        os.remove(temp_file_name)

if __name__ == '__main__':
    unittest.main()