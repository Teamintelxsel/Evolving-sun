"""KEGG Pathway Fetcher - REST API wrapper for fetching KEGG metabolic pathways."""

import logging
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class KEGGPathwayFetcher:
    """Wrapper for KEGG REST API to fetch metabolic pathways."""

    BASE_URL = "https://rest.kegg.jp"
    RATE_LIMIT_DELAY = 0.5  # Respect KEGG's rate limits

    def __init__(self, cache_enabled: bool = True) -> None:
        """Initialize the KEGG pathway fetcher.

        Args:
            cache_enabled: Whether to cache fetched pathways
        """
        self.cache_enabled = cache_enabled
        self._cache: Dict[str, Any] = {}
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "Evolving-Sun/0.2.0"})

    def fetch_pathway(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific KEGG pathway by ID.

        Args:
            pathway_id: KEGG pathway identifier (e.g., 'ko01100')

        Returns:
            Dictionary containing pathway data or None if fetch fails
        """
        if self.cache_enabled and pathway_id in self._cache:
            logger.info(f"Returning cached pathway: {pathway_id}")
            return self._cache[pathway_id]

        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            url = f"{self.BASE_URL}/get/{pathway_id}"
            response = self._session.get(url, timeout=30)
            response.raise_for_status()

            pathway_data = self._parse_pathway_response(response.text, pathway_id)

            if self.cache_enabled:
                self._cache[pathway_id] = pathway_data

            logger.info(f"Successfully fetched pathway: {pathway_id}")
            return pathway_data

        except requests.RequestException as e:
            logger.error(f"Failed to fetch pathway {pathway_id}: {e}")
            return None

    def fetch_pathway_list(self, organism: str = "ko") -> List[str]:
        """Fetch list of available pathways for an organism.

        Args:
            organism: KEGG organism code (default: 'ko' for KEGG Orthology)

        Returns:
            List of pathway IDs
        """
        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            url = f"{self.BASE_URL}/list/pathway/{organism}"
            response = self._session.get(url, timeout=30)
            response.raise_for_status()

            pathways = []
            for line in response.text.strip().split("\n"):
                if line:
                    pathway_id = line.split("\t")[0]
                    pathways.append(pathway_id)

            logger.info(f"Fetched {len(pathways)} pathways for organism: {organism}")
            return pathways

        except requests.RequestException as e:
            logger.error(f"Failed to fetch pathway list for {organism}: {e}")
            return []

    def fetch_pathway_kgml(self, pathway_id: str) -> Optional[str]:
        """Fetch pathway in KGML (KEGG Markup Language) format.

        Args:
            pathway_id: KEGG pathway identifier

        Returns:
            KGML XML string or None if fetch fails
        """
        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            url = f"{self.BASE_URL}/get/{pathway_id}/kgml"
            response = self._session.get(url, timeout=30)
            response.raise_for_status()

            logger.info(f"Successfully fetched KGML for pathway: {pathway_id}")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Failed to fetch KGML for {pathway_id}: {e}")
            return None

    def fetch_reaction(self, reaction_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific KEGG reaction.

        Args:
            reaction_id: KEGG reaction identifier (e.g., 'R00001')

        Returns:
            Dictionary containing reaction data or None if fetch fails
        """
        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            url = f"{self.BASE_URL}/get/{reaction_id}"
            response = self._session.get(url, timeout=30)
            response.raise_for_status()

            reaction_data = self._parse_reaction_response(response.text, reaction_id)
            logger.info(f"Successfully fetched reaction: {reaction_id}")
            return reaction_data

        except requests.RequestException as e:
            logger.error(f"Failed to fetch reaction {reaction_id}: {e}")
            return None

    def _parse_pathway_response(self, text: str, pathway_id: str) -> Dict[str, Any]:
        """Parse KEGG pathway response text.

        Args:
            text: Response text from KEGG API
            pathway_id: Pathway identifier

        Returns:
            Parsed pathway data
        """
        data: Dict[str, Any] = {"id": pathway_id, "name": "", "genes": [], "compounds": []}

        current_section = None
        for line in text.split("\n"):
            if not line.strip():
                continue

            if line.startswith("NAME"):
                data["name"] = line[12:].strip()
            elif line.startswith("GENE"):
                current_section = "GENE"
                gene_info = line[12:].strip()
                if gene_info:
                    data["genes"].append(gene_info)
            elif line.startswith("COMPOUND"):
                current_section = "COMPOUND"
                compound_info = line[12:].strip()
                if compound_info:
                    data["compounds"].append(compound_info)
            elif current_section == "GENE" and line.startswith(" "):
                data["genes"].append(line.strip())
            elif current_section == "COMPOUND" and line.startswith(" "):
                data["compounds"].append(line.strip())
            elif line.startswith("///"):
                break

        return data

    def _parse_reaction_response(self, text: str, reaction_id: str) -> Dict[str, Any]:
        """Parse KEGG reaction response text.

        Args:
            text: Response text from KEGG API
            reaction_id: Reaction identifier

        Returns:
            Parsed reaction data
        """
        data: Dict[str, Any] = {
            "id": reaction_id,
            "name": "",
            "equation": "",
            "enzymes": [],
        }

        for line in text.split("\n"):
            if not line.strip():
                continue

            if line.startswith("NAME"):
                data["name"] = line[12:].strip()
            elif line.startswith("EQUATION"):
                data["equation"] = line[12:].strip()
            elif line.startswith("ENZYME"):
                enzyme_info = line[12:].strip()
                if enzyme_info:
                    data["enzymes"].append(enzyme_info)
            elif line.startswith("///"):
                break

        return data

    def clear_cache(self) -> None:
        """Clear the pathway cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    def close(self) -> None:
        """Close the session."""
        self._session.close()
