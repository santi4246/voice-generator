"""
# Encontrar una voz en específico
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
voices = client.list_voices()

for voice in voices.voices:
    if "es-US-Chirp-HD-O" in voice.name:
        print(f"Voz encontrada: {voice.name} - Idiomas: {voice.language_codes}")
"""

"""
# Salida de audio sencilla
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

synthesis_input = texttospeech.SynthesisInput(text="Hello, world!")

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Wavenet-D"
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

with open("output.mp3", "wb") as out:
    out.write(response.audio_content)

print("Audio content written to file 'output.mp3'")
"""
# Prueba mínima de salida de audio
from google.cloud import texttospeech

def prueba_minima():
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text="Hola, este es un texto de prueba.")

    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US",
        name="es-US-Wavenet-A"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open("prueba_minima.mp3", "wb") as out:
        out.write(response.audio_content)

    print("Archivo prueba_minima.mp3 generado correctamente.")

if __name__ == "__main__":
    prueba_minima()