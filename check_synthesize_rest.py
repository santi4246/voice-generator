#!/usr/bin/env python3
# check_synthesize_rest.py
# Llama al endpoint REST v1/text:synthesize y muestra la respuesta cruda

import json
import sys
from google.auth.transport.requests import Request
import google.auth

# Si querés usar tu SSML desde voice_input.py
try:
    from voice_input import SSML, VOICE
except Exception:
    # SSML de fallback mínimo si no existe voice_input.py
    SSML = "<speak>Hola</speak>"
    VOICE = "es-US-Chirp-HD-O"

def get_access_token():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token, project

def call_synthesize(ssml_text, voice_name="es-US-Chirp-HD-O", language_code="es-US"):
    token, project = get_access_token()
    import requests
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "input": {"ssml": ssml_text},
        "voice": {"languageCode": language_code, "name": voice_name},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    print("==> Enviando petición REST a", url)
    print("Payload (truncado a 1000 chars):")
    s = json.dumps(payload, ensure_ascii=False, indent=2)
    print(s[:1000])
    resp = requests.post(url, headers=headers, json=payload)
    print("\n==> HTTP status:", resp.status_code)
    # imprimir body completo (posible JSON de error)
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)

if __name__ == "__main__":
    try:
        call_synthesize(SSML, VOICE, "es-US")
    except Exception as e:
        print("Error al ejecutar la petición REST:", repr(e))
        sys.exit(1)