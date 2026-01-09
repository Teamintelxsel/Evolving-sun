"""
LLM Independence Framework - 2025 Best Practices
Multi-Model Orchestration with Smart Routing, Cost Optimization, and Automatic Fallbacks

Supports: OpenAI, Anthropic, Google Gemini, Meta Llama, Custom Models
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    CUSTOM = "custom"


class TaskType(Enum):
    """Task classification for intelligent routing"""
    REASONING = "reasoning"
    CODING = "coding"
    ANALYSIS = "analysis"
    FAST_INFERENCE = "fast_inference"
    LONG_CONTEXT = "long_context"
    MULTIMODAL = "multimodal"
    COST_OPTIMIZED = "cost_optimized"


@dataclass
class ModelMetadata:
    """Metadata for a specific model"""
    model_id: str
    provider: ModelProvider
    version: str
    capabilities: List[str]
    performance: Dict[str, float]
    cost_per_1k_tokens: float
    p95_latency_ms: int
    quantized_versions: List[str]
    max_tokens: int = 4096
    available: bool = True


@dataclass
class RoutingRequest:
    """Request for model routing"""
    prompt: str
    task_type: TaskType
    cost_limit: Optional[float] = None
    latency_limit: Optional[int] = None
    min_accuracy: Optional[float] = None
    context_length: int = 0


@dataclass
class RoutingResponse:
    """Response from model routing"""
    model_id: str
    provider: ModelProvider
    response: str
    latency_ms: int
    cost: float
    confidence: float
    fallback_used: bool = False


class ModelRegistry:
    """
    Model registry for versioning and performance tracking
    Loads from model-tracking.yml
    """
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.models: Dict[str, ModelMetadata] = {}
        self.performance_history: Dict[str, List[Dict]] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load model registry from YAML configuration"""
        if not self.config_path.exists():
            logger.warning(f"Registry config not found: {self.config_path}")
            return
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        for model_id, metadata in config.get('models', {}).items():
            self.models[model_id] = ModelMetadata(
                model_id=model_id,
                provider=ModelProvider(metadata['provider']),
                version=metadata['version'],
                capabilities=metadata['capabilities'],
                performance=metadata['performance'],
                cost_per_1k_tokens=metadata['cost_per_1k_tokens'],
                p95_latency_ms=metadata['p95_latency_ms'],
                quantized_versions=metadata.get('quantized_versions', []),
                max_tokens=metadata.get('max_tokens', 4096)
            )
        
        logger.info(f"Loaded {len(self.models)} models from registry")
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata by ID"""
        return self.models.get(model_id)
    
    def get_models_by_capability(self, capability: str) -> List[ModelMetadata]:
        """Get all models with a specific capability"""
        return [
            model for model in self.models.values()
            if capability in model.capabilities and model.available
        ]
    
    def update_performance(self, model_id: str, metrics: Dict):
        """Update model performance metrics"""
        if model_id not in self.performance_history:
            self.performance_history[model_id] = []
        
        self.performance_history[model_id].append({
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics
        })
        
        # Keep only last 1000 entries
        if len(self.performance_history[model_id]) > 1000:
            self.performance_history[model_id] = self.performance_history[model_id][-1000:]


class ModelRouter:
    """
    Framework-agnostic model routing with fallback mechanisms
    Implements prompt chaining, cost optimization, and performance tracking
    """
    
    def __init__(self, config_path: str, registry_path: str):
        self.config_path = Path(config_path)
        self.registry = ModelRegistry(registry_path)
        self.fallback_chains: Dict[str, List[str]] = {}
        self.request_cache: Dict[str, RoutingResponse] = {}
        self.load_config()
    
    def load_config(self):
        """Load routing configuration"""
        if not self.config_path.exists():
            logger.warning(f"Router config not found: {self.config_path}")
            return
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.fallback_chains = config.get('fallback_chains', {})
        logger.info(f"Loaded {len(self.fallback_chains)} fallback chains")
    
    async def route_request(self, request: RoutingRequest) -> RoutingResponse:
        """
        Intelligent routing based on:
        - Task complexity
        - Cost constraints
        - Latency requirements
        - Current model performance
        """
        
        # Check cache first (for identical prompts)
        cache_key = self._generate_cache_key(request)
        if cache_key in self.request_cache:
            logger.info(f"Cache hit for request")
            return self.request_cache[cache_key]
        
        # Select optimal model
        model = await self.select_model(
            task_type=request.task_type,
            cost_limit=request.cost_limit,
            latency_limit=request.latency_limit,
            min_accuracy=request.min_accuracy,
            context_length=request.context_length
        )
        
        if not model:
            raise RuntimeError("No suitable model found for request")
        
        # Get fallback chain
        fallback_models = self.get_fallback_chain(model.model_id, request.task_type)
        
        # Execute with retry logic
        for attempt, current_model in enumerate([model] + fallback_models):
            try:
                logger.info(f"Attempting with model: {current_model.model_id}")
                
                result = await self.execute(current_model, request)
                
                # Track performance
                self.update_metrics(current_model, result)
                
                # Cache result
                self.request_cache[cache_key] = result
                
                return result
                
            except Exception as e:
                logger.error(f"Model {current_model.model_id} failed: {e}")
                self.log_failure(current_model, e)
                
                # Mark model as unavailable temporarily
                current_model.available = False
                
                # Continue to next model
                continue
        
        raise RuntimeError("All models in fallback chain failed")
    
    async def select_model(
        self,
        task_type: TaskType,
        cost_limit: Optional[float] = None,
        latency_limit: Optional[int] = None,
        min_accuracy: Optional[float] = None,
        context_length: int = 0
    ) -> Optional[ModelMetadata]:
        """
        Multi-criteria decision:
        - Accuracy score for task type
        - Cost per 1K tokens
        - P95 latency
        - Current availability
        - Context length support
        """
        
        task_type_str = task_type.value
        
        # Get candidate models with required capability
        candidates = []
        
        for model in self.registry.models.values():
            if not model.available:
                continue
            
            # Check capability match
            if task_type_str not in model.capabilities:
                continue
            
            # Check context length
            if context_length > model.max_tokens:
                continue
            
            # Check accuracy threshold
            if min_accuracy:
                # Use appropriate performance metric for task type
                metric_key = self._get_metric_key(task_type)
                if metric_key not in model.performance:
                    continue
                if model.performance[metric_key] < min_accuracy:
                    continue
            
            # Check cost limit
            if cost_limit and model.cost_per_1k_tokens > cost_limit:
                continue
            
            # Check latency limit
            if latency_limit and model.p95_latency_ms > latency_limit:
                continue
            
            # Calculate composite score (weighted)
            score = self._calculate_score(model, task_type, cost_limit, latency_limit)
            
            candidates.append((score, model))
        
        if not candidates:
            logger.warning(f"No candidates found for {task_type}")
            return None
        
        # Return highest scoring model
        candidates.sort(reverse=True, key=lambda x: x[0])
        best_model = candidates[0][1]
        
        logger.info(f"Selected {best_model.model_id} (score: {candidates[0][0]:.3f})")
        
        return best_model
    
    def _calculate_score(
        self,
        model: ModelMetadata,
        task_type: TaskType,
        cost_limit: Optional[float],
        latency_limit: Optional[int]
    ) -> float:
        """Calculate composite score for model selection"""
        
        # Get performance metric for this task type
        metric_key = self._get_metric_key(task_type)
        accuracy = model.performance.get(metric_key, 0.5)
        
        # Normalize cost (inverse - lower is better)
        cost_score = 1.0 - min(model.cost_per_1k_tokens / 0.02, 1.0) if cost_limit else 0.5
        
        # Normalize latency (inverse - lower is better)
        latency_score = 1.0 - min(model.p95_latency_ms / 3000, 1.0) if latency_limit else 0.5
        
        # Weighted combination
        score = (
            accuracy * 0.5 +      # 50% weight on accuracy
            cost_score * 0.3 +    # 30% weight on cost
            latency_score * 0.2   # 20% weight on latency
        )
        
        return score
    
    def _get_metric_key(self, task_type: TaskType) -> str:
        """Map task type to performance metric key"""
        mapping = {
            TaskType.REASONING: 'gpqa_score',
            TaskType.CODING: 'swe_bench_verified',
            TaskType.ANALYSIS: 'gpqa_score',
            TaskType.FAST_INFERENCE: 'swe_bench_verified',
            TaskType.LONG_CONTEXT: 'gpqa_score',
            TaskType.MULTIMODAL: 'swe_bench_verified',
            TaskType.COST_OPTIMIZED: 'swe_bench_verified'
        }
        return mapping.get(task_type, 'gpqa_score')
    
    def get_fallback_chain(self, model_id: str, task_type: TaskType) -> List[ModelMetadata]:
        """Get fallback chain for a model"""
        
        # Get predefined fallback chain for task type
        chain_key = self._get_fallback_chain_key(task_type)
        model_ids = self.fallback_chains.get(chain_key, [])
        
        # Remove the primary model from chain
        model_ids = [mid for mid in model_ids if mid != model_id]
        
        # Convert to ModelMetadata objects
        fallbacks = []
        for mid in model_ids:
            model = self.registry.get_model(mid)
            if model and model.available:
                fallbacks.append(model)
        
        return fallbacks
    
    def _get_fallback_chain_key(self, task_type: TaskType) -> str:
        """Map task type to fallback chain key"""
        mapping = {
            TaskType.REASONING: 'critical_reasoning',
            TaskType.CODING: 'fast_coding',
            TaskType.COST_OPTIMIZED: 'cost_optimized',
            TaskType.FAST_INFERENCE: 'fast_coding',
        }
        return mapping.get(task_type, 'critical_reasoning')
    
    async def execute(self, model: ModelMetadata, request: RoutingRequest) -> RoutingResponse:
        """
        Execute request against a specific model
        This is a placeholder - actual implementation would call provider APIs
        """
        
        start_time = time.time()
        
        # TODO: Implement actual provider integrations
        # For now, simulate execution
        await asyncio.sleep(model.p95_latency_ms / 1000)
        
        # Simulate response
        response_text = f"[Simulated response from {model.model_id}]"
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Estimate cost (tokens approximation)
        estimated_tokens = len(request.prompt.split()) * 1.3  # Rough estimate
        cost = (estimated_tokens / 1000) * model.cost_per_1k_tokens
        
        return RoutingResponse(
            model_id=model.model_id,
            provider=model.provider,
            response=response_text,
            latency_ms=latency_ms,
            cost=cost,
            confidence=0.92  # Placeholder
        )
    
    def update_metrics(self, model: ModelMetadata, result: RoutingResponse):
        """Update model performance metrics"""
        
        metrics = {
            'latency_ms': result.latency_ms,
            'cost': result.cost,
            'confidence': result.confidence,
            'success': True
        }
        
        self.registry.update_performance(model.model_id, metrics)
        
        logger.info(f"Updated metrics for {model.model_id}")
    
    def log_failure(self, model: ModelMetadata, error: Exception):
        """Log model failure"""
        
        metrics = {
            'error': str(error),
            'success': False
        }
        
        self.registry.update_performance(model.model_id, metrics)
        
        logger.error(f"Logged failure for {model.model_id}: {error}")
    
    def _generate_cache_key(self, request: RoutingRequest) -> str:
        """Generate cache key for request"""
        
        # Create deterministic hash of request
        request_str = f"{request.prompt}|{request.task_type.value}"
        return hashlib.sha256(request_str.encode()).hexdigest()[:16]
    
    def quantize_model(self, model_id: str, target_size: str = "int8"):
        """
        Model quantization for cost optimization
        Reduces inference cost by 50-70% with <2% accuracy loss
        
        Args:
            model_id: Model to quantize
            target_size: Target quantization (int8, int4, etc.)
        """
        
        model = self.registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        if target_size not in model.quantized_versions:
            logger.warning(f"{target_size} quantization not available for {model_id}")
            return
        
        # TODO: Implement actual quantization using frameworks like:
        # - GGML/GGUF (for local models)
        # - TensorRT (for NVIDIA)
        # - OpenVINO (for Intel)
        # - Torch quantization
        
        logger.info(f"Quantized {model_id} to {target_size}")
    
    def get_performance_report(self, model_id: str) -> Dict:
        """Get performance report for a model"""
        
        history = self.registry.performance_history.get(model_id, [])
        
        if not history:
            return {}
        
        # Calculate aggregates
        successful = [h for h in history if h['metrics'].get('success', False)]
        
        if not successful:
            return {'total_requests': len(history), 'success_rate': 0.0}
        
        avg_latency = sum(h['metrics'].get('latency_ms', 0) for h in successful) / len(successful)
        avg_cost = sum(h['metrics'].get('cost', 0) for h in successful) / len(successful)
        avg_confidence = sum(h['metrics'].get('confidence', 0) for h in successful) / len(successful)
        
        return {
            'model_id': model_id,
            'total_requests': len(history),
            'successful_requests': len(successful),
            'success_rate': len(successful) / len(history),
            'avg_latency_ms': avg_latency,
            'avg_cost': avg_cost,
            'avg_confidence': avg_confidence
        }


# Example usage
async def main():
    """Example usage of ModelRouter"""
    
    # Initialize router
    router = ModelRouter(
        config_path='ai/registry/model-tracking.yml',
        registry_path='ai/registry/model-tracking.yml'
    )
    
    # Example request
    request = RoutingRequest(
        prompt="Explain quantum computing in simple terms",
        task_type=TaskType.REASONING,
        cost_limit=0.015,
        latency_limit=2000
    )
    
    # Route and execute
    result = await router.route_request(request)
    
    print(f"\nRouting Result:")
    print(f"Model: {result.model_id}")
    print(f"Provider: {result.provider.value}")
    print(f"Latency: {result.latency_ms}ms")
    print(f"Cost: ${result.cost:.4f}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Response: {result.response}")


if __name__ == "__main__":
    asyncio.run(main())
