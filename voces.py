import re
from typing import Optional, Tuple, Dict

# Diccionario de voces con claves normalizadas
VOICE_INFO: Dict[str, Dict] = {    
    "es-US-Wavenet-A": { "name": "es-US-Wavenet-A", "languageCode": "es-US", "type": "wavenet", "price_per_million": 4.00 },
    "es-US-Neural2-A": { "name": "es-US-Neural2-A", "languageCode": "es-US", "type": "neural", "price_per_million": 16.00 },    
    'es-US-Chirp-HD-O':  { "name": "es-US-Chirp-HD-O", "languageCode": "es-US", "type": "chirp3", "price_per_million": 30.00},
    # ... otras voces ...
}

def resolve_voice(voice_key: str) -> Optional[Tuple[str, str, Dict]]:
    """
    Resuelve el nombre de voz y devuelve (voice_name, language_code, voice_meta).
    Busca la voz en VOICE_INFO ignorando mayúsculas/minúsculas.
    """
    if not voice_key:
        return None

    key_norm = voice_key.strip().lower()
    voice_meta = VOICE_INFO.get(key_norm)

    if not voice_meta:
        # Buscar por coincidencia parcial en 'name'
        for meta in VOICE_INFO.values():
            if meta.get("name", "").lower() == key_norm:
                voice_meta = meta
                break
        else:
            raise KeyError(f"Voz '{voice_key}' no encontrada en VOICE_INFO.")

    voice_name = voice_meta.get("name", voice_key)
    language_code = voice_meta.get("languageCode", "es-US")

    return voice_name, language_code, voice_meta

def sanitize_ssml_for_chirp(ssml: str) -> str:
    """
    Sanitiza SSML para voces Chirp eliminando tags problemáticos como <break/>.
    Envuelve el texto en oraciones <s> para compatibilidad.
    """
    if not ssml:
        return "<speak><p></p></speak>"

    # Extraer contenido dentro de <speak> si existe
    inner = re.sub(r'^\s*<\s*speak[^>]*>\s*', '', ssml, flags=re.I)
    inner = re.sub(r'\s*<\s*/\s*speak\s*>\s*$', '', inner, flags=re.I)

    # Eliminar tags problemáticos
    inner = re.sub(r'<\s*break\b[^>]*?/?>', ' ', inner, flags=re.I)
    inner = re.sub(r'<\s*audio\b[^>]*?>.*?<\s*/\s*audio\s*>', ' ', inner, flags=re.I | re.S)
    inner = re.sub(r'<\s*par\b[^>]*?>.*?<\s*/\s*par\s*>', ' ', inner, flags=re.I | re.S)
    inner = re.sub(r'<\s*par\b[^>]*?/?>', ' ', inner, flags=re.I)

    # Quitar tags no permitidos (mantener texto)
    allowed_tags = {'s', 'p', 'emphasis', 'say-as', 'phoneme', 'sub'}
    def strip_disallowed_tags(match):
        tag = match.group(1).lower()
        return match.group(0) if tag in allowed_tags else ''
    inner = re.sub(r'<\s*/?\s*([a-zA-Z0-9:-]+)[^>]*?>', strip_disallowed_tags, inner)

    # Normalizar espacios y saltos de línea
    inner = re.sub(r'\r\n?', '\n', inner)
    inner = re.sub(r'<\s*/\s*p\s*>', '\n\n', inner, flags=re.I)
    inner = re.sub(r'<\s*p\b[^>]*>', '\n', inner, flags=re.I)
    inner = re.sub(r'<\s*/\s*s\s*>', '\n', inner, flags=re.I)
    inner = re.sub(r'<\s*s\b[^>]*>', '\n', inner, flags=re.I)
    inner = re.sub(r'\n\s*\n+', '\n\n', inner)
    inner = re.sub(r'[ \t]+', ' ', inner)

    # Dividir en oraciones
    paragraphs = [p.strip() for p in inner.split('\n\n') if p.strip()]
    s_chunks = []
    sentence_split = re.compile(r'(?<=[\.\!\?\…])\s+')
    for para in paragraphs:
        pieces = sentence_split.split(para) if sentence_split.search(para) else [para]
        s_chunks.extend(p.strip() for p in pieces if p.strip())

    if not s_chunks:
        text_only = re.sub(r'<[^>]+>', '', inner).strip()
        s_chunks = [p.strip() for p in sentence_split.split(text_only) if p.strip()]

    s_tags = "".join(f"<s>{chunk}</s>" for chunk in s_chunks)
    return f"<speak><p>{s_tags}</p></speak>"