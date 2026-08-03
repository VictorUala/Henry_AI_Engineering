import os
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

# Precios oficiales de gpt-4o-mini por millón de tokens (USD)
COST_PER_1M_INPUT_TOKENS = 0.150
COST_PER_1M_OUTPUT_TOKENS = 0.600

def calculate_estimated_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Calcula el costo financiero estimado en USD para gpt-4o-mini."""
    input_cost = (prompt_tokens / 1_000_000) * COST_PER_1M_INPUT_TOKENS
    output_cost = (completion_tokens / 1_000_000) * COST_PER_1M_OUTPUT_TOKENS
    return round(input_cost + output_cost, 6)

def log_execution_metrics(
    query: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    metrics_file_path: str = "metrics/metrics.json"
) -> Dict[str, Any]:
    """
    Registra las métricas por ejecución (tokens, latencia, costo, request_id) en el archivo JSON.
    """
    total_tokens = prompt_tokens + completion_tokens
    estimated_cost_usd = calculate_estimated_cost(prompt_tokens, completion_tokens)
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    metric_entry = {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query_preview": query[:60] + "..." if len(query) > 60 else query,
        "model": model,
        "tokens_prompt": prompt_tokens,
        "tokens_completion": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(latency_ms, 2),
        "estimated_cost_usd": estimated_cost_usd
    }
    
    # Persistir registro en metrics/metrics.json
    try:
        if os.path.exists(metrics_file_path):
            with open(metrics_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        else:
            data = []
            
        data.append(metric_entry)
        
        os.makedirs(os.path.dirname(metrics_file_path), exist_ok=True)
        with open(metrics_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo guardar el registro de métricas: {e}")
        
    return metric_entry
