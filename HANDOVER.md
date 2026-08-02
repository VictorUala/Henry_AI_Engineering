# 📑 HANDOVER DE PROYECTO - Henry AI Engineering Módulo 1

**Estudiante:** Víctor  
**Proyecto:** Multitasking Customer Support AI Utility & Telemetry Dashboard  
**Repositorio GitHub:** [https://github.com/VictorUala/Henry_AI_Engineering](https://github.com/VictorUala/Henry_AI_Engineering) (Público, verificado y sincronizado vía SSH)  
**Última actualización:** 31 de Julio, 2026  

---

## 📌 Estado Actual del Proyecto (¡PROYECTO COMPLETO Y VERIFICADO EN VIVO!)

### 1. Repositorio & Git
- [x] Repositorio Git local inicializado en rama `main`.
- [x] Conectado exitosamente con GitHub via SSH (`git@github.com:VictorUala/Henry_AI_Engineering.git`).
- [x] `.gitignore` configurado estrictamente (excluye `.env`, `jupiters/`, `moderation_service/` y `venv/`).
- [x] `.env` verificado con `OPENAI_API_KEY` activa y funcional.
- [x] Todos los cambios commiteados y pusheados a GitHub (`main`).

### 2. Estructura de Código & Funcionalidades
- [x] `app.py`: Interfaz Gráfica Web Interactiva con Streamlit (`streamlit run app.py`). Incluye métricas KPI en tiempo real (latencia, tokens, costo, request_id), visualización para el agente de soporte en español, inspector JSON y tabla histórica de telemetría.
- [x] `prompts/main_prompt.txt`: Plantilla Few-Shot + CoT estandarizada y localizada en español con categorías oficiales.
- [x] `src/run_query.py`: Aplicación principal ejecutable (llamada a API `gpt-4o-mini`, timeouts de 15s, 3 reintentos con backoff exponencial, doble guardia de seguridad de entrada/salida y validación con Pydantic).
- [x] `src/metrics_logger.py`: Módulo de telemetría que registra `request_id` único por llamada, `tokens_prompt`, `tokens_completion`, `total_tokens`, `latency_ms` y `estimated_cost_usd` en `metrics/metrics.json`.
- [x] `src/safety.py`: **Módulo Avanzado de Guardia de Seguridad Doble (Entrada Proactiva + Salida Reactiva)**:
  - **Entrada (Proactivo)**: Intercepta inyecciones de prompt (jailbreaks) y tarjetas de crédito o contraseñas en crudo antes de llamar al LLM (0.34ms, $0 USD).
  - **Salida (Reactivo - `check_response_safety`)**: Sanitiza automáticamente si la IA llegase a filtrar accidentalmente API Keys o tarjetas en su respuesta.
- [x] `tests/test_core.py`: Suite de 6 pruebas unitarias automatizadas con `pytest` (**6/6 pasadas exitosamente**).
- [x] `reports/PI_report_es.md`: Informe oficial del proyecto en español (completo y detallado).
- [x] `README.md`: Documentación completa del proyecto.

---

## 📊 Resultados de Pruebas Automatizadas

- **Suite de Pruebas Unitarias (`pytest tests/test_core.py`)**: **6/6 tests pasados exitosamente (100%)**.
  - `test_reactive_output_guardrail_sanitizes_leaked_credentials` ✅ PASADO
  - `test_safety_filter_detects_adversarial_input` ✅ PASADO
  - `test_safety_filter_detects_pii_leak` ✅ PASADO
  - `test_safety_filter_allows_normal_input` ✅ PASADO
  - `test_cost_calculation_accuracy` ✅ PASADO
  - `test_json_schema_validation` ✅ PASADO
