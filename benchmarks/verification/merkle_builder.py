"""Merkle Tree Builder - Construct Merkle trees for result verification."""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MerkleTreeBuilder:
    """Build Merkle trees for cryptographic verification of results."""

    def __init__(self) -> None:
        """Initialize Merkle tree builder."""
        self.trees: List[Dict[str, Any]] = []

    def hash_leaf(self, data: str) -> str:
        """Hash a leaf node.

        Args:
            data: Leaf data

        Returns:
            SHA256 hash
        """
        return hashlib.sha256(data.encode()).hexdigest()

    def hash_pair(self, left: str, right: str) -> str:
        """Hash a pair of nodes.

        Args:
            left: Left node hash
            right: Right node hash

        Returns:
            Combined hash
        """
        return hashlib.sha256((left + right).encode()).hexdigest()

    def build_tree(self, leaves: List[str]) -> Dict[str, Any]:
        """Build a Merkle tree from leaf data.

        Args:
            leaves: List of leaf data strings

        Returns:
            Merkle tree dictionary
        """
        if not leaves:
            return {"root": "", "leaves": [], "levels": []}

        # Hash all leaves
        leaf_hashes = [self.hash_leaf(leaf) for leaf in leaves]

        # Build tree levels
        levels = [leaf_hashes]

        while len(levels[-1]) > 1:
            current_level = levels[-1]
            next_level = []

            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = self.hash_pair(left, right)
                next_level.append(parent)

            levels.append(next_level)

        root = levels[-1][0]

        tree = {
            "root": root,
            "leaves": leaf_hashes,
            "levels": levels,
            "leaf_count": len(leaves),
        }

        self.trees.append(tree)
        logger.info(f"Built Merkle tree: root={root[:16]}..., {len(leaves)} leaves")

        return tree

    def build_from_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build Merkle tree from benchmark results.

        Args:
            results: List of result dictionaries

        Returns:
            Merkle tree
        """
        # Convert results to leaf strings
        leaves = [json.dumps(result, sort_keys=True) for result in results]
        return self.build_tree(leaves)

    def verify_leaf(
        self, leaf_data: str, proof: List[str], root: str
    ) -> bool:
        """Verify a leaf is in the tree using a Merkle proof.

        Args:
            leaf_data: Original leaf data
            proof: List of sibling hashes from leaf to root
            root: Expected root hash

        Returns:
            True if leaf is valid
        """
        current_hash = self.hash_leaf(leaf_data)

        for sibling in proof:
            # Combine with sibling (order matters)
            if current_hash < sibling:
                current_hash = self.hash_pair(current_hash, sibling)
            else:
                current_hash = self.hash_pair(sibling, current_hash)

        is_valid = current_hash == root
        logger.info(f"Merkle proof verification: {is_valid}")
        return is_valid

    def generate_proof(
        self, tree: Dict[str, Any], leaf_index: int
    ) -> List[str]:
        """Generate Merkle proof for a specific leaf.

        Args:
            tree: Merkle tree
            leaf_index: Index of leaf to prove

        Returns:
            List of sibling hashes
        """
        if leaf_index >= len(tree["leaves"]):
            return []

        proof = []
        levels = tree["levels"]

        current_index = leaf_index

        for level in levels[:-1]:  # Exclude root level
            # Get sibling
            if current_index % 2 == 0:
                # Left node, sibling is to the right
                sibling_index = current_index + 1
            else:
                # Right node, sibling is to the left
                sibling_index = current_index - 1

            if sibling_index < len(level):
                proof.append(level[sibling_index])
            else:
                # No sibling (odd number of nodes), use current
                proof.append(level[current_index])

            current_index = current_index // 2

        return proof

    def save_tree(self, tree: Dict[str, Any], output_path: str) -> None:
        """Save Merkle tree to file.

        Args:
            tree: Merkle tree
            output_path: Output file path
        """
        from pathlib import Path

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(tree, f, indent=2)

        logger.info(f"Merkle tree saved to: {output_path}")

    def get_tree_stats(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about a Merkle tree.

        Args:
            tree: Merkle tree

        Returns:
            Statistics dictionary
        """
        return {
            "root_hash": tree["root"],
            "leaf_count": tree["leaf_count"],
            "tree_depth": len(tree["levels"]),
            "total_nodes": sum(len(level) for level in tree["levels"]),
        }
