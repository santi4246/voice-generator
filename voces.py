# voces.py (versión de depuración)
import os
import re
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime
from google.cloud import texttospeech
from google.api_core import exceptions as g_exceptions

DEFAULT_INPUT_MODULE = "voice_input.py"

def load_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location("voice_input_module", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo desde {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def find_ssml_and_voice(mod):
    ssml = None
    for name in ("SSML", "ssml"):
        if hasattr(mod, name):
            ssml = getattr(mod, name)
            break
    voice_text = None
    for name in ("VOICE_INFO", "VOICE", "voice_info", "voice"):
        if hasattr(mod, name):
            voice_text = getattr(mod, name)
            break
    if ssml is None:
        raise ValueError("No se encontró variable SSML en el módulo de entrada.")
    if voice_text is None:
        raise ValueError("No se encontró la variable de ficha de voz (VOICE_INFO / VOICE) en el módulo de entrada.")
    if not isinstance(ssml, str):
        raise TypeError("La variable SSML debe ser un string con SSML válido.")
    if not isinstance(voice_text, str):
        voice_text = str(voice_text)
    return ssml, voice_text

def parse_voice_block(voice_block: str):
    out = {}
    for raw_line in voice_block.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip().lower()] = v.strip()
    return out

def choose_language_from_parsed(parsed):
    langs = parsed.get("languages") or parsed.get("language") or parsed.get("language_code")
    if not langs:
        return None
    first = [p.strip() for p in langs.replace(";", ",").split(",") if p.strip()]
    return first[0] if first else None

def get_client():
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and Path(env_path).is_file():
        print(f"Usando GOOGLE_APPLICATION_CREDENTIALS = {env_path}")
        return texttospeech.TextToSpeechClient()
    candidate = Path(__file__).parent / "tts-sa-key.json"
    if candidate.is_file():
        print(f"Usando credencial desde archivo: {candidate}")
        return texttospeech.TextToSpeechClient.from_service_account_file(str(candidate))
    print("Intentando cliente por defecto (ADC). Si falla, configurá credenciales.")
    return texttospeech.TextToSpeechClient()

def sanitize_ssml_for_api(ssml: str, language_code: str | None) -> str:
    if not ssml:
        return ssml
    # Eliminar wrapper <voice>...</voice>
    ssml_no_voice = re.sub(r'<voice\b[^>]*>(.*?)</voice>', r'\1', ssml, flags=re.IGNORECASE | re.DOTALL)
    # Ajustar o eliminar xml:lang
    if language_code:
        ssml_no_lang = re.sub(r'xml:lang\s*=\s*"[^"]*"', f'xml:lang="{language_code}"', ssml_no_voice, flags=re.IGNORECASE)
    else:
        ssml_no_lang = re.sub(r'\s+xml:lang\s*=\s*"[^"]*"', '', ssml_no_voice, flags=re.IGNORECASE)
    ssml_clean = re.sub(r'>\s+<', '><', ssml_no_lang)
    return ssml_clean

def synthesize_ssml(client, ssml_text: str, voice_name: str, language_code: str, out_path: Path, speaking_rate: float = 1.0, pitch: float = 0.0, use_ssml=True):
    if use_ssml:
        input_ = texttospeech.SynthesisInput(ssml=ssml_text)
    else:
        # si use_ssml=False enviamos texto plano (sin tags)
        input_ = texttospeech.SynthesisInput(text=ssml_text)
    voice = texttospeech.VoiceSelectionParams(language_code=language_code or "es-AR", name=voice_name)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speaking_rate, pitch=pitch)
    response = client.synthesize_speech(input=input_, voice=voice, audio_config=audio_config)
    out_path.write_bytes(response.audio_content)
    return out_path

def default_out_name(voice_name: str):
    safe = "".join(c if c.isalnum() else "_" for c in (voice_name or "tts"))
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return Path(f"tts_{safe}_{stamp}.mp3")

def extract_plain_text_from_ssml(ssml: str) -> str:
    # Extrae texto plano eliminando tags SSML (básico)
    text = re.sub(r'<[^>]+>', ' ', ssml)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:5000]  # límite práctico

def main():
    p = argparse.ArgumentParser(description="Depuración: Generar MP3 leyendo SSML y ficha de voz (muestra más info).")
    p.add_argument("--input-file", "-i", default=DEFAULT_INPUT_MODULE, help="Archivo Python que define SSML y VOICE_INFO.")
    p.add_argument("--out", "-o", help="Archivo MP3 de salida.")
    p.add_argument("--rate", type=float, default=1.0, help="speaking_rate (opcional).")
    p.add_argument("--pitch", type=float, default=0.0, help="pitch en semitonos (opcional).")
    args = p.parse_args()

    input_path = Path(args.input_file)
    if not input_path.is_file():
        print(f"ERROR: No se encontró el archivo de entrada: {input_path.resolve()}")
        return

    try:
        mod = load_module_from_path(input_path)
        ssml_text, voice_block = find_ssml_and_voice(mod)
    except Exception as e:
        print("ERROR cargando o parseando el módulo de entrada:", e)
        return

    parsed = parse_voice_block(voice_block)
    voice_name = parsed.get("name")
    language_code = choose_language_from_parsed(parsed)

    print("Ficha parseada:", parsed)
    print("Voice name:", voice_name)
    print("Language code:", language_code)

    if not voice_name:
        print("ERROR: no se encontró 'Name' en la ficha de voz.")
        return
    if not language_code:
        print("ADVERTENCIA: no se pudo inferir 'Languages'; usando 'es-AR' por defecto.")
        language_code = "es-AR"

    try:
        client = get_client()
    except Exception as e:
        print("ERROR creando cliente:", e)
        return

    # listar voces disponibles (para verificar exactitud del name)
    try:
        available = {v.name: v for v in client.list_voices().voices}
        print(f"Se encontraron {len(available)} voces en la API.")
        if voice_name not in available:
            print(f"ADVERTENCIA: La voz '{voice_name}' no figura entre las voces retornadas por la API.")
            print("Nombres de voz (muestra hasta 30):", list(list(available.keys())[:30]))
        else:
            print(f"La voz '{voice_name}' sí figura en la lista. Languages de la voz: {available[voice_name].language_codes}")
    except Exception as e:
        print("No pude listar voces (continuo):", e)
        available = {}

    # Sanitizar SSML y guardar a archivo para inspección
    ssml_to_send = sanitize_ssml_for_api(ssml_text, language_code)
    ssml_file = Path("ssml_to_send.xml")
    ssml_file.write_text(ssml_to_send, encoding="utf-8")
    print(f"SSML sanitizado guardado en: {ssml_file.resolve()} (tamaño {ssml_file.stat().st_size} bytes)")

    out_path = Path(args.out) if args.out else default_out_name(voice_name)

    # Intento 1: enviar SSML
    try:
        print("Intentando síntesis SSML con voice:", voice_name, "language:", language_code)
        result = synthesize_ssml(client, ssml_to_send, voice_name, language_code, out_path, speaking_rate=args.rate, pitch=args.pitch, use_ssml=True)
        print("Generado (SSML):", result.resolve())
        return
    except g_exceptions.BadRequest as e:
        print("BadRequest (400) recibido de la API:")
        print(repr(e))
        try:
            print("Detalle (message):", e.message)
        except Exception:
            pass
        try:
            print("Errors:", getattr(e, "errors", None))
        except Exception:
            pass
    except g_exceptions.GoogleAPICallError as e:
        print("GoogleAPICallError:", repr(e))
    except Exception as e:
        print("Excepción al sintetizar SSML:", repr(e))

    # Si llegamos aquí, intentar fallback con texto plano
    try:
        plain_text = extract_plain_text_from_ssml(ssml_text)
        if not plain_text:
            print("No hay texto plano extraíble para fallback.")
            return
        fallback_out = out_path.with_name(out_path.stem + "_fallback.mp3")
        print("Intentando fallback con texto plano (primeros 5000 chars):", plain_text[:200])
        result2 = synthesize_ssml(client, plain_text, voice_name, language_code, fallback_out, speaking_rate=args.rate, pitch=args.pitch, use_ssml=False)
        print("Generado (fallback texto plano):", result2.resolve())
    except Exception as e:
        print("Falló también el fallback de texto plano:", repr(e))
        print("Por favor pega aquí la salida completa que ves en la consola y el contenido (o un fragmento) de ssml_to_send.xml para que lo revise.")
    
if __name__ == "__main__":
    main()