#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from graphmaster import Graph
import sys
import os
import urllib.request

def load_OBO(filename=sys.path[0]+'/data/go-basic.obo'):
	"""
	parse the OBO file and returns the graph
	obsolete terms are discarded
	only is_a and part_of relationships are loaded

	Extract of a file to be parsed:
	[Term]
	id: GO:0000028
	name: ribosomal small subunit assembly
	namespace: biological_process
	def: "The aggregation, arrangement and bonding together of constituent RNAs and proteins to form the small ribosomal subunit." [GOC:jl]
	subset: gosubset_prok
	synonym: "30S ribosomal subunit assembly" NARROW [GOC:mah]
	synonym: "40S ribosomal subunit assembly" NARROW [GOC:mah]
	is_a: GO:0022618 ! ribonucleoprotein complex assembly
	relationship: part_of GO:0042255 ! ribosome assembly
	relationship: part_of GO:0042274 ! ribosomal small subunit biogenesis
	"""
	def parseTerm(lines):
		# search for obsolete
		for l in lines:
			if l.startswith('is_obsolete: true'):
				return
		# otherwise create node
		go_id = re_go_id.match(lines.pop(0)).group(1)
		go_attr = go_graph.add_node(go_id) # add node to graph and get the node attribute dict
		go_attr['type'] = 'GOTerm'
		for line in lines:
			if re_go_name.match(line): go_attr['name'] = re_go_name.match(line).group(1)
			elif re_go_namespace.match(line): go_attr['namespace'] = re_go_namespace.match(line).group(1)
			elif re_go_def.match(line): go_attr['def'] = re_go_def.match(line).group(1)
			elif re_go_alt_id.match(line): go_graph.alt_id[ re_go_alt_id.match(line).group(1) ] = go_id  # alt_id → go_id
			elif re_go_is_a.match(line): 
				parent_id = re_go_is_a.match(line).group(1)
				go_graph.add_edge(go_id, parent_id, { 'relationship': 'is a' })
			elif re_go_part_of.match(line): 
				parent_id = re_go_part_of.match(line).group(1)
				go_graph.add_edge(go_id, parent_id, { 'relationship': 'part of' })
	# method main
	go_graph = Graph(directed=True, weighted=False)
	go_graph.alt_id = {} # alternate GO ids
	# regexp to parse term lines
	re_go_id = re.compile(r'^id:\s+(GO:\d+)\s*$')
	re_go_name = re.compile(r'^name:\s+(.+)\s*$')
	re_go_namespace = re.compile(r'^namespace:\s+(.+)\s*$')
	re_go_def = re.compile(r'^def:\s+"(.+)"\s+\[.*\]\s*$')
	re_go_alt_id = re.compile(r'^alt_id:\s+(GO:\d+)\s*$')
	re_go_is_a = re.compile(r'^is_a:\s+(GO:\d+)\s')
	re_go_xref = re.compile(r'^xref:\s+(.+)\s*$')
	re_go_part_of = re.compile(r'^relationship:\s+part_of\s+(GO:\d+)\s')
	# buffer each term lines, then parse lines to create GOTerm node
	with open(filename) as f:
		line = f.readline().rstrip()
		# skip header until first [Term] is reached
		while not line.startswith('[Term]'): 
			line = f.readline().rstrip()
		buff = []  
		line = f.readline()
		stop = False
		while line and not stop:
			line = line.rstrip()
			# new Term
			if line.startswith('[Term]'):
				parseTerm(buff)
				buff=[]
			# last Term
			elif line.startswith('[Typedef]'):
				parseTerm(buff)
				stop=True
			# or append to buffer
			else:
				buff.append(line)
			line = f.readline()
	return go_graph

def load_GOA(go:Graph, filename, warnings=True):
	"""
	parse GOA file and add annotated gene products to previsouly loaded graph go

	Extract of a file to be parsed:
	gaf-version: 2.1
	!GO-version: http://purl.obolibrary.org/obo/go/releases/2020-11-28/extensions/go-plus.owl
	UniProtKB       O05154  tagX            GO:0008360      GO_REF:0000043  IEA     UniProtKB-KW:KW-0133    P       Putative glycosyltransferase TagX       tagX|SAOUHSC_00644      protein 93061   20201128        UniProt 
			
	UniProtKB       O05154  tagX            GO:0016740      GO_REF:0000043  IEA     UniProtKB-KW:KW-0808    F       Putative glycosyltransferase TagX       tagX|SAOUHSC_00644      protein 93061   20201128        UniProt 
			
	UniProtKB       O05204  ahpF            GO:0000302      GO_REF:0000002  IEA     InterPro:IPR012081      P       Alkyl hydroperoxide reductase subunit F ahpF|SAOUHSC_00364      protein 93061   20201128        InterPro
			
		0        1       2   3       4             5          6        7      8             9                              10
				id    name        go_id               evidence-codes                     desc                           aliases

	GAF spec: http://geneontology.org/docs/go-annotation-file-gaf-format-2.1/
	Column 	Content 						Required? 	Cardinality 	Example
	1 		DB 								required 	1 				UniProtKB
	2 		DB Object ID 					required 	1 				P12345
	3 		DB Object Symbol 				required 	1 				PHO3
	4 		Qualifier 						optional 	0 or greater 	NOT
	5 		GO ID 							required 	1 				GO:0003993
	6 		DB:Reference (|DB:Reference) 	required 	1 or greater 	PMID:2676709
	7 		Evidence Code 					required 	1 				IMP
	8 		With (or) From 					optional 	0 or greater 	GO:0000346
	9 		Aspect 							required 	1 				F
	10 		DB Object Name 					optional 	0 or 1 			Toll-like receptor 4
	11 		DB Object Synonym (|Synonym) 	optional 	0 or greater 	hToll 	Tollbooth
	12 		DB Object Type 					required 	1 				protein
	13 		Taxon(|taxon) 					required 	1 or 2 			taxon:9606
	14 		Date 							required 	1 				20090118
	15 		Assigned By 					required 	1 				SGD
	16 		Annotation Extension 			optional 	0 or greater 	part_of(CL:0000576)
	17 		Gene Product Form ID 			optional 	0 or 1 			UniProtKB:P12345-2
	"""
	with open(filename) as f: 
		line = f.readline()
		while line:
			if not line.startswith('!'): # skip comments
				cols = line.rstrip().split('\t')
				gp_id = cols[1]
				gt_id = cols[4]
				if gt_id not in go.nodes: # GOTerm not found search alternate ids
					while gt_id not in go.nodes and gt_id in go.alt_id:
						gt_id = go.alt_id[gt_id] # replace term by alternate
				if gt_id not in go.nodes: # failure: warn user
					if warnings:
						print(f'Warning: could not attach a gene product ({gp_id}) to a non existing GO Term ({gt_id})\n')
				else: # success: GOTerm to attach to was found
					# create node for gene product if not already present
					if gp_id not in go.nodes:
						gp_attr = go.add_node(gp_id, { 'id': gp_id, 'type': 'GeneProduct'})
					# create or update gene product attributes
					gp_attr = go.nodes[gp_id]
					gp_attr['name'] = cols[2]
					gp_attr['desc'] = cols[9]
					gp_attr['aliases'] = cols[10].split('|')
					# attach gene product to GOTerm
					gt_attr = go.nodes[gt_id]
					e_attr = go.add_edge(gp_id, gt_id)
					e_attr['relationship'] = 'annotation'
					if 'evidence-codes' not in e_attr:
						e_attr['evidence-codes'] = []
					e_attr['evidence-codes'].append( cols[6] )
			line = f.readline()

def GOTerms(go:Graph, gp_id, recursive=False):
	"""
	Retrieve Gene Ontology (GO) terms associated with a given gene product ID (gp_id).

	Parameters:
	go (Graph): A Graph object representing the Gene Ontology graph.
			   It should contain 'nodes' which is a dictionary of node IDs and their attributes.
	gp_id (str): The gene product ID for which GO terms are to be retrieved.
	recursive (bool): If False, only directly linked GO terms (successors) are returned.
					  If True, both directly linked GO terms and their descendants are returned.

	Returns:
	list or None: A list of GO terms (node IDs) associated with the given gene product ID.
				  Returns None if the gp_id is not found in the GO graph.
	"""
	if not recursive:
		if gp_id in go.nodes:
			# Return directly linked GO terms (successors)
			return go.neighbors(gp_id)
	else:
		# GOTerms directly linked (successors) AND their descendants should be returned
		def get_descendants(go, node, descendants):
			for neighbor in go.neighbors(node):
				if go.nodes[neighbor]['type'] == 'GOTerm' and neighbor not in descendants:
					# Add the neighbor to descendants set
					descendants.add(neighbor)
					# Recursively find descendants of the neighbor
					get_descendants(go, neighbor, descendants)
		descendants = set()
		if gp_id in go.nodes:
			# Start finding descendants from the given gene product ID
			get_descendants(go, gp_id, descendants)
		# Return the list of all descendants
		return list(descendants)
	
def GeneProducts(go:Graph, go_id, recursive=False):
	"""
	Retrieve GeneProducts linked to a given GO term.

	Parameters:
	go (Graph): A Graph object representing the Gene Ontology graph. It should contain 'nodes' and 'edges'.
	go_id (str): The GO term identifier for which GeneProducts are to be retrieved.
	recursive (bool): If False, only direct predecessors of type GeneProduct are returned.
					  If True, all ancestors of type GeneProduct connected by a path are returned.

	Returns:
	list: A list of GeneProducts linked to the given GO term.

	Notes:
	- The 'go' dictionary should have the following structure:
	  {'nodes': {node_id: {'type': 'NodeType', ...}, ...},'edges': [(source_node_id, {'target': target_node_id, ...}), ...]}
	- The function uses a helper function `predecessors` to find direct predecessors of a node.
	- If `recursive` is True, another helper function `get_ancestors` is used to find all ancestors.
	"""
	if not recursive:
		if go_id in go.nodes:
			# Return direct predecessors of type GeneProduct
			return [node for node in predecessors(go, go_id) if go.nodes[node]['type'] == 'GeneProduct']
	else:
		def get_ancestors(go, node, ancestors):
			"""
			Recursively find all ancestors of type GeneProduct connected by a path.
			"""
			for neighbor in predecessors(go, node):
				if go.nodes[neighbor]['type'] == 'GeneProduct' and neighbor not in ancestors:
					# Add the neighbor to ancestors set
					ancestors.add(neighbor)
				# Recursively find ancestors of the neighbor
				get_ancestors(go, neighbor, ancestors)

		ancestors = set()
		if go_id in go.nodes:
			# Start finding ancestors from the given GO term ID
			get_ancestors(go, go_id, ancestors)
		# Return the list of all ancestors
		return list(ancestors)

def ascendants(go:Graph, start_node):
	"""
	Find all ascendants of a node in a directed acyclic graph (DAG).
	"""
	return go.get_ascendants(start_node)

def descendants(go:Graph, start_node):
	"""
	Find all descendants of a node in a directed acyclic graph (DAG).
	"""
	return go.get_descendants(start_node)

def successors(go:Graph, start_node):
	"""
	Find all successors of a node in a directed acyclic graph (DAG).
	"""
	return go.get_successors(start_node)

def predecessors(go:Graph, start_node):
	"""
	Find all predecessors of a node in a directed acyclic graph (DAG).
	"""
	return go.get_predecessors(start_node)


##### main → tests #####
if __name__ == "__main__":
	try:
		filename_goa = sys.argv[1]
	except:
		# Check if the file exists, if not, download it
		filename_goa = "data/122.R_norvegicus.goa"
		if not os.path.exists(filename_goa):
			url = "http://ftp.ebi.ac.uk/pub/databases/GO/goa/proteomes/122.R_norvegicus.goa"
			print(f"File 122.R_norvegicus.goa not found in data/.\nDownloading from {url}...")
			urllib.request.urlretrieve(url, filename_goa)
			print("Downloaded 122.R_norvegicus.goa")
	
 	# Load Graph
    
	print("# Gene Ontology module tests")
	# Load Gene Ontology graph
	go = load_OBO()
	print(f"GO graph: {len(go.nodes)} nodes, {len(go.edges)} edges")
	# Load Gene Ontology Annotations
	load_GOA(go, filename_goa)
	print(f"GO graph: {len(go.nodes)} nodes, {len(go.edges)} edges")
 
	# Test non-recursive functions
 
	## Test GOTerms
	print("\n# Test GOTerms")
	gp_id = 'A0A023IKK2'
	go_terms = GOTerms(go, gp_id)
	print(f"GO terms for gene product {gp_id}: {go_terms}")
	## Test GeneProducts
	print("\n# Test GeneProducts")
	go_id = 'GO:0042742'
	gene_products = GeneProducts(go, go_id)
	print(f"Gene products linked to GO term {go_id}: {gene_products}")
	 
	# Test recursive functions
 
	## Test GOTerms (recursive)
	print("\n# Test GOTerms (recursive)")
	gp_id = 'A0A023IKK2'
	go_terms = GOTerms(go, gp_id, recursive=True)
	print(f"GO terms for gene product {gp_id} (recursive): {go_terms}")
	## Test GeneProducts (recursive)
	print("\n# Test GeneProducts (recursive)")
	go_id = 'GO:0042742'
	gene_products = GeneProducts(go, go_id, recursive=True)
	print(f"Gene products linked to GO term {go_id} (recursive): {gene_products}")
 
	# Test max depth function
	print("\n# Test max_depth")
	max_d = go.max_depth()
	print(f"Maximum depth of the GO graph: {max_d}")
