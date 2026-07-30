"""
🛡️ Middleware de Moderación REST con FastAPI y Umbrales Configurables
Henry AI Engineering - Ejercicio de Clase
"""

import os
import sys
import json
import time
import uuid
import re
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 1. Cargar Configuración de Umbrales desde JSON
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "thresholds": {
            "default": { "permitir": 0.2, "marcar": 0.5, "bloquear": 0.8 }
        },
        "policy_version": "2026-07-30",
        "thresholds_version": "v1.0"
    }

config_data = load_config()

# 2. Esquemas de Pydantic para el Contrato API
class ModerationRequest(BaseModel):
    user_id: str = Field(description="ID único del usuario")
    input_text: str = Field(description="Texto ingresado por el usuario")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto adicional")

class ReasonItem(BaseModel):
    code: str
    description: str
    source: str = "modelo"

class ModerationResponse(BaseModel):
    action: str = Field(description="permitir | marcar | bloquear")
    reasons: List[ReasonItem] = Field(default_factory=list)
    severity: str = Field(description="baja | media | alta")
    request_id: str
    model_response_id: Optional[str] = None

# 3. Adaptador Mock de Clasificación de Moderación (Determinista)
def mock_moderation_classifier(text: str) -> Dict[str, float]:
    """
    Simula las puntuaciones del modelo [0.0, 1.0] por categoría.
    """
    scores = {
        "filtracion_de_privacidad": 0.05,
        "acoso": 0.05,
        "discurso_de_odio": 0.05,
        "contenido_sexual": 0.05
    }
    
    lower_text = text.lower()
    
    # Patrones de filtración de privacidad (email, contraseñas, DNI, etc.)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if re.search(email_pattern, text) or "contraseña" in lower_text or "password" in lower_text or "1234" in lower_text:
        scores["filtracion_de_privacidad"] = 0.90
        
    # Patrones de acoso / toxicidad
    if "idiot" in lower_text or "tonto" in lower_text or "acoso" in lower_text or "hate" in lower_text:
        scores["acoso"] = 0.65
        
    # Patrones de contenido sexual
    if "sexo" in lower_text or "porno" in lower_text or "sexual" in lower_text:
        scores["contenido_sexual"] = 0.85
        
    return scores

# 4. Motor de Evaluación de Umbrales
def evaluate_moderation(input_text: str, user_id: str) -> ModerationResponse:
    start_time = time.time()
    req_id = f"mod_{uuid.uuid4().hex[:8]}"
    
    # Obtener scores del mock
    scores = mock_moderation_classifier(input_text)
    thresholds = config_data.get("thresholds", {})
    default_thresh = thresholds.get("default", { "permitir": 0.2, "marcar": 0.5, "bloquear": 0.8 })
    
    category_actions = []
    reasons = []
    
    for category, score in scores.items():
        thresh = thresholds.get(category, default_thresh)
        allow_t = thresh.get("permitir", 0.2)
        block_t = thresh.get("bloquear", 0.8)
        
        if score >= block_t:
            category_actions.append("bloquear")
            reasons.append(ReasonItem(
                code=category,
                description=f"Puntaje alto de {score:.2f} superó el umbral de bloqueo ({block_t})",
                source="modelo"
            ))
        elif score >= allow_t:
            category_actions.append("marcar")
            reasons.append(ReasonItem(
                code=category,
                description=f"Puntaje de {score:.2f} cayó en la banda de marcado para revisión humana",
                source="modelo"
            ))
        else:
            category_actions.append("permitir")
            
    # Resolver la Acción Global (La más severa domina: bloquear > marcar > permitir)
    if "bloquear" in category_actions:
        final_action = "bloquear"
        severity = "alta"
    elif "marcar" in category_actions:
        final_action = "marcar"
        severity = "media"
    else:
        final_action = "permitir"
        severity = "baja"
        
    # Si todo se permite pero queremos dar feedback limpio
    if not reasons:
        reasons.append(ReasonItem(
            code="contenido_seguro",
            description="El contenido no infringió ninguna política de moderación",
            source="regla"
        ))
        
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    # Telemetría segura (Sin PII: Hash SHA-256)
    user_id_h = hashlib.sha256(user_id.encode('utf-8')).hexdigest()[:12]
    input_hash = hashlib.sha256(input_text.encode('utf-8')).hexdigest()[:12]
    
    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "request_id": req_id,
        "user_id_h": user_id_h,
        "model": "acme-moderator-mock-v1",
        "policy_version": config_data.get("policy_version"),
        "thresholds_version": config_data.get("thresholds_version"),
        "action": final_action,
        "severity": severity,
        "reasons": [r.model_dump() for r in reasons],
        "scores": scores,
        "input_hash": input_hash,
        "latency_ms": latency_ms
    }
    
    # Escribir log estructurado seguro
    try:
        log_file = os.path.join(os.path.dirname(__file__), "logs.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️ Error registrando log: {e}")
        
    return ModerationResponse(
        action=final_action,
        reasons=reasons,
        severity=severity,
        request_id=req_id,
        model_response_id=f"mod_resp_{uuid.uuid4().hex[:6]}"
    )

# 5. Inicializar la Aplicación FastAPI
app = FastAPI(
    title="Moderation Middleware Service",
    description="Middleware de moderación con umbrales configurables y respuestas instrumentadas",
    version="1.0.0"
)

@app.post("/moderate", response_model=ModerationResponse)
async def moderate_endpoint(request: ModerationRequest):
    """
    Endpoint principal REST para evaluar contenido con el middleware de moderación.
    """
    try:
        return evaluate_moderation(request.input_text, request.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
