import os
import sys
import json
import time
import argparse
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Local imports
from src.safety import check_prompt_safety, check_response_safety
from src.metrics_logger import log_execution_metrics

# Load environment variables
load_dotenv()

# Pydantic schema for output contract validation
class SupportResponseSchema(BaseModel):
    category: str = Field(description="Category of the ticket: Facturación, Técnico, Cuenta, Envíos, General")
    answer: str = Field(description="Direct, helpful answer to the customer inquiry in Spanish")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    rationale: str = Field(description="Brief explanation of decision reasoning")
    actions: list[str] = Field(description="Recommended downstream actions")

def load_prompt_template(filepath: str = "prompts/main_prompt.txt") -> str:
    """Reads system prompt template from file."""
    if not os.path.exists(filepath):
        # Fallback default system prompt if file missing
        return "You are a customer support assistant. Respond ONLY in valid JSON with keys: category, answer, confidence, rationale, actions."
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def process_customer_query(query: str, model: str = "gpt-4o-mini", temperature: float = 0.2) -> Dict[str, Any]:
    """
    Main pipeline: Safety Check -> Prompting -> API Call -> JSON Validation -> Metrics Logging
    """
    start_time = time.time()
    
    # 1. Safety & Security Check (Bonus Guardrail)
    is_safe, fallback_response = check_prompt_safety(query)
    if not is_safe:
        latency_ms = (time.time() - start_time) * 1000
        metrics = log_execution_metrics(
            query=query,
            model=model,
            prompt_tokens=0,
            completion_tokens=0,
            latency_ms=latency_ms
        )
        return {
            "status": "security_blocked",
            "data": fallback_response,
            "metrics": metrics
        }
        
    # 2. Verify API Key & Initialize Client with Timeout and Retries Backoff
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
        
    # Configure production resilience: explicit 15s timeout and 3 retries backoff
    client = OpenAI(
        api_key=api_key,
        timeout=15.0,
        max_retries=3
    )
    system_prompt = load_prompt_template()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Customer Inquiry: {query}"}
    ]
    
    # 3. Call OpenAI API with Structured JSON enforcement
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
        max_tokens=300
    )
    
    latency_ms = (time.time() - start_time) * 1000
    raw_content = response.choices[0].message.content
    usage = response.usage
    
    # 4. Reactive Output Guardrail Check (Safety & Privacy Leak Filter)
    is_response_safe, sanitized_content = check_response_safety(raw_content)
    if not is_response_safe:
        raw_content = json.dumps({
            "category": "General",
            "answer": sanitized_content,
            "confidence": 0.0,
            "rationale": "Alerta de Seguridad: La salida del modelo contenía credenciales o datos no permitidos.",
            "actions": ["Sanitizar salida", "Loguear incidente de seguridad de salida"]
        })
    
    # 5. Parse & Validate JSON output
    try:
        data_dict = json.loads(raw_content)
        validated = SupportResponseSchema(**data_dict)
        final_data = validated.model_dump()
    except Exception as e:
        print(f"⚠️ Validation Warning: Output schema parsing error ({e}). Returning raw parsed dict.")
        final_data = json.loads(raw_content) if raw_content.startswith("{") else {"raw_response": raw_content}
        
    # 5. Log metrics
    metrics = log_execution_metrics(
        query=query,
        model=model,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        latency_ms=latency_ms
    )
    
    return {
        "status": "success",
        "data": final_data,
        "metrics": metrics
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multitasking Customer Support Text Utility")
    parser.add_argument("--query", type=str, default="How do I change my billing address for upcoming invoices?", help="Customer inquiry text")
    args = parser.parse_args()
    
    result = process_customer_query(args.query)
    print(json.dumps(result, indent=2, ensure_ascii=False))
