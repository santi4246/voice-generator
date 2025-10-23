### checkApi.py (fragmento)
import os
from google.oauth2 import service_account
import google.auth.transport.requests
import requests

def check_api_enabled_rest(project_id, key_path=None):
    """
    Comprueba si texttospeech.googleapis.com está ENABLED para el proyecto.
    - project_id: ID del proyecto (ej. 'speaker-ad-475818')
    - key_path: ruta al JSON de la service account. Si es None, usará GOOGLE_APPLICATION_CREDENTIALS.
    Devuelve True/False.
    """
    # Resolver ruta de credenciales
    if key_path is None:
        key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not key_path:
        print("Error: no se proporcionó ruta de credenciales (key_path) y GOOGLE_APPLICATION_CREDENTIALS no está definido.")
        return False

    if not os.path.isfile(key_path):
        print(f"Error: archivo de credenciales no existe: {key_path}")
        return False

    try:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)  # obtiene token
        token = creds.token

        url = f"https://serviceusage.googleapis.com/v1/projects/{project_id}/services/texttospeech.googleapis.com"
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)

        if resp.status_code == 200:
            state = resp.json().get("state", "").upper()
            return state == "ENABLED"
        else:
            print("Error llamando a Service Usage API:", resp.status_code, resp.text)
            return False

    except Exception as e:
        print("Excepción al comprobar la API:", e)
        return False


def main():
    print("🔍 Verificando configuración de Text-to-Speech...\n")

    # ejemplo: podes obtener esto desde tu config o environment
    project_id = "speaker-ad-475818"
    key_path = r"D:\Documentos\Proyectos\SSML\tts-sa-key.json"  # <- ajustá si hace falta

    # Llamada: ahora pasamos key_path explícitamente (o dejá None si preferís usar GOOGLE_APPLICATION_CREDENTIALS)
    api_ok = check_api_enabled_rest(project_id, key_path)

    print(f"✅ Credenciales usadas: {key_path}")
    print(f"✅ Proyecto ID: {project_id}")
    print("✅ API Text-to-Speech habilitada:" , api_ok)


if __name__ == "__main__":
    main()