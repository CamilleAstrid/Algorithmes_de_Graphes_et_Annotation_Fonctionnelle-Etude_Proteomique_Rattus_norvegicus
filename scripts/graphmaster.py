#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque
import sys
from pprint import pprint # pprint allows for better display of dictionaries

class Graph:
    def __init__(self, directed=True, weighted=False, weight_attribute=None):
        """
        Initializes a graph object.

        Parameters:
        directed (bool): If True, the graph is directed. If False, the graph is undirected. Default is True.
        weighted (bool): If True, the graph is weighted. If False, the graph is unweighted. Default is False.
        weight_attribute (str or None): The attribute name to be used for weights if the graph is weighted. Default is None.
        """
        self.nodes = {}
        self.edges = {}
        self.directed = directed
        self.weighted = weighted
        self.weight_attribute = weight_attribute
        self.alt_id = {}  # alternative id for nodes
        self.roots = [] # list of nodes with no predecessors
        self.leaves = [] # list of nodes with no successors

    def display_nodes(self):
        """
        Displays all nodes in the graph along with their attributes.
        """
        print("Nodes:")
        for node_id, attributes in self.nodes.items():
            print(f"{node_id}: {attributes}")

    def display_edges(self):
        """
        Displays all edges in the graph along with their attributes.
        """
        print("Edges:")
        for node_id1, neighbors in self.edges.items():
            for node_id2, attributes in neighbors.items():
                print(f"{node_id1} -> {node_id2}: {attributes}")
    
    def display_bfs(self, start_node_id):
        """
        Displays the BFS traversal results starting from the given node.
        
        Parameters:
        start_node_id (hashable): The identifier for the starting node.
        """
        state, distance, predecessor = self.bfs(start_node_id)
        print("\nBFS Traversal:")
        print("State:")
        pprint(state)
        print("\nDistance from start node:")
        pprint(distance)
        print("\nPredecessor nodes:")
        pprint(predecessor)

    def display_dfs(self):
        """
        Displays the DFS traversal results.
        """
        state, predecessor, discovered, classification, finished = self.dfs()
        print("\nDFS Traversal:")
        print("State:")
        pprint(state)
        print("\nPredecessor nodes:")
        pprint(predecessor)
        print("\nDiscovery times:")
        pprint(discovered)
        print("\nEdge classifications:")
        pprint(classification)
        print("\nFinish times:")
        pprint(finished)

    def display_topological_sort(self):
        """
        Displays the topological sort of the graph.
        """
        try:
            topo_sort = self.topological_sort()
            print("\nTopological Sort:")
            pprint(topo_sort)
        except ValueError as e:
            print(f"\nError: {e}")

    def display_shortest_path(self, start_node_id, end_node_id):
        """
        Displays the shortest path from start_node_id to end_node_id.
        
        Parameters:
        start_node_id (hashable): The identifier for the starting node.
        end_node_id (hashable): The identifier for the ending node.
        """
        path = self.get_shortest_path(start_node_id, end_node_id)
        if path:
            print(f"\nShortest path from {start_node_id} to {end_node_id}:")
            print(" -> ".join(map(str, path)))
        else:
            print(f"\nNo path found from {start_node_id} to {end_node_id}.")

    def add_node(self, node_id, attributes=None):
        """
        Adds a node with the given node_id to the graph. If the node already exists, it does nothing.
        
        Parameters:
        node_id (hashable): The identifier for the node.
        attributes (dict, optional): Attributes for the node. Defaults to None.
        
        Returns:
        dict: The attributes of the node with the given node_id.
        """
        if node_id not in self.nodes:  # ensure node does not already exist
            if attributes is None:  # create empty attributes if not provided
                attributes = {}
            self.nodes[node_id] = attributes
            self.edges[node_id] = {}  # init outgoing edges
            if self.directed:  # if directed graph
                self.roots.append(node_id)
                self.leaves.append(node_id)
        return self.nodes[node_id]  # return node attributes

    def nb_nodes(self):
        """
        Counts the number of nodes in the graph.

        Returns:
        int: The number of nodes in the graph.
        """
        return len(self.nodes)

    def add_edge(self, node_id1, node_id2, attributes=None, node1_attributes=None, node2_attributes=None): 
        """
        Adds an edge between two nodes in the graph. If the nodes do not exist, they are created with optional attributes.
        
        Parameters:
        node_id1 (hashable): The identifier for the first node.
        node_id2 (hashable): The identifier for the second node.
        attributes (dict, optional): Attributes for the edge. Defaults to None.
        node1_attributes (dict, optional): Attributes for the first node if it needs to be created. Defaults to None.
        node2_attributes (dict, optional): Attributes for the second node if it needs to be created. Defaults to None.
        
        Returns:
        dict: The attributes of the edge between node_id1 and node_id2.
        """
        # create nodes if they do not exist
        if node_id1 not in self.nodes: self.add_node(node_id1, node1_attributes) # ensure node1 exists
        if node_id2 not in self.nodes: self.add_node(node_id2, node2_attributes) # ensure node2 exists
        
        # add edge(s) only if they do not exist
        if node_id2 not in self.edges[node_id1]:
            if attributes is None: # create empty attributes if not provided
                attributes = {}
            self.edges[node_id1][node_id2] = attributes
            if not self.directed: # if undirected graph
                self.edges[node_id2][node_id1] = self.edges[node_id1][node_id2] # share the same attributes as n1->n2
            else:
                if node_id2 in self.roots:
                    self.roots.remove(node_id2)
                if node_id1 in self.leaves:
                    self.leaves.remove(node_id1)
        return self.edges[node_id1][node_id2] # return edge attributes

    def nb_edges(self):
        """
        Calculate the number of edges in the graph.

        Returns:
        int: The number of edges in the graph.
        """
        count = 0
        for node in self.edges:
            count += len(self.edges[node])
        return count

    def read_delim(self, filename, column_separator='\t', potential_weight_attribute=None):
        """
        Parses a text file with columns separated by the specified column_separator and returns a graph.
        The file should have the following line syntax:
        node_id1   node_id2    att1    att2    att3    ...
        
        Parameters:
        filename (str): The path to the file to be read.
        column_separator (str): The character used to separate columns in the file. Default is tab ('\t').
        potential_weight_attribute (str, optional): The attribute name to be used for weights if the graph is weighted. Default is None.
        
        Returns:
        Graph: A graph object created from the file data.
        """
        with open(filename) as f: 
            # GET COLUMNS NAMES
            tmp = f.readline().rstrip() # rstrip removes the trailing space (lstrip removes leading space, and strip removes both)
            attNames = tmp.split(column_separator) # create a list with the characters
            
            # REMOVES FIRST TWO COLUMNS WHICH CORRESPONDS TO THE LABELS OF THE CONNECTED VERTICES
            attNames.pop(0)  # remove first column name (source node not to be in attribute names)
            attNames.pop(0)  # remove second column (target node ...)
            
            # Check if the graph is weighted by looking for a weight attribute
            if potential_weight_attribute and potential_weight_attribute in attNames:
                self.weighted = True
                self.weight_attribute = potential_weight_attribute
            
            # PROCESS THE REMAINING LINES
            row = f.readline().rstrip()
            while row:
                vals = row.split(column_separator)
                u = vals.pop(0) # starting vertex
                v = vals.pop(0) # finishing vertex
                att = {}
                for i in range(len(attNames)):
                    att[attNames[i]] = vals[i]  # create the corresponding attribute list
                self.add_edge(u, v, att)
                row = f.readline().rstrip() # NEXT LINE
        return self

    def neighbors(self, node_id): 
        """
        Returns the neighbors of a given node.

        Args:
            node_id (int): The ID of the node for which to find neighbors.

        Returns:
            list: A sorted list of neighbors for the given node ID. If the node ID 
            is not in the edges, returns an empty list.
        """
        if node_id in self.edges:
            return sorted(list(self.edges[node_id]))

    def get_successors(self, node_id):
        """
        Returns the successors of a given node in a directed graph.

        Args:
            node_id (any): The identifier of the node for which to find successors.

        Returns:
            list: A list of successors of the given node.
        """
        if self.directed is True and node_id in self.edges:
            return sorted(list(self.edges[node_id]))
        else:
            raise ValueError("The graph is undirected or the node does not exist.")
    
    def get_predecessors(self, node_id):
        """
        Returns the predecessors of a given node in a directed graph.

        Args:
            node_id (any): The identifier of the node for which to find predecessors.

        Returns:
            list: A list of predecessors of the given node.
        """
        if self.directed is True and node_id in self.nodes:
            predecessors = []
            for node in self.edges:
                if node_id in self.edges[node]:
                    predecessors.append(node)
            return predecessors
        else:
            raise ValueError("The graph is undirected or the node does not exist.")
    
    def get_descendants(self, node_id):
        """
        Returns the descendants of a given node in a directed graph.

        Args:
            node_id (any): The identifier of the node for which to find descendants.

        Returns:
            list: A list of descendants of the given node.
        """
        if self.directed is True and node_id in self.edges:
            descendants = []
            stack = [node_id]
            while stack:
                current_node = stack.pop()
                for neighbor in self.edges[current_node]:
                    descendants.append(neighbor)
                    stack.append(neighbor)
            return descendants
        else:
            raise ValueError("The graph is undirected or the node does not exist.")
    
    def get_ascendants(self, node_id):
        """
        Returns the ascendants of a given node in a directed graph.

        Args:
            node_id (any): The identifier of the node for which to find ascendants.

        Returns:
            list: A list of ascendants of the given node.
        """
        if self.directed is True and node_id in self.nodes:
            ascendants = []
            stack = [node_id]
            while stack:
                current_node = stack.pop()
                for node in self.edges:
                    if current_node in self.edges[node]:
                        ascendants.append(node)
                        stack.append(node)
            return ascendants
        else:
            raise ValueError("The graph is undirected or the node does not exist.")

    def bfs(self, start_node_id):
        """
        Performs a Breadth-First Search (BFS) traversal on a graph starting from a given node.

        Args:
            start_node_id (any): The identifier of the starting node for the BFS traversal.

        Returns:
            tuple: A tuple containing three elements:
                - state (dict): A dictionary where keys are nodes and values are their states ('UNEXPLORED', 'DISCOVERED', 'FINISHED').
                - distance (dict): A dictionary where keys are nodes and values are the distances from the starting node.
                - predecessor (dict): A dictionary where keys are nodes and values are their predecessors in the BFS traversal.
        """
        # Initialize states, distances, and predecessors for each node
        state = {node: 'UNEXPLORED' for node in self.nodes}
        distance = {node: float('inf') for node in self.nodes}
        predecessor = {node: None for node in self.nodes}

        # Mark the start node as discovered and initialize its distance to 0
        state[start_node_id] = 'DISCOVERED'
        distance[start_node_id] = 0
        queue = deque([start_node_id])  # Use a queue for breadth-first traversal

        while queue:
            u = queue.popleft()  # Get the first node from the queue
            for v in self.edges[u]:  # Traverse all neighbors of node u
                if state[v] == 'UNEXPLORED':  # If the neighbor has not been explored yet
                    state[v] = 'DISCOVERED'  # Mark the neighbor as discovered
                    distance[v] = distance[u] + 1  # Update the distance of the neighbor
                    predecessor[v] = u  # Set the predecessor of the neighbor
                    queue.append(v)  # Add the neighbor to the queue for future exploration
            state[u] = 'FINISHED'  # Mark node u as finished

        return state, distance, predecessor  # Return states, distances, and predecessors

    def dfs(self):
        """
        Performs a depth-first search (DFS) on the graph.

        Returns:
        tuple: A tuple containing five elements:
            - state (dict): A dictionary where keys are nodes and values are states ('UNEXPLORED', 'DISCOVERED', 'FINISHED').
            - predecessor (dict): A dictionary where keys are nodes and values are predecessors in the DFS.
            - discovered (dict): A dictionary where keys are nodes and values are discovery times.
            - classification (dict): A dictionary where keys are edges (tuples) and values are edge classifications ('TREE EDGE', 'BACK EDGE', 'CROSS EDGE', 'FORWARD EDGE').
            - finished (dict): A dictionary where keys are nodes and values are finishing times.
        """
        # Initialize dictionaries to store the state, predecessor, discovery time, edge classification, and finish time for each node
        state, predecessor, discovered, classification, finished = {}, {}, {}, {}, {}
        
        # Set all nodes to the initial state of "UNEXPLORED" and no predecessors
        for vertex in self.nodes:
            state[vertex] = "UNEXPLORED"
            predecessor[vertex] = None
        
        # Initialize the time counter
        time = 0
        
        # Perform DFS for each node that is still "UNEXPLORED"
        for vertex in self.nodes:
            if state[vertex] == "UNEXPLORED":
                state, predecessor, discovered, classification, finished = self.dfs_visit(vertex, time, state, predecessor, discovered, classification, finished)
        
        # Return the state, predecessor, discovery time, edge classification, and finish time for each node
        return state, predecessor, discovered, classification, finished

    def dfs_visit(self, vertex, time, state, predecessor, discovered, classification, finished):
        """
        Perform a Depth-First Search (DFS) visit on a graph starting from a given vertex.
        
        Args:
            vertex (any): The current vertex being visited.
            time (int): The current time step in the DFS.
            state (dict): A dictionary tracking the state of each vertex (UNEXPLORED, DISCOVERED, FINISHED).
            predecessor (dict): A dictionary tracking the predecessor of each vertex.
            discovered (dict): A dictionary tracking the discovery time of each vertex.
            classification (dict): A dictionary classifying the edges (TREE EDGE, BACK EDGE, CROSS EDGE, FORWARD EDGE).
            finished (dict): A dictionary tracking the finish time of each vertex.
            
        Returns:
            tuple: Updated state, predecessor, discovered, classification, and finished dictionaries.
            
        The function explores the graph using DFS and classifies the edges based on their types:
        - TREE EDGE: An edge leading to an undiscovered vertex.
        - BACK EDGE: An edge leading to an already discovered vertex.
        - CROSS EDGE: An edge leading to a vertex discovered before the current vertex.
        - FORWARD EDGE: An edge leading to a vertex discovered after the current vertex.
        """
        # Mark the current vertex as discovered
        state[vertex] = "DISCOVERED"
        time += 1
        # Record the discovery time of the current vertex
        discovered[vertex] = time
        # Traverse all adjacent vertices
        for v in self.edges[vertex]:
            if state[v] == "UNEXPLORED":
                # If the adjacent vertex is unexplored, set its predecessor and classify the edge as a tree edge
                predecessor[v] = vertex
                classification[(vertex, v)] = "TREE EDGE"
                # Recursively visit the adjacent vertex
                state, predecessor, discovered, classification, finished = self.dfs_visit(v, time, state, predecessor, discovered, classification, finished)
            else:
                if state[v] == "DISCOVERED":
                    # If the adjacent vertex is discovered, classify the edge as a back edge
                    classification[(vertex, v)] = "BACK EDGE"
                else:
                    if discovered[vertex] > discovered[v]:
                        # If the current vertex was discovered after the adjacent vertex, classify the edge as a cross edge
                        classification[(vertex, v)] = "CROSS EDGE"
                    else:
                        # Otherwise, classify the edge as a forward edge
                        classification[(vertex, v)] = "FORWARD EDGE"
        # Mark the current vertex as finished
        state[vertex] = "FINISHED"
        # Record the finish time of the current vertex
        finished[vertex] = time + 1
        
        return state, predecessor, discovered, classification, finished
    
    def get_shortest_path(self, start_node_id, end_node_id):
        """
        Finds the shortest path from start_node_id to end_node_id using BFS.

        Parameters:
        start_node_id (hashable): The identifier for the starting node.
        end_node_id (hashable): The identifier for the ending node.

        Returns:
        list: A list of nodes representing the shortest path from start_node_id to end_node_id.
        """
        # Check if the start node exists in the graph
        if start_node_id not in self.nodes:
            raise ValueError(f"Start node {start_node_id} does not exist in the graph.")
        
        # Check if the end node exists in the graph
        if end_node_id not in self.nodes:
            raise ValueError(f"End node {end_node_id} does not exist in the graph.")
        
        state, distance, predecessor = self.bfs(start_node_id)

        # If the end node is unreachable, return an empty list
        if distance[end_node_id] == float('inf'):
            return []

        # Reconstruct the path from end_node_id to start_node_id
        path = []
        current_node = end_node_id
        while current_node is not None:
            path.append(current_node)
            current_node = predecessor[current_node]
        
        # Reverse the path to get it from start_node_id to end_node_id
        path.reverse()
        return path

    def max_depth(self):
        """
        Calculate the maximum depth of the GO graph (the diameter of the GO graph).
        The depth of a node is defined as the length of the longest path from a leaf node to a root node.
        A root node is a node with no predecessors, a leaf node is a node with no successors.

        Parameters:
        go (Graph): A Graph object representing the Gene Ontology graph. It should contain 'nodes' and 'edges'.

        Returns:
        int: The maximum depth of the GO graph.
        """
        if self.is_acyclic() is False:
            raise ValueError("The graph is not acyclic.")
        else:	
            # get the depth between each root and each leaf
            depths = {}
            for node_start in self.roots:
                for node_end in self.leaves:
                    depths[node_start] = 0
                    path = self.get_shortest_path(node_start, node_end)
                    if path:
                        depths[node_start] = max(depths[node_start], len(path)-1)
            return max(depths.values())

    def is_acyclic(self):
        """
        Determines if the graph is acyclic.
        This function uses Depth-First Search (DFS) to classify the edges of the graph.
        If any edge is classified as a "BACK EDGE", the graph contains a cycle and is not acyclic.

        Returns:
        bool: True if the graph is acyclic, False otherwise.
        """
        # Perform DFS on the graph and get the edge classifications
        res = self.dfs()
        classification = res[3]
        acyclic = True

        # Check if any edge is classified as a "BACK EDGE"
        for key in classification:
            if classification[key] == "BACK EDGE":
                acyclic = False  # If a back edge is found, the graph is not acyclic

        return acyclic  # Return True if no back edges are found, otherwise False

    def topological_sort(self):
        """
        Performs a topological sort on a Directed Acyclic Graph (DAG).

        Returns:
            list: A list of nodes sorted in topological order.
        """
        def dfs_topological(v, visited, stack):
            """
            Perform a Depth-First Search (DFS) to achieve topological sorting of a graph.

            Args:
                v (int): The current node to process.
                visited (list of bool): A list indicating whether each node has been visited.
                stack (list of int): The stack to store the topologically sorted nodes.

            Returns:
                None: This function modifies the visited list and stack in place.

            The function marks the current node as visited, recursively visits all its unvisited neighbors,
            and finally adds the current node to the stack once all its neighbors have been visited.
            """
            # Mark the current node as visited
            visited[v] = True
            # Traverse all neighbors of the current node
            for neighbor in self.edges[v]:
                # If the neighbor has not been visited yet, recursively call dfs_topological
                if not visited[neighbor]:
                    dfs_topological(neighbor, visited, stack)
            # Add the current node to the stack once all its neighbors have been visited
            stack.append(v)

        # Initialize all nodes as not visited
        if not self.is_acyclic():
            raise ValueError("The graph is not acyclic")
        visited = {node: False for node in self.nodes}
        stack = []
        
        # Perform DFS for each unvisited node
        for node in self.nodes:
            if not visited[node]:
                dfs_topological(node, visited, stack)

        # Return the reversed stack to get the topological order
        return stack[::-1]

##### main → tests #####
if __name__ == "__main__":
    print("# Graph lib tests")
    try:
        filename = sys.argv[1]
    except:
        print("Usage : programme.py <filename>")
        quit()
    print(f"## Loading graph from {filename}")
    g = Graph(directed=True, weighted=False)
    pprint(g.read_delim(filename))
