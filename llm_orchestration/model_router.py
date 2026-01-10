"""Model Router - Smart routing across multiple LLM providers."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelRouter:
    """Routes requests to optimal LLM based on cost, latency, and capabilities."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize model router.

        Args:
            config_path: Path to model configuration file
        """
        self.config_path = config_path
        self.models = self._load_models()
        self.request_count = 0
        self.route_history: List[Dict[str, Any]] = []

    def _load_models(self) -> Dict[str, Dict[str, Any]]:
        """Load model configurations.

        Returns:
            Dictionary of model configurations
        """
        # Default model configurations
        return {
            "grok-4": {
                "provider": "xai",
                "cost_per_1k_tokens": 0.015,
                "latency_ms": 800,
                "capabilities": ["reasoning", "coding", "analysis"],
                "context_window": 128000,
                "priority": 1,
            },
            "claude-opus-4.5": {
                "provider": "anthropic",
                "cost_per_1k_tokens": 0.075,
                "latency_ms": 1200,
                "capabilities": ["coding", "analysis", "long-context"],
                "context_window": 200000,
                "priority": 2,
            },
            "gemini-3-flash": {
                "provider": "google",
                "cost_per_1k_tokens": 0.002,
                "latency_ms": 300,
                "capabilities": ["speed", "basic-reasoning"],
                "context_window": 32000,
                "priority": 3,
            },
            "llama-4": {
                "provider": "meta",
                "cost_per_1k_tokens": 0.0,
                "latency_ms": 500,
                "capabilities": ["open-source", "self-hosted"],
                "context_window": 16000,
                "priority": 4,
            },
            "qwen-3": {
                "provider": "alibaba",
                "cost_per_1k_tokens": 0.003,
                "latency_ms": 600,
                "capabilities": ["multilingual", "reasoning"],
                "context_window": 32000,
                "priority": 5,
            },
            "deepseek": {
                "provider": "deepseek",
                "cost_per_1k_tokens": 0.004,
                "latency_ms": 700,
                "capabilities": ["coding", "reasoning"],
                "context_window": 64000,
                "priority": 6,
            },
        }

    def route_request(
        self,
        task_type: str,
        max_cost: Optional[float] = None,
        max_latency: Optional[int] = None,
        required_capabilities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Route request to optimal model.

        Args:
            task_type: Type of task (e.g., 'coding', 'reasoning')
            max_cost: Maximum cost per 1k tokens
            max_latency: Maximum acceptable latency in ms
            required_capabilities: Required model capabilities

        Returns:
            Selected model information
        """
        self.request_count += 1

        # Filter models by constraints
        candidates = []
        for model_name, config in self.models.items():
            # Check cost constraint
            if max_cost and config["cost_per_1k_tokens"] > max_cost:
                continue

            # Check latency constraint
            if max_latency and config["latency_ms"] > max_latency:
                continue

            # Check capabilities
            if required_capabilities:
                if not all(
                    cap in config["capabilities"] for cap in required_capabilities
                ):
                    continue

            candidates.append((model_name, config))

        if not candidates:
            # Fallback to cheapest model
            logger.warning("No models meet constraints, using fallback")
            candidates = [
                (name, cfg)
                for name, cfg in self.models.items()
                if cfg["cost_per_1k_tokens"] == 0
            ]
            if not candidates:
                candidates = list(self.models.items())

        # Sort by priority (lower is better)
        candidates.sort(key=lambda x: x[1]["priority"])

        selected_model, selected_config = candidates[0]

        routing_decision = {
            "model": selected_model,
            "provider": selected_config["provider"],
            "cost_per_1k_tokens": selected_config["cost_per_1k_tokens"],
            "latency_ms": selected_config["latency_ms"],
            "task_type": task_type,
            "request_id": self.request_count,
        }

        self.route_history.append(routing_decision)

        logger.info(
            f"Routed request #{self.request_count} to {selected_model} "
            f"(cost: ${selected_config['cost_per_1k_tokens']}/1k, "
            f"latency: {selected_config['latency_ms']}ms)"
        )

        return routing_decision

    def get_model_for_task(self, task_type: str) -> str:
        """Get recommended model for a specific task type.

        Args:
            task_type: Type of task

        Returns:
            Model name
        """
        task_to_model = {
            "reasoning": "grok-4",
            "coding": "claude-opus-4.5",
            "speed": "gemini-3-flash",
            "open-source": "llama-4",
            "multilingual": "qwen-3",
            "analysis": "deepseek",
        }

        return task_to_model.get(task_type, "gemini-3-flash")

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics.

        Returns:
            Statistics dictionary
        """
        if not self.route_history:
            return {"total_requests": 0, "models_used": {}, "avg_cost": 0.0}

        models_used: Dict[str, int] = {}
        total_cost = 0.0

        for decision in self.route_history:
            model = decision["model"]
            models_used[model] = models_used.get(model, 0) + 1
            total_cost += decision["cost_per_1k_tokens"]

        return {
            "total_requests": len(self.route_history),
            "models_used": models_used,
            "avg_cost": total_cost / len(self.route_history),
            "total_estimated_cost": total_cost,
        }

    def optimize_for_cost(self) -> str:
        """Get the cheapest model.

        Returns:
            Model name
        """
        sorted_models = sorted(
            self.models.items(), key=lambda x: x[1]["cost_per_1k_tokens"]
        )
        return sorted_models[0][0]

    def optimize_for_latency(self) -> str:
        """Get the fastest model.

        Returns:
            Model name
        """
        sorted_models = sorted(self.models.items(), key=lambda x: x[1]["latency_ms"])
        return sorted_models[0][0]
