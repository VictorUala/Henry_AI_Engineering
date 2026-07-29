# Project Integrator Report: Multitasking Customer Support Text Utility

**Author:** Víctor  
**Course:** Soy Henry - AI Engineering (Module 1)  
**Date:** July 2026  

---

## 1. System Architecture Overview

This project implements a production-grade **Multitasking Customer Support AI Utility** using OpenAI's API (`gpt-4o-mini`). The system receives unstructured customer inquiries and outputs validated, structured JSON payloads containing answer content, confidence estimations, decision rationales, and recommended downstream actions.

### Architecture Diagram
```
Customer Query ➔ Security Guardrail (src/safety.py) ➔ System Prompt Assembly (prompts/main_prompt.txt)
                                                                 │
                                                                 ▼
JSON Output ◄── Schema Validation ◄── OpenAI Chat Completions API (gpt-4o-mini)
    │                                                            │
    ▼                                                            ▼
Console/Downstream                                   Metrics Logger (metrics/metrics.json)
```

### Key Engineering Choices
* **Model Selection (`gpt-4o-mini`)**: Selected for high reasoning capabilities, sub-second latency, and ultra-low cost ($0.150 / 1M prompt tokens, $0.600 / 1M completion tokens).
* **Strict JSON Contract**: Enforced via `response_format={"type": "json_object"}` and validated at runtime using `Pydantic` schemas.
* **Observability & Cost Control**: Every execution automatically logs latency, token consumption, and calculated USD cost to `metrics/metrics.json`.

---

## 2. Prompt Engineering Rationale

The system prompt ([prompts/main_prompt.txt](file:///C:/Users/power/.gemini/antigravity/brain/Henry_Engineering/prompts/main_prompt.txt)) combines **Few-Shot Learning** and **Chain-of-Thought (CoT) Reasoning**:

1. **Few-Shot Examples**: Providing high-quality input-output pairs anchors the model's behavior, establishing exact tone, JSON formatting, and action categorization without requiring model fine-tuning.
2. **Chain-of-Thought (`rationale` field)**: Forcing the model to output a step-by-step rationale before or alongside its answer improves classification precision and auditability.
3. **Deterministic Parameters**: Configured with `temperature=0.2` to minimize randomness, reduce hallucinations, and ensure consistent JSON structure across execution runs.

---

## 3. Metrics & Observability Summary

The system tracks three core operational metrics per execution:
* **Token Consumption**: Separated into `tokens_prompt`, `tokens_completion`, and `total_tokens`.
* **Latency**: Execution duration measured in milliseconds (`latency_ms`).
* **Estimated Cost**: Real-time per-query cost calculation in USD (`estimated_cost_usd`).

### Sample Metric Log Entry (`metrics/metrics.json`)
```json
{
  "timestamp": "2026-07-29T19:40:00+00:00",
  "query_preview": "How do I change my billing address for upcoming invoices?",
  "model": "gpt-4o-mini",
  "tokens_prompt": 245,
  "tokens_completion": 68,
  "total_tokens": 313,
  "latency_ms": 782.4,
  "estimated_cost_usd": 0.000078
}
```

---

## 4. Security Guardrails & Adversarial Fallback (Bonus)

To defend against malicious inputs, the application includes an adversarial input filter ([src/safety.py](file:///C:/Users/power/.gemini/antigravity/brain/Henry_Engineering/src/safety.py)). It intercepts common prompt injection triggers (e.g., *"ignore previous instructions"*, *"reveal system prompt"*, jailbreak patterns) prior to invoking the LLM API. 

When an attack is detected, the system safely halts execution, logs a security alert, and returns a controlled fallback JSON response without incurring API token charges.

---

## 5. Architectural Trade-offs & Future Work

* **Trade-off (Lightweight Regex Guardrail vs. Guardrails LLM)**: Using pattern-based detection in `src/safety.py` provides instantaneous (<1ms) filtering zero API cost, though complex obfuscated prompt injections could require an external moderation model (e.g., `text-moderation-latest`).
* **Future Work**:
  * Implement RAG (Retrieval-Augmented Generation) using vector search over company knowledge base articles.
  * Add automatic retry logic with exponential backoff for handling HTTP 429 rate limit spikes.
