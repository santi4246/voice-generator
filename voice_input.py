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

VOICE_INFO = """Name: es-US-Chirp-HD-O
Languages: es-US
SSML gender: FEMALE
Natural sample rate (Hz): 24000"""

VOICE = 'es-US-Chirp-HD-O'
SSML_FILE = None

VOICE_INFO = {
    'es-US-Chirp-HD-O':  {'model_type': 'Chirp3',  'price_per_million': 30.00},
    'es-AR-Neural2-A':   {'model_type': 'Neural2', 'price_per_million': 16.00},
    'es-AR-Wavenet-A':   {'model_type': 'WaveNet', 'price_per_million': 4.00},
    'es-AR-Standard-A':  {'model_type': 'Standard','price_per_million': 4.00},
    # ... otras voces
}

FREE_TIER_CHARS = {
    'Chirp3':  1_000_000,
    'Neural2': 1_000_000,
    'WaveNet': 4_000_000,
    'Standard':4_000_000,
    'Studio':  1_000_000,
}
USE_TEXT_ONLY = False