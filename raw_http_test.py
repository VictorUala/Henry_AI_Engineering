"""
PRUEBA DE LLAMADA REST HTTP DIRECTA (Sin usar la librería de OpenAI)
Demuestra que la API REST de OpenAI responde directamente a solicitudes HTTP POST.
"""

import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

# Configurar consola UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: No se encontró OPENAI_API_KEY en .env")
    sys.exit(1)

# 1. Definir URL del Endpoint oficial REST de OpenAI
url = "https://api.openai.com/v1/chat/completions"

# 2. Definir Encabezados HTTP (Headers) con la API Key y el tipo de contenido
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 3. Definir el Payload (Cuerpo de la solicitud) en JSON
payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "Sos un tutor de IA conciso."},
        {"role": "user", "content": "Confirmame en 1 sola oración si una llamada HTTP POST pura funciona."}
    ],
    "temperature": 0.1,
    "max_tokens": 60
}

print("--- 🌐 Enviando HTTP POST directo a https://api.openai.com/v1/chat/completions ---")

# Convertir el diccionario a bytes JSON
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        response_body = response.read().decode('utf-8')
        response_json = json.loads(response_body)
        
        print("\n--- 📥 Respuesta HTTP 200 OK de OpenAI ---")
        respuesta_texto = response_json['choices'][0]['message']['content']
        tokens = response_json['usage']['total_tokens']
        
        print(f"Texto devuelto: {respuesta_texto}")
        print(f"Tokens totales consumidos: {tokens}")
        print("\n✅ ¡DEMOSTRADO! La llamada HTTP POST pura funcionó sin necesidad de la librería de OpenAI.")

except Exception as e:
    print(f"❌ Error en la llamada HTTP: {e}")
