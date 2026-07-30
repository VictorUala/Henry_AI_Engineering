# 📑 HANDOVER DE PROYECTO - Henry AI Engineering Módulo 1

**Estudiante:** Víctor  
**Proyecto:** Multitasking Customer Support AI Utility  
**Repositorio GitHub:** [https://github.com/VictorUala/Henry_AI_Engineering](https://github.com/VictorUala/Henry_AI_Engineering) (Público, conectado por SSH)  
**Última actualización:** 29 de Julio, 2026  

---

## 💻 Entorno de Trabajo Virtual (`virtual.bat`)

### ¿Qué hace `virtual.bat`?
- Activa el entorno virtual de Python de este proyecto (`call ".\venv\Scripts\activate.bat"`).
- Garantiza que los comandos `python`, `pip` y las librerías (`openai`, `pydantic`, `pytest`) utilicen el aislamiento adecuado.

### ¿Cuándo debes ejecutarlo?
- **Cada vez que abras una nueva terminal de comandos en Windows (CMD)** para empezar a trabajar en este proyecto.
- **NO** es necesario ejecutarlo cada vez que creas o modificas un archivo `.py`. Se ejecuta **una sola vez por sesión de terminal**.
- *Nota en VS Code/Antigravity*: Si seleccionas el intérprete de Python del `venv` (`.\venv\Scripts\python.exe`), el IDE lo activa automáticamente al ejecutar scripts o al abrir una terminal integrada.

---

## 📌 Estado Actual del Proyecto

### 1. Repositorio & Git
- [x] Repositorio Git local inicializado en rama `main`.
- [x] Conectado exitosamente con GitHub via SSH (`git@github.com:VictorUala/Henry_AI_Engineering.git`).
- [x] `.gitignore` configurado (excluye estrictamente `jupiters/`, `.env`, `venv/` y archivos temporales).
- [x] `.env` creado y verificado con la clave `OPENAI_API_KEY`.
- [x] Commit inicial y push a GitHub (`main`) completado.

### 2. Estructura de Código & Funcionalidades
- [x] `prompts/main_prompt.txt`: Plantilla de prompt combinando **Few-Shot** + **Chain-of-Thought (CoT)**.
- [x] `src/run_query.py`: Aplicación principal ejecutable que llama a `gpt-4o-mini`, fuerza JSON estructurado y valida con Pydantic.
- [x] `src/metrics_logger.py`: Módulo de telemetría que registra `tokens_prompt`, `tokens_completion`, `total_tokens`, `latency_ms` y `estimated_cost_usd` en `metrics/metrics.json`.
- [x] `src/safety.py`: Filtro bonus de moderación para interceptar inyecciones de prompt / ataques adversariales.
- [x] `tests/test_core.py`: Suite de 4 pruebas unitarias automatizadas con `pytest` (**4/4 pasadas exitosamente**).
- [x] `reports/PI_report_en.md`: Informe oficial de 1 a 2 páginas en Markdown.
- [x] `README.md`: Documentación completa de instalación, arquitectura y reproducción.
- [x] `virtual.bat`: Script de activación rápida de entorno virtual.

---

## 🎯 Plan de Estudio Actual (Sesión de Estudio Módulo 1 - Lección 2)

1. **Conceptos de Comunicación entre Sistemas**:
   - Explicación de REST APIs y protocolo HTTP.
   - Cómo interactúa tu código Python con los servidores de OpenAI/Anthropic/Gemini.
2. **Experimentación en Sandbox**:
   - Crear `sandbox.py` para probar llamadas REST/SDK y observar respuestas crudas.
3. **Prueba de Aplicación Final en Vivo**:
   - Ejecutar `python -m src.run_query` contra la API de OpenAI y verificar el registro de métricas reales.
