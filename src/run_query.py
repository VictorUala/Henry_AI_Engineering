import os
import sys
import json
import time
import argparse
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Importaciones locales de módulos del proyecto
from src.safety import check_prompt_safety, check_response_safety
from src.metrics_logger import log_execution_metrics

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Esquema Pydantic para la validación estricta del contrato de salida JSON
class SupportResponseSchema(BaseModel):
    category: str = Field(description="Categoría del ticket: Facturación, Técnico, Cuenta, Envíos, General")
    answer: str = Field(description="Respuesta directa, útil y empática en español")
    confidence: float = Field(ge=0.0, le=1.0, description="Puntaje de confianza flotante entre 0.0 y 1.0")
    rationale: str = Field(description="Breve explicación del razonamiento de la decisión")
    actions: list[str] = Field(description="Lista de acciones recomendadas a seguir")

def load_prompt_template(filepath: str = "prompts/main_prompt.txt") -> str:
    """Carga la plantilla del prompt del sistema desde el archivo indicado."""
    if not os.path.exists(filepath):
        # Prompt por defecto en caso de que no exista el archivo
        return "Sos un asistente de soporte al cliente. Respondé ÚNICAMENTE en JSON válido con las claves: category, answer, confidence, rationale, actions."
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def process_customer_query(query: str, model: str = "gpt-4o-mini", temperature: float = 0.2) -> Dict[str, Any]:
    """
    Pipeline principal: Filtro de Seguridad ➔ Inyección de Prompt ➔ Llamada a API OpenAI ➔ Validación JSON ➔ Registro de Métricas
    """
    start_time = time.time()
    
    # 1. Chequeo de Seguridad Proactivo (Guardia de Entrada contra Jailbreaks y PII)
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
        
    # 2. Verificación de API Key e Inicialización del Cliente OpenAI con Timeout y Reintentos
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada. Por favor verifica tu archivo .env.")
        
    # Configuración de resiliencia en producción: timeout explícito de 15s y 3 reintentos con backoff
    client = OpenAI(
        api_key=api_key,
        timeout=15.0,
        max_retries=3
    )
    system_prompt = load_prompt_template()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Consulta del Cliente: {query}"}
    ]
    
    # 3. Llamada a la API de OpenAI con formato JSON forzado
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
    
    # 4. Chequeo de Seguridad Reactivo (Filtro de Salida contra credenciales o PII)
    is_response_safe, sanitized_content = check_response_safety(raw_content)
    if not is_response_safe:
        raw_content = json.dumps({
            "category": "General",
            "answer": sanitized_content,
            "confidence": 0.0,
            "rationale": "Alerta de Seguridad: La salida del modelo contenía credenciales o datos no permitidos.",
            "actions": ["Sanitizar salida", "Loguear incidente de seguridad de salida"]
        })
    
    # 5. Parseo y Validación Estricta del Contrato JSON
    try:
        data_dict = json.loads(raw_content)
        validated = SupportResponseSchema(**data_dict)
        final_data = validated.model_dump()
    except Exception as e:
        print(f"⚠️ Advertencia de Validación: Error al parsear el esquema ({e}). Retornando diccionario crudo.")
        final_data = json.loads(raw_content) if raw_content.startswith("{") else {"raw_response": raw_content}
        
    # 6. Registrar Métricas y Telemetría en metrics.json
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
    parser = argparse.ArgumentParser(description="Utilidad CLI de Atención al Cliente con IA Multitarea")
    parser.add_argument("--query", type=str, default="¿Cómo puedo cambiar mi dirección de facturación para las próximas facturas?", help="Texto de la consulta del cliente")
    args = parser.parse_args()
    
    result = process_customer_query(args.query)
    print(json.dumps(result, indent=2, ensure_ascii=False))
