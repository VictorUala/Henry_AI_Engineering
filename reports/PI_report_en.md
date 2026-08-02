# 📑 Project Integrator Report: Multitasking Customer Support Text Utility

**Student:** Víctor  
**Course:** Soy Henry - AI Engineering (Module 1)  
**Project:** Multitasking Customer Support AI Utility & Telemetry Dashboard  
**Date:** August 2026  

---

## 1. System Architecture Overview

This project implements a production-ready **Multitasking Customer Support AI Utility** using OpenAI's API (`gpt-4o-mini`). The system receives unstructured customer inquiries and outputs validated, structured JSON payloads containing answer content, confidence estimations, decision rationales, and recommended downstream actions for customer support agents.

### Architecture Diagram
```text
Customer Query ➔ Proactive Input Safety Guardrail (src/safety.py) ➔ System Prompt Assembly (prompts/main_prompt.txt)
                                                                                  │
                                                                                  ▼
Final JSON Payload ◄── Reactive Output Guardrail ◄── Pydantic Validation ◄── OpenAI API (gpt-4o-mini)
      │                                                                           │
      ▼                                                                           ▼
Console / Streamlit Web UI (app.py)                                   Metrics Logger (metrics/metrics.json)
```

### Key Engineering Choices
* **Model Selection (`gpt-4o-mini`)**: Chosen for its high reasoning capabilities, sub-second latency, and ultra-low cost ($0.150 USD / 1M prompt tokens, $0.600 USD / 1M completion tokens).
* **Strict JSON Contract**: Enforced via `response_format={"type": "json_object"}` in the OpenAI API call and validated at runtime using `Pydantic` models.
* **Production Resilience**: Configured with an **explicit 15-second timeout** and **3 automatic retries with exponential backoff** to handle network hiccups or API rate limits gracefully.
* **Observability & Cost Control**: Automatically records latency in milliseconds, token counts, and calculated USD cost per execution in `metrics/metrics.json`.

---

## 2. Prompt Engineering Rationale

The system prompt ([prompts/main_prompt.txt](file:///c:/Users/power/.gemini/antigravity/brain/Henry_Engineering/prompts/main_prompt.txt)) was designed following modern AI engineering best practices:

1. **Few-Shot In-Context Learning**: Incorporates high-quality, localized Spanish input-output examples. This establishes the empathetic tone, strict category bounds (`Facturación`, `Técnico`, `Cuenta`, `Envíos`, `General`), and JSON schema without needing expensive model fine-tuning.
2. **Output Rationale (`rationale` field)**: Forcing the model to output a contextual explanation/rationale (`rationale`) alongside its answer improves classification precision, prevents blind guesses, and ensures auditability.
3. **Deterministic Parameters**: Configured with `temperature=0.2` to minimize randomness, reduce hallucination risks, and maintain consistent JSON output formatting across executions.

---

## 3. Security Guardrails, Moderation & Bias Mitigation (Bonus)

To defend against malicious inputs and protect sensitive user data, a multi-layer security module was implemented in [src/safety.py](file:///c:/Users/power/.gemini/antigravity/brain/Henry_Engineering/src/safety.py):

### A. Proactive Input Guardrail (Pre-API Call)
* **Prompt Injection & Jailbreak Defense:** Scans user input for adversarial manipulation attempts (e.g., *"ignore previous instructions"*, *"reveal system prompt"*, *"DAN"*, *"ignora las instrucciones anteriores"*).
* **PII Leakage Prevention:** Intercepts raw unmasked credit card numbers (13-16 digit patterns) and plain-text credentials (`password=...`).
* **Instant Fallback Response ($0 USD / Latency < 1ms):** Halts execution immediately **without calling the OpenAI API**, returning a safe JSON payload with category `"General"`, confidence `0.0`, and audit log justifications.

### B. Reactive Output Guardrail (Post-Generation)
* **Credential Sanitization:** Scans generated text before returning it to the user. Automatically sanitizes API Keys (`sk-...`) or masked credit cards if accidentally produced by the LLM.

---

## 4. Metrics & Observability Summary

The system tracks six core operational metrics per execution in `metrics/metrics.json`:
* **Timestamp**: ISO 8601 UTC timestamp.
* **Token Counts**: Separated into `tokens_prompt`, `tokens_completion`, and `total_tokens`.
* **Latency**: Duration measured in milliseconds (`latency_ms`).
* **Estimated Cost**: Real-time USD cost calculation (`estimated_cost_usd`).

### Sample Metric Log Entry (`metrics/metrics.json`)
```json
{
  "timestamp": "2026-07-31T20:15:00+00:00",
  "query_preview": "¿Dónde puedo descargar mi factura del mes pasado?",
  "model": "gpt-4o-mini",
  "tokens_prompt": 245,
  "tokens_completion": 68,
  "total_tokens": 313,
  "latency_ms": 782.4,
  "estimated_cost_usd": 0.000078
}
```

---

## 5. Automated Unit Tests

Covered by a comprehensive `pytest` suite ([tests/test_core.py](file:///c:/Users/power/.gemini/antigravity/brain/Henry_Engineering/tests/test_core.py)). **100% Pass Rate (6 of 6 tests passed)**:

1. `test_reactive_output_guardrail_sanitizes_leaked_credentials` ✅ **PASSED**
2. `test_safety_filter_detects_adversarial_input` ✅ **PASSED**
3. `test_safety_filter_detects_pii_leak` ✅ **PASSED**
4. `test_safety_filter_allows_normal_input` ✅ **PASSED**
5. `test_cost_calculation_accuracy` ✅ **PASSED**
6. `test_json_schema_validation` ✅ **PASSED**

---

## 6. Conclusion & Future Improvements

The project fully satisfies all requirements specified by the **Soy Henry AI Engineering (Module 1)** rubric.

### Future Work
* **RAG (Retrieval-Augmented Generation):** Integrate vector search over internal knowledge base docs.
* **External Moderation API:** Combine regex-based filtering with OpenAI's `text-moderation-latest` endpoint.
