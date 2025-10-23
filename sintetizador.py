#!/usr/bin/env python3
# sintetizador.py

from google.cloud import texttospeech
from voces import sanitize_ssml_for_chirp, resolve_voice

# Importar variables de configuración
try:
    from voice_input import SSML, VOICE
except ImportError:
    print("No se pudo importar voice_input.py. Usando valores por defecto.")
    SSML = "<speak>Hola mundo</speak>"
    VOICE = "es-US-Wavenet-A"

def sintetizar_audio(ssml_input: str, voice_name: str, output_file: str = "output.mp3"):
    # Resolver la voz pasando VOICE_INFO
    voice_name_resolved, language_code, voice_meta = resolve_voice(voice_name)

    # Detectar si es voz Chirp para sanitizar SSML
    if voice_meta.get("type") == "chirp":
        ssml_a_usar = sanitize_ssml_for_chirp(ssml_input)
    else:
        ssml_a_usar = ssml_input

    # Crear cliente de Text-to-Speech
    client = texttospeech.TextToSpeechClient()

    # Preparar la entrada de síntesis
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_a_usar)

    # Configurar la voz
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code or "es-US",
        name=voice_name_resolved
    )

    # Configurar el formato de audio
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    print(f"SSML a enviar: {ssml_a_usar}")    

    # Llamar a la API para sintetizar
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Guardar el audio en archivo
    with open(output_file, "wb") as out:
        out.write(response.audio_content)

    print(f"Audio generado y guardado en: {output_file}")

if __name__ == "__main__":
    print(f"Usando voz: {VOICE}")
    sintetizar_audio(SSML, VOICE, "audio_generado.mp3")