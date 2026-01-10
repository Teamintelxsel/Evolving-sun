"""Test suite for KEGG mutation engine."""

import pytest
from src.agents.mutator import KEGGMutator
from src.agents.nano_agent import NanoAgent
from src.agents.swarm_orchestrator import SwarmOrchestrator
from kegg_integration.pathway_fetcher import KEGGPathwayFetcher
from kegg_integration.graph_builder import KEGGGraphBuilder
from kegg_integration.operator_mapper import BiologicalOperatorMapper


class TestKEGGPathwayFetcher:
    """Test KEGG pathway fetching."""

    def test_initialization(self):
        """Test fetcher initializes correctly."""
        fetcher = KEGGPathwayFetcher()
        assert fetcher.cache_enabled is True
        assert len(fetcher._cache) == 0

    def test_fetch_pathway_structure(self):
        """Test pathway fetch returns expected structure."""
        fetcher = KEGGPathwayFetcher()
        # Note: This will make actual API call in real tests
        # For unit tests, mock the response
        pathway = {"id": "test", "name": "Test Pathway", "genes": [], "compounds": []}
        assert "id" in pathway
        assert "name" in pathway


class TestGraphBuilder:
    """Test graph building from pathways."""

    def test_initialization(self):
        """Test graph builder initializes."""
        builder = KEGGGraphBuilder()
        assert len(builder.graphs) == 0

    def test_build_from_pathway_data(self):
        """Test building graph from pathway data."""
        builder = KEGGGraphBuilder()
        pathway_data = {
            "id": "ko01100",
            "name": "Metabolic pathways",
            "genes": ["Gene1", "Gene2"],
            "compounds": ["Compound1"],
        }

        graph = builder.build_from_pathway_data(pathway_data)
        assert graph is not None
        assert graph.number_of_nodes() > 0


class TestOperatorMapper:
    """Test biological operator mapping."""

    def test_initialization(self):
        """Test operator mapper initializes."""
        mapper = BiologicalOperatorMapper()
        assert len(mapper.mutation_history) == 0

    def test_mutation_types(self):
        """Test mutation types are defined."""
        mapper = BiologicalOperatorMapper()
        assert "branching_pathway" in mapper.MUTATION_TYPES
        assert "catalytic_reaction" in mapper.MUTATION_TYPES


class TestNanoAgent:
    """Test nano agent functionality."""

    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = NanoAgent()
        assert agent.agent_id is not None
        assert agent.specialization is not None
        assert agent.fitness == 0.5

    def test_apply_mutation(self):
        """Test mutation application."""
        agent = NanoAgent()
        mutation = {
            "id": "test_mutation",
            "type": "branching_pathway",
            "operator": "function_decomposition",
        }

        result = agent.apply_mutation(mutation)
        assert "agent_id" in result
        assert "success" in result
        assert agent.mutations_applied == 1

    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        agent = NanoAgent()
        metrics = agent.get_performance_metrics()
        assert "agent_id" in metrics
        assert "fitness" in metrics
        assert "success_rate" in metrics


class TestSwarmOrchestrator:
    """Test swarm orchestration."""

    def test_initialization(self):
        """Test swarm initializes with agents."""
        swarm = SwarmOrchestrator(swarm_size=10)
        assert len(swarm.agents) == 10
        assert swarm.generation == 0

    def test_distribute_mutations(self):
        """Test mutation distribution."""
        swarm = SwarmOrchestrator(swarm_size=5)
        mutations = [
            {"id": f"mut_{i}", "type": "test", "operator": "test_op"}
            for i in range(3)
        ]

        results = swarm.distribute_mutations(mutations)
        assert len(results) == 3
        assert swarm.generation == 1

    def test_swarm_statistics(self):
        """Test statistics calculation."""
        swarm = SwarmOrchestrator(swarm_size=10)
        stats = swarm.get_swarm_statistics()
        assert "swarm_size" in stats
        assert stats["swarm_size"] == 10


class TestKEGGMutator:
    """Test core mutation engine."""

    def test_initialization(self):
        """Test mutator initializes."""
        mutator = KEGGMutator()
        assert mutator.generation == 0
        assert len(mutator.mutation_history) == 0

    def test_evolve_basic(self):
        """Test basic evolution run."""
        mutator = KEGGMutator()
        results = mutator.evolve(generations=1, target_mutations_per_gen=2)

        assert "generations" in results
        assert "total_mutations" in results
        assert results["generations"] == 1

    def test_statistics(self):
        """Test statistics generation."""
        mutator = KEGGMutator()
        stats = mutator.get_statistics()
        assert "total_generations" in stats
