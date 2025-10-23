# listar.py
import os
from pathlib import Path
from google.cloud import texttospeech
import sys

OUT_FILENAME = "voces_listadas.txt"

def get_client():
    # Si la variable de entorno está definida y apunta a un archivo -> usar ADC (cliente por defecto)
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and Path(env_path).is_file():
        # ADC funcionará cuando exista la variable, así que usamos el cliente por defecto
        return texttospeech.TextToSpeechClient()

    # Fallback: buscar un archivo JSON común en el mismo directorio
    candidate = Path(__file__).parent / "tts-sa-key.json"
    if candidate.is_file():
        return texttospeech.TextToSpeechClient.from_service_account_file(str(candidate))

    # Último recurso: intentar cliente por defecto (puede fallar si no hay credenciales)
    return texttospeech.TextToSpeechClient()

def format_voice(v):
    # Convierte un objeto Voice en texto legible
    genders = {
        0: "SSML_VOICE_GENDER_UNSPECIFIED",
        1: "MALE",
        2: "FEMALE",
        3: "NEUTRAL"
    }
    # v.ssml_gender es un enum int en algunas versiones; intentar resolver
    try:
        gender = genders.get(int(v.ssml_gender), str(v.ssml_gender))
    except Exception:
        gender = str(v.ssml_gender)

    lines = [
        f"Name: {v.name}",
        f"Languages: {', '.join(v.language_codes)}",
        f"SSML gender: {gender}",
        f"Natural sample rate (Hz): {getattr(v, 'natural_sample_rate_hertz', 'N/A')}",
    ]
    return "\n".join(lines)

def main():
    # Opcional: permitir pasar language_code y nombre de archivo por línea de comandos
    language_code = "es-AR"
    out_file = Path(__file__).parent / OUT_FILENAME

    # Si args: primer arg puede ser language_code, segundo nombre de salida
    if len(sys.argv) > 1:
        language_code = sys.argv[1]
    if len(sys.argv) > 2:
        out_file = Path(sys.argv[2])

    try:
        client = get_client()
    except Exception as e:
        print("ERROR creando cliente de Text-to-Speech:", e)
        return

    try:
        # Pedimos la lista filtrada por language_code (si el servicio lo soporta)
        resp = client.list_voices(language_code=language_code)
        voices = resp.voices
        if not voices:
            # Fallback si no hay voces para ese language_code
            resp_all = client.list_voices()
            voices = resp_all.voices
            header = f"No se encontraron voces para '{language_code}'. Listando todas las voces disponibles:\n\n"
        else:
            header = f"Voces disponibles para '{language_code}':\n\n"

        with out_file.open("w", encoding="utf-8") as fh:
            fh.write(header)
            for i, v in enumerate(voices, start=1):
                fh.write(f"--- Voz #{i} ---\n")
                fh.write(format_voice(v))
                fh.write("\n\n")

        print(f"Escritas {len(voices)} voces en: {out_file.resolve()}")
    except Exception as e:
        print("ERROR al listar voces o escribir el archivo:", e)

if __name__ == "__main__":
    main()