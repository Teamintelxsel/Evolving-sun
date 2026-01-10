"""Graph Builder - Constructs NetworkX graphs from KEGG pathways."""

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import networkx as nx

logger = logging.getLogger(__name__)


class KEGGGraphBuilder:
    """Builds directed graphs from KEGG pathway data."""

    def __init__(self) -> None:
        """Initialize the graph builder."""
        self.graphs: Dict[str, nx.DiGraph] = {}

    def build_from_kgml(self, kgml_xml: str, pathway_id: str) -> Optional[nx.DiGraph]:
        """Build a NetworkX graph from KGML XML.

        Args:
            kgml_xml: KGML XML string
            pathway_id: Pathway identifier

        Returns:
            NetworkX DiGraph or None if parsing fails
        """
        try:
            root = ET.fromstring(kgml_xml)
            graph = nx.DiGraph(pathway_id=pathway_id, name=root.get("title", ""))

            # Parse entries (nodes)
            entries = {}
            for entry in root.findall("entry"):
                entry_id = entry.get("id")
                entry_type = entry.get("type")
                entry_name = entry.get("name", "")

                entries[entry_id] = {
                    "type": entry_type,
                    "name": entry_name,
                    "reaction": entry.get("reaction", ""),
                }

                graph.add_node(
                    entry_id,
                    type=entry_type,
                    name=entry_name,
                    reaction=entry.get("reaction", ""),
                )

            # Parse relations (edges)
            for relation in root.findall("relation"):
                entry1 = relation.get("entry1")
                entry2 = relation.get("entry2")
                rel_type = relation.get("type")

                if entry1 in entries and entry2 in entries:
                    graph.add_edge(entry1, entry2, type=rel_type)

                    # Add subtypes if available
                    for subtype in relation.findall("subtype"):
                        graph[entry1][entry2][subtype.get("name")] = subtype.get("value")

            # Parse reactions
            for reaction in root.findall("reaction"):
                reaction_id = reaction.get("id")
                reaction_type = reaction.get("type")

                # Add reaction substrates and products
                substrates = [s.get("id") for s in reaction.findall("substrate")]
                products = [p.get("id") for p in reaction.findall("product")]

                for substrate in substrates:
                    for product in products:
                        if substrate in graph.nodes and product in graph.nodes:
                            graph.add_edge(
                                substrate, product, type="reaction", reaction_id=reaction_id
                            )

            self.graphs[pathway_id] = graph
            logger.info(
                f"Built graph for {pathway_id}: {graph.number_of_nodes()} nodes, "
                f"{graph.number_of_edges()} edges"
            )
            return graph

        except ET.ParseError as e:
            logger.error(f"Failed to parse KGML XML for {pathway_id}: {e}")
            return None

    def build_from_pathway_data(self, pathway_data: Dict[str, Any]) -> nx.DiGraph:
        """Build a simplified graph from pathway data dictionary.

        Args:
            pathway_data: Pathway data from KEGGPathwayFetcher

        Returns:
            NetworkX DiGraph
        """
        pathway_id = pathway_data.get("id", "unknown")
        graph = nx.DiGraph(
            pathway_id=pathway_id, name=pathway_data.get("name", ""), source="simplified"
        )

        # Add genes as nodes
        for idx, gene in enumerate(pathway_data.get("genes", [])):
            node_id = f"gene_{idx}"
            graph.add_node(node_id, type="gene", name=gene)

        # Add compounds as nodes
        for idx, compound in enumerate(pathway_data.get("compounds", [])):
            node_id = f"compound_{idx}"
            graph.add_node(node_id, type="compound", name=compound)

        logger.info(
            f"Built simplified graph for {pathway_id}: {graph.number_of_nodes()} nodes"
        )
        return graph

    def analyze_graph_structure(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze the structure of a pathway graph.

        Args:
            graph: NetworkX DiGraph

        Returns:
            Dictionary containing graph statistics
        """
        analysis: Dict[str, Any] = {
            "num_nodes": graph.number_of_nodes(),
            "num_edges": graph.number_of_edges(),
            "is_dag": nx.is_directed_acyclic_graph(graph),
            "num_weakly_connected_components": nx.number_weakly_connected_components(graph),
            "density": nx.density(graph),
        }

        # Identify branching points (nodes with multiple outgoing edges)
        branching_points = [node for node in graph.nodes() if graph.out_degree(node) > 1]
        analysis["branching_points"] = len(branching_points)
        analysis["branching_nodes"] = branching_points[:10]  # Sample of branching nodes

        # Identify convergence points (nodes with multiple incoming edges)
        convergence_points = [node for node in graph.nodes() if graph.in_degree(node) > 1]
        analysis["convergence_points"] = len(convergence_points)
        analysis["convergence_nodes"] = convergence_points[:10]

        # Identify catalytic nodes (specific node types)
        if graph.number_of_nodes() > 0:
            node_types = {}
            for node in graph.nodes():
                node_type = graph.nodes[node].get("type", "unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1
            analysis["node_types"] = node_types

        return analysis

    def find_mutation_candidates(self, graph: nx.DiGraph) -> List[Dict[str, Any]]:
        """Identify mutation candidates from graph structure.

        Args:
            graph: NetworkX DiGraph

        Returns:
            List of mutation candidate dictionaries
        """
        candidates = []

        # Branching pathways → Function decomposition
        for node in graph.nodes():
            if graph.out_degree(node) > 1:
                candidates.append(
                    {
                        "type": "branching_pathway",
                        "mutation_operator": "function_decomposition",
                        "node": node,
                        "out_degree": graph.out_degree(node),
                        "successors": list(graph.successors(node)),
                    }
                )

        # Catalytic reactions → Code insertion/optimization
        for node in graph.nodes():
            if graph.nodes[node].get("type") == "enzyme":
                candidates.append(
                    {
                        "type": "catalytic_reaction",
                        "mutation_operator": "code_optimization",
                        "node": node,
                        "reaction": graph.nodes[node].get("reaction", ""),
                    }
                )

        # Linear chains → Potential for combination
        try:
            for path in nx.all_simple_paths(graph, source=None, target=None, cutoff=5):
                if len(path) >= 3:
                    # Check if it's a linear chain
                    is_linear = all(
                        graph.out_degree(path[i]) == 1 for i in range(len(path) - 1)
                    )
                    if is_linear:
                        candidates.append(
                            {
                                "type": "linear_chain",
                                "mutation_operator": "module_combination",
                                "path": path,
                                "length": len(path),
                            }
                        )
                        break  # Limit to prevent excessive computation
        except (nx.NetworkXError, TypeError):
            # Skip if path finding fails
            pass

        logger.info(f"Found {len(candidates)} mutation candidates")
        return candidates

    def get_graph(self, pathway_id: str) -> Optional[nx.DiGraph]:
        """Retrieve a built graph by pathway ID.

        Args:
            pathway_id: Pathway identifier

        Returns:
            NetworkX DiGraph or None if not found
        """
        return self.graphs.get(pathway_id)

    def export_graph(self, pathway_id: str, format: str = "gml") -> Optional[str]:
        """Export graph to various formats.

        Args:
            pathway_id: Pathway identifier
            format: Export format ('gml', 'graphml', 'json')

        Returns:
            Exported graph string or None if graph not found
        """
        graph = self.graphs.get(pathway_id)
        if graph is None:
            logger.error(f"Graph not found for pathway: {pathway_id}")
            return None

        try:
            if format == "gml":
                from io import StringIO

                output = StringIO()
                nx.write_gml(graph, output)
                return output.getvalue()
            elif format == "graphml":
                from io import BytesIO

                output = BytesIO()
                nx.write_graphml(graph, output)
                return output.getvalue().decode("utf-8")
            elif format == "json":
                from networkx.readwrite import json_graph

                return str(json_graph.node_link_data(graph))
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return None
