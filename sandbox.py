"""
SANDBOX DE EXPERIMENTACIÓN - Henry AI Engineering Módulo 1
Este archivo es nuestro laboratorio para probar llamadas a la API de OpenAI,
inspeccionar respuestas crudas y entender cómo viajan los datos (REST/JSON).
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# Asegurar codificación UTF-8 en consola de Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Cargar la API key desde el archivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print("--- Verificacion de Credenciales ---")
if not api_key:
    print("[ERROR] No se encontro la OPENAI_API_KEY en el archivo .env")
    exit(1)
else:
    print(f"[OK] OPENAI_API_KEY detectada correctamente: {api_key[:7]}...{api_key[-4:]}\n")

# 2. Inicializar el cliente oficial de OpenAI
client = OpenAI(api_key=api_key)

# 3. Definir nuestro mensaje de prueba
prompt_usuario = "Explicame brevemente en 2 oraciones qué es una API REST y por qué la usamos en Inteligencia Artificial."

print("--- Enviando Solicitud a la API de OpenAI (gpt-4o-mini) ---")
print(f"Pregunta: '{prompt_usuario}'\n")

# 4. Hacer la llamada REST a la API de OpenAI
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Sos un tutor experto y conciso en AI Engineering."},
        {"role": "user", "content": prompt_usuario}
    ],
    temperature=0.2,
    max_tokens=150
)

# 5. Extraer y mostrar el resultado
contenido_respuesta = response.choices[0].message.content
tokens_usados = response.usage.total_tokens

print("--- Respuesta Recibida de la API ---")
print(contenido_respuesta)
print("\n--- Metricast Rapidas de esta llamada ---")
print(f"Tokens de Entrada (Prompt): {response.usage.prompt_tokens}")
print(f"Tokens de Salida (Completion): {response.usage.completion_tokens}")
print(f"Total de Tokens Consumidos: {tokens_usados}")
