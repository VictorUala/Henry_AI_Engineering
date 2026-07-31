"""
🛡️ Módulo Avanzado de Seguridad, Moderación y Guardia de Privacidad (No PII)
Henry AI Engineering - Módulo 1
"""

import re
from typing import Tuple, Dict, Any, List

# 1. Patrones Adversariales (Inyecciones de Prompt & Jailbreaks)
ADVERSARIAL_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above)\s+(instructions|prompts)",
    r"disregard\s+(your\s+)?(system\s+)?prompt",
    r"reveal\s+(your\s+)?system\s+prompt",
    r"system\s*:\s*",
    r"you\s+are\s+now\s+a\s+DAN",
    r"jailbreak",
    r"ignora\s+(las\s+)?instrucciones\s+anteriores",
    r"muestra\s+(el\s+)?prompt\s+de\s+sistema",
]

# 2. Patrones de Filtración de Datos Sensibles (PII: Tarjetas de crédito, Contraseñas en crudo)
CREDIT_CARD_PATTERN = r'\b(?:\d[ -]*?){13,16}\b'
SENSITIVE_KEYWORD_PATTERN = r'\b(password|contraseña)\s*[:=]\s*\S+'
API_KEY_PATTERN = r'sk-[a-zA-Z0-9]{20,}'

def check_prompt_safety(query: str) -> Tuple[bool, Dict[str, Any]]:
    """
    CHEQUEO PROACTIVO (ENTRADA): Escanea la consulta del usuario buscando inyecciones de prompt o PII.
    
    Returns:
        (is_safe: bool, fallback_response: Dict[str, Any] o None)
    """
    normalized_query = query.lower().strip()
    reasons: List[Dict[str, str]] = []
    severity = "baja"
    
    # Check 1: Inyecciones de Prompt / Adversarial Attacks
    for pattern in ADVERSARIAL_PATTERNS:
        if re.search(pattern, normalized_query, re.IGNORECASE):
            reasons.append({
                "code": "prompt_injection",
                "description": f"Patrón de inyección de prompt detectado: '{pattern}'",
                "source": "guardia_seguridad"
            })
            severity = "alta"
            break
            
    # Check 2: Detectar números de tarjeta de crédito sin enmascarar o contraseñas expuestas
    if re.search(CREDIT_CARD_PATTERN, query) or re.search(SENSITIVE_KEYWORD_PATTERN, normalized_query):
        reasons.append({
            "code": "filtracion_de_privacidad",
            "description": "Se detectó información sensible sin enmascarar (PII: tarjeta o contraseña) en la consulta.",
            "source": "filtro_privacidad"
        })
        if severity != "alta":
            severity = "media"
            
    # Si se detectó alguna violación de seguridad o privacidad
    if reasons:
        primary_reason = reasons[0]
        code = primary_reason["code"]
        desc = primary_reason["description"]
        
        fallback_response = {
            "category": "General",
            "answer": "Alerta de Política de Seguridad: La consulta contiene instrucciones restringidas o datos sensibles no permitidos y no puede ser procesada.",
            "confidence": 0.0,
            "rationale": f"Bloqueo de seguridad [{code.upper()}] (Severidad: {severity}): {desc}",
            "actions": [
                "Registrar violación de política de seguridad",
                "Rechazar consulta adversarial o con PII sin llamar al LLM",
                "Flag en log de auditoría sin registrar PII en crudo"
            ]
        }
        return False, fallback_response
        
    return True, None


def check_response_safety(response_text: str) -> Tuple[bool, str]:
    """
    CHEQUEO REACTIVO (SALIDA): Escanea la respuesta generada por el LLM antes de enviársela al cliente.
    Verifica que la IA no haya filtrado accidentalmente API Keys o contraseñas en su texto.
    
    Returns:
        (is_safe: bool, sanitized_response_text: str)
    """
    # 1. Verificar si la respuesta contiene accidentalmente una API Key de OpenAI
    if re.search(API_KEY_PATTERN, response_text):
        sanitized_text = "Alerta de Privacidad: La respuesta generada contenía credenciales del sistema y ha sido sanitizada por seguridad."
        return False, sanitized_text

    # 2. Verificar si la respuesta filtró números de tarjeta sin enmascarar
    if re.search(CREDIT_CARD_PATTERN, response_text):
        sanitized_text = re.sub(CREDIT_CARD_PATTERN, "****-****-****-****", response_text)
        return False, sanitized_text

    return True, response_text
