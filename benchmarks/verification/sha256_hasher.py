"""SHA256 Hasher - Cryptographic hashing for benchmark results."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SHA256Hasher:
    """Generate SHA256 hashes for verification."""

    def __init__(self) -> None:
        """Initialize SHA256 hasher."""
        self.hashes: List[Dict[str, str]] = []

    def hash_file(self, filepath: str) -> str:
        """Calculate SHA256 hash of a file.

        Args:
            filepath: Path to file

        Returns:
            Hex-encoded SHA256 hash
        """
        sha256 = hashlib.sha256()

        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        file_hash = sha256.hexdigest()
        logger.info(f"Hashed {filepath}: {file_hash}")

        return file_hash

    def hash_data(self, data: bytes) -> str:
        """Calculate SHA256 hash of data.

        Args:
            data: Data to hash

        Returns:
            Hex-encoded SHA256 hash
        """
        return hashlib.sha256(data).hexdigest()

    def hash_json(self, data: Dict[str, Any]) -> str:
        """Calculate SHA256 hash of JSON data.

        Args:
            data: Dictionary to hash

        Returns:
            Hex-encoded SHA256 hash
        """
        # Serialize with sorted keys for consistency
        json_bytes = json.dumps(data, sort_keys=True).encode()
        return self.hash_data(json_bytes)

    def hash_benchmark_results(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Hash benchmark results for verification.

        Args:
            results: Benchmark results dictionary

        Returns:
            Dictionary with result hash and metadata hash
        """
        # Hash full results
        full_hash = self.hash_json(results)

        # Hash metadata only (without detailed results)
        metadata = {k: v for k, v in results.items() if k != "results"}
        metadata_hash = self.hash_json(metadata)

        hash_record = {
            "full_hash": full_hash,
            "metadata_hash": metadata_hash,
            "timestamp": results.get("timestamp", "unknown"),
            "benchmark": results.get("benchmark", "unknown"),
        }

        self.hashes.append(hash_record)

        return hash_record

    def verify_hash(self, data: Dict[str, Any], expected_hash: str) -> bool:
        """Verify data against expected hash.

        Args:
            data: Data to verify
            expected_hash: Expected SHA256 hash

        Returns:
            True if hash matches
        """
        actual_hash = self.hash_json(data)
        matches = actual_hash == expected_hash

        logger.info(f"Hash verification: {matches}")
        return matches

    def save_hashes(self, output_path: str) -> None:
        """Save hash records to file.

        Args:
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(self.hashes, f, indent=2)

        logger.info(f"Saved {len(self.hashes)} hash records to: {output_path}")
