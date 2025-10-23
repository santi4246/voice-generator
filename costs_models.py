#!/usr/bin/env python3
"""
costs_models.py

Cuenta caracteres en SSML y estima costos según el modelo declarado en VOICE_INFO.

Uso:
  python costs_models.py --ssml-file ejemplo.ssml --voice es-AR-Wavenet-A
  cat ejemplo.ssml | python costs_models.py --voice es-AR-Wavenet-A
"""

import argparse
import sys
import re
import html
from pathlib import Path

# VOICE_INFO: actualizar precios según tarifas reales.
# key: voice name (ej. 'es-AR-Wavenet-A')
# model_type: 'WaveNet' | 'Neural2' | 'Standard' (u otros categóricos)
# price_per_million: precio en USD por 1,000,000 caracteres para ese tipo de voz
VOICE_INFO = {
    'es-AR-Wavenet-A':    {'model_type': 'WaveNet',  'price_per_million': 16.00},
    'es-AR-Neural2-A':    {'model_type': 'Neural2', 'price_per_million': 20.00},
    'es-AR-Standard-A':   {'model_type': 'Standard','price_per_million': 4.00},
    # Añade aquí más voces/entradas según tu proyecto...
}

# Free tier por tipo de modelo (caracteres gratuitos por mes, ejemplo)
FREE_TIER_CHARS = {
    'WaveNet': 1_000_000,    # ejemplo: 1M gratis para WaveNet
    'Neural2': 1_000_000,    # si aplica igual que WaveNet
    'Standard': 4_000_000,   # ejemplo: 4M gratis para Standard
}

def read_ssml_from_file(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def read_ssml_from_stdin() -> str:
    return sys.stdin.read()

def strip_ssml_tags(ssml: str) -> str:
    """Elimina etiquetas XML/SSML y desempaqueta entidades HTML."""
    text = re.sub(r'<[^>]+>', '', ssml)         # quita tags <...>
    text = html.unescape(text)                 # convierte &amp; etc a caracteres reales
    return text

def estimate_cost(char_count: int, model_type: str, price_per_million: float, free_tier: int) -> dict:
    """Calcula coste estimado y retorna un dict con desglose.

    Además calcula el precio unitario por 10,000 caracteres y una estimación
    del coste para 10,000 caracteres teniendo en cuenta la franquicia gratuita.
    """
    billable_chars = max(0, char_count - free_tier)
    cost = (billable_chars / 1_000_000.0) * price_per_million

    # Precio por 10,000 caracteres (1,000,000 / 10,000 = 100)
    price_per_10k = price_per_million / 100.0

    # Estimación del coste para 10,000 caracteres tras aplicar la franquicia.
    # Si los caracteres facturables son 0 -> coste 0. Si hay menos de 10k facturables,
    # se prorratea el coste.
    billable_for_10k = max(0, min(10_000, billable_chars))
    estimated_cost_usd_for_10k = (billable_for_10k / 10_000.0) * price_per_10k

    return {
        'model_type': model_type,
        'price_per_million': price_per_million,
        'price_per_10k': price_per_10k,
        'free_tier_chars': free_tier,
        'total_chars': char_count,
        'billable_chars': billable_chars,
        'estimated_cost_usd': cost,
        'estimated_cost_usd_for_10k': estimated_cost_usd_for_10k,
    }

def pretty_print(result: dict, label: str):
    print(f"\nEstimación para: {label}")
    print(f"  Modelo: {result['model_type']}")
    print(f"  Precio por 1,000,000 chars: ${result['price_per_million']:.4f}")
    # Mostrar también el precio por 10k
    if 'price_per_10k' in result:
        print(f"  Precio aproximado por 10,000 chars: ${result['price_per_10k']:.6f}")
    print(f"  Franquicia gratuita (mensual): {result['free_tier_chars']:,} caracteres")
    print(f"  Total de caracteres {label}: {result['total_chars']:,}")
    print(f"  Caracteres facturables (tras franquicia): {result['billable_chars']:,}")
    print(f"  Coste estimado: ${result['estimated_cost_usd']:.6f}")
    if 'estimated_cost_usd_for_10k' in result:
        print(f"  Coste estimado para 10,000 chars (teniendo en cuenta franquicia): ${result['estimated_cost_usd_for_10k']:.6f}")

def main():
    parser = argparse.ArgumentParser(description="Cuenta caracteres SSML y estima costos según VOICE_INFO. Toma valores desde voice_input.py si existe.")
    parser.add_argument('--ssml-file', '-f', type=str, help='Archivo que contiene SSML. Si no se provee, se lee de stdin o desde voice_input.SSML/SSML_FILE si existe.')
    parser.add_argument('--voice', '-v', type=str, help='Nombre de la voz (clave en VOICE_INFO). Si no se provee, se usará voice_input.VOICE o la primera voz en VOICE_INFO.')
    parser.add_argument('--use-text-only', action='store_true', help='Estimar costos basados en texto limpio (sin tags) además del SSML bruto.')
    args = parser.parse_args()

    # Intentar cargar voice_input.py
    voice_input = None
    try:
        import voice_input
        voice_input = voice_input
    except Exception:
        voice_input = None

    # Sobrescribir VOICE_INFO/FREE_TIER_CHARS si están en voice_input
    global VOICE_INFO, FREE_TIER_CHARS
    if voice_input is not None:
        if hasattr(voice_input, 'VOICE_INFO'):
            VOICE_INFO = getattr(voice_input, 'VOICE_INFO')
        if hasattr(voice_input, 'FREE_TIER_CHARS'):
            FREE_TIER_CHARS = getattr(voice_input, 'FREE_TIER_CHARS')

    # Determinar voz: CLI > voice_input.VOICE > primera en VOICE_INFO
    voice = args.voice if args.voice else (getattr(voice_input, 'VOICE', None) if voice_input is not None else None)
    if not voice:
        try:
            voice = next(iter(VOICE_INFO.keys()))
        except StopIteration:
            voice = None

    if not voice:
        print("No se especificó ninguna voz y VOICE_INFO está vacío. Define VOICE en voice_input.py o pasa --voice.")
        sys.exit(2)

    if voice not in VOICE_INFO:
        print(f"Voz '{voice}' no encontrada en VOICE_INFO. Voces disponibles:")
        for k in sorted(VOICE_INFO.keys()):
            print(f"  - {k}  ({VOICE_INFO[k].get('model_type', 'Unknown')})")
        sys.exit(2)

    # Determinar use_text_only por CLI o voice_input
    use_text_only = args.use_text_only or (bool(getattr(voice_input, 'USE_TEXT_ONLY', False)) if voice_input is not None else False)

    # Obtener SSML: priority SSML string in voice_input > SSML_FILE in voice_input > CLI file > stdin
    ssml = None
    if voice_input is not None and hasattr(voice_input, 'SSML') and getattr(voice_input, 'SSML'):
        ssml = getattr(voice_input, 'SSML')
    elif voice_input is not None and hasattr(voice_input, 'SSML_FILE') and getattr(voice_input, 'SSML_FILE'):
        try:
            ssml = read_ssml_from_file(Path(getattr(voice_input, 'SSML_FILE')))
        except Exception as e:
            print(f"No se pudo leer SSML desde voice_input.SSML_FILE: {e}")
            ssml = None

    if ssml is None:
        if args.ssml_file:
            ssml = read_ssml_from_file(Path(args.ssml_file))
        else:
            if sys.stdin.isatty():
                print("No se proporcionó SSML. Pasa el SSML por stdin, usa --ssml-file o define SSML/SSML_FILE en voice_input.py.")
                sys.exit(1)
            ssml = read_ssml_from_stdin()

    ssml = ssml.strip()
    raw_chars = len(ssml)
    text_only = strip_ssml_tags(ssml)
    text_chars = len(text_only)

    voice_meta = VOICE_INFO[voice]
    model_type = voice_meta.get('model_type', 'Unknown')
    price_per_million = float(voice_meta.get('price_per_million', 0.0))
    free_tier = FREE_TIER_CHARS.get(model_type, 0)

    print("\nResumen de conteo:")
    print(f"  - Longitud SSML (incluye etiquetas): {raw_chars:,} caracteres")
    print(f"  - Longitud texto (sin tags): {text_chars:,} caracteres")
    print(f"  - Voz seleccionada: {voice} (tipo: {model_type})")

    result_ssml = estimate_cost(raw_chars, model_type, price_per_million, free_tier)
    pretty_print(result_ssml, label="SSML bruto")

    if use_text_only:
        result_text = estimate_cost(text_chars, model_type, price_per_million, free_tier)
        pretty_print(result_text, label="Texto limpio (sin tags)")

    print("\nObservaciones:")
    print("  - Google Cloud factura por caracteres procesados (incluyendo etiquetas SSML).")
    print("  - Si define variables en voice_input.py, estas se han cargado automáticamente (VOICE, SSML, SSML_FILE, VOICE_INFO, FREE_TIER_CHARS, USE_TEXT_ONLY).")
    print("  - Actualiza los valores en VOICE_INFO y FREE_TIER_CHARS con las tarifas y límites reales.")
    print("  - Esta es una estimación. Revisa la facturación del proyecto en Google Cloud para valores finales.\n")

if __name__ == "__main__":
    main()