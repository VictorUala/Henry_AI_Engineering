# 📑 Informe Integrador: Asistente Multitarea de Soporte al Cliente con IA

**Estudiante:** Víctor  
**Curso:** Soy Henry - AI Engineering (Módulo 1)  
**Proyecto:** Multitasking Customer Support AI Utility & Telemetry Dashboard  
**Fecha:** Agosto 2026  

---

## 1. Visión General y Arquitectura del Sistema

Este proyecto implementa una herramienta de **Soporte al Cliente Multitarea basada en Inteligencia Artificial** lista para producción, utilizando la API de OpenAI (`gpt-4o-mini`). El sistema procesa consultas no estructuradas de clientes y genera respuestas estructuradas en formato JSON estricto, incluyendo contenido de respuesta, nivel de confianza, razonamiento/justificación y acciones recomendadas para el equipo de atención al cliente.

### Diagrama de Arquitectura
```text
Consulta del Cliente ➔ Guardia Proactiva de Entrada (src/safety.py) ➔ Ensamble de Prompt System (prompts/main_prompt.txt)
                                                                                  │
                                                                                  ▼
Payload JSON Final ◄── Guardia Reactiva de Salida ◄── Validación Pydantic ◄── API OpenAI (gpt-4o-mini)
      │                                                                           │
      ▼                                                                           ▼
Consola / Interfaz Web (app.py)                                       Registro de Telemetría (metrics/metrics.json)
```

### Decisiones Principales de Ingeniería
* **Selección del Modelo (`gpt-4o-mini`)**: Elegido por su equilibrio óptimo entre razonamiento, latencia sub-segundo y costo extremadamente bajo ($0.150 USD por millón de tokens de prompt / $0.600 USD por millón de tokens de completitud).
* **Contrato JSON Estricto**: Garantizado mediante la propiedad `response_format={"type": "json_object"}` en la llamada a la API y validado en tiempo de ejecución con modelos de `Pydantic`.
* **Resiliencia de Producción**: Configuración de **timeout explícito de 15 segundos** y un mecanismo de **3 reintentos con backoff exponencial** para mitigar picos de latencia o caídas temporales de red.
* **Observabilidad y Control de Costos**: Cada ejecución registra en tiempo real la latencia en milisegundos, el consumo de tokens y el costo calculado en USD en `metrics/metrics.json`.

---

## 2. Ingeniería de Prompts & Estrategia de Diseño

El prompt del sistema ([prompts/main_prompt.txt](file:///c:/Users/power/.gemini/antigravity/brain/Henry_Engineering/prompts/main_prompt.txt)) fue diseñado aplicando buenas prácticas de desarrollo en IA:

1. **Aprendizaje en Contexto con Ejemplos (*Few-Shot In-Context Learning*)**: Se incorporan ejemplos reales representativos de entrada y respuesta esperada en español. Esto delimita el tono empático, la categorización cerrada (`Facturación`, `Técnico`, `Cuenta`, `Envíos`, `General`) y el esquema JSON sin necesidad de realizar un ajuste fino (*fine-tuning*) del modelo.
2. **Justificación del Análisis (`rationale`)**: Exigir al modelo un campo obligatorio de explicación previa/simultánea (`rationale`) incrementa la precisión en la clasificación y asegura la auditoría de las decisiones tomadas por la IA.
3. **Parámetros Deterministas**: Configuración de `temperature=0.2` para minimizar la aleatoriedad, reducir drásticamente el riesgo de alucinaciones y garantizar respuestas consistentes entre ejecuciones.

---

## 3. Medidas de Seguridad, Moderación y Mitigación de Sesgos

Para garantizar la protección en un entorno de atención al cliente real, se desarrolló un módulo de seguridad multicapa ([src/safety.py](file:///c:/Users/power/.gemini/antigravity/brain/Henry_Engineering/src/safety.py)):

### A. Guardia Proactiva de Entrada (Antes de llamar a la API)
* **Detección de Inyecciones de Prompt (*Jailbreaks* & Ataques Adversariales):** Intercepta intentos de manipulación del prompt (ej. *"ignore previous instructions"*, *"reveal system prompt"*, *"DAN"*, *"ignora las instrucciones anteriores"*).
* **Filtro de Privacidad de Datos Sensibles (PII):** Bloquea consultas que contengan números de tarjeta de crédito en crudo (patrones de 13 a 16 dígitos) o contraseñas expuestas (`password=...` / `contraseña=...`).
* **Respuesta Fallback Segura ($0 USD / Latencia < 1ms):** Ante una amenaza, la ejecución se interrumpe inmediatamente **sin consumir tokens de la API de OpenAI**, devolviendo un JSON seguro con categoría `"General"`, score de confianza `0.0` y registrando el motivo en los logs de auditoría.

### B. Guardia Reactiva de Salida (Antes de responder al usuario)
* **Sanitización Automática:** Escanea la respuesta generada por el LLM antes de mostrarla. Si la IA llegara a filtrar accidentalmente una API Key (`sk-...`) o un número de tarjeta de crédito en su texto, el filtro sanitiza y enmascara automáticamente el contenido sensible.

### C. Mitigación de Sesgos y Neutralidad
* **Localización y Lenguaje Neutro:** Tono profesional, empático y libre de sesgos de género o culturales.
* **Categorización Estricta:** Limita las categorías de soporte a las opciones oficiales, evitando clasificaciones ambiguas o discriminatorias.

---

## 4. Telemetría y Observabilidad

El sistema registra tres métricas operativas clave por cada consulta en `metrics/metrics.json`:
* **Consumo de Tokens**: Desglosado en `tokens_prompt`, `tokens_completion` y `total_tokens`.
* **Latencia**: Tiempo total de ejecución medido en milisegundos (`latency_ms`).
* **Costo Estimado**: Cálculo automático del costo financiero en USD (`estimated_cost_usd`).

### Ejemplo de Registro de Telemetría (`metrics/metrics.json`)
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

## 5. Frontend Interactivo del Operador de Soporte (`app.py`)

Para ir más allá de un simple script de consola y ofrecer una experiencia de usuario completa y lista para producción, se desarrolló un **Dashboard Web Interactivo en Streamlit** ([app.py](file:///c:/Users/power/.gemini/antigravity/brain/Henry_Engineering/app.py)):

### Características del Frontend
* **Diseño Orientado al Agente Humano**: Interfaz limpia en español donde el operador de soporte introduce consultas de clientes o selecciona ejemplos preconfigurados.
* **Visualización de Respuesta & Acciones Recomendadas**: Muestra de forma clara la categoría asignada, la respuesta empática sugerida y la lista de acciones a seguir por el equipo.
* **Inspector de JSON & Métricas en Tiempo Real**: Panel lateral e inspector desplegable con los KPIs exactos de cada consulta (`request_id`, latencia en ms, consumo de tokens, costo en USD) y el payload JSON estructurado devuelto.
* **Histórico de Telemetría**: Tabla interactiva con el registro histórico de métricas guardadas en el sistema.

### Modos de Ejecución para Evaluación
El evaluador puede poner a prueba el proyecto mediante dos alternativas simples:
1. **Modo Web Interactivo (Recomendado):** `streamlit run app.py`
2. **Modo Consola (CLI):** `python -m src.run_query --query "Tu consulta aquí"`

---

## 6. Pruebas Automatizadas (Suite de Test Unitarios)

El proyecto cuenta con una suite completa de pruebas unitarias automatizadas ([tests/test_core.py](file:///c:/Users/power/.gemini/antigravity/brain/Henry_Engineering/tests/test_core.py)) ejecutadas con `pytest`. Cobertura del **100% (6 de 6 pruebas aprobadas)**:

1. `test_reactive_output_guardrail_sanitizes_leaked_credentials` ✅ **PASADO**
2. `test_safety_filter_detects_adversarial_input` ✅ **PASADO**
3. `test_safety_filter_detects_pii_leak` ✅ **PASADO**
4. `test_safety_filter_allows_normal_input` ✅ **PASADO**
5. `test_cost_calculation_accuracy` ✅ **PASADO**
6. `test_json_schema_validation` ✅ **PASADO**

---

## 7. Conclusión y Trabajo Futuro

El prototipo cumple holgadamente con todos los requerimientos técnicos y funcionales exigidos por el programa de **Henry AI Engineering (Módulo 1)**.

### Trabajo Futuro Recomendado
* **RAG (Generación Aumentada por Recuperación):** Integrar búsqueda vectorial sobre la base de conocimiento de la empresa para enriquecer las respuestas de soporte con información dinámica.
* **Modelo de Moderación Externo:** Evaluar el uso del endpoint `text-moderation-latest` como complemento del filtro por expresiones regulares actual.
