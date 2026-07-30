"""
🚀 Script de Demostración Rápida para la Clase en Vivo
Muestra las 3 decisiones: Bloquear, Marcar y Permitir con trazabilidad y telemetría.
"""

import os
import sys
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import evaluate_moderation

examples = [
    ("user_101", "Comparte mi contraseña 1234"),
    ("user_102", "You are an idiot"),
    ("user_103", "Donde puedo descargar mi factura con IVA?")
]

print("==================================================================")
print("🛡️ DEMOSTRACIÓN EN VIVO: MIDDLEWARE DE MODERACIÓN DE CONTENIDO")
print("==================================================================\n")

for uid, text in examples:
    res = evaluate_moderation(text, uid)
    print(f"📥 INPUT: '{text}' (User ID: {uid})")
    print(f"RESULTADO: {res.action.upper()} | Severidad: {res.severity} | Request ID: {res.request_id}")
    print("RAZONES:")
    for r in res.reasons:
        print(f"  - [{r.code}] {r.description} (Fuente: {r.source})")
    print("-" * 65)
