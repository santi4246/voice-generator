# voice_input.py

SSML = """<speak>
  Ese momento <break time="350ms"/>
  cuando todos miran <break time="350ms"/>
  y aprueban lo que estás usando. <break time="400ms"/>
  Con los Air Max, cada detalle cuenta. <break time="350ms"/>
  Diseño moderno, <break time="250ms"/>
  comodidad total, <break time="250ms"/>
  y un sonido que te hace sentir la música como nunca antes. <break time="350ms"/>
  No es solo escuchar. <break time="300ms"/>
  Es que todos noten tu estilo <break time="300ms"/>
  sin decir una palabra. <break time="450ms"/>
  ¡Hacé clic <break time="300ms"/> y llevátelos con 10% de descuento y envío gratis. <break time="250ms"/>
</speak>"""

SSML = """<speak>Hola, este es un ejemplo simple de audio text to speech.</speak>"""

VOICE = "es-US-Wavenet-A"

FREE_TIER_CHARS = {
    'Chirp3':  1_000_000,
    'Neural2': 1_000_000,
    'WaveNet': 4_000_000,
    'Standard':4_000_000,
    'Studio':  1_000_000,
}

"""
# Tomado del archivo voces_listadas que resulta de ejecutar el script listar.py
Name: es-US-Neural2-A
Languages: es-US
SSML gender: FEMALE
Natural sample rate (Hz): 24000
"""