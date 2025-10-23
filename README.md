# Google Cloud Text-to-Speech — SSML + Scripts de Prueba

## Descripción
Este repositorio contiene utilidades y scripts para sintetizar audio con Google Cloud Text-to-Speech usando SSML. Se separaron las configuraciones de voz y entrada en `voces.py` y `voice_input.py` y se añadieron comprobaciones más robustas (ver `checkApi.py`). También hay scripts de prueba para sintetizar MP3 (por ejemplo `synth_test.py`) y un sintetizador principal que usa las variables de `voice_input.py`.

---

## Requisitos principales
- Python 3.8+  
- Cuenta de Google Cloud con billing habilitado en el proyecto que vas a usar.  
- Text-to-Speech API habilitada: `texttospeech.googleapis.com`.  
- Service Account con key JSON para autenticación (recomendado: roles mínimos indicados abajo).

---

## Instalación (recomendada)
1. Clonar repo y crear virtualenv:
```bash
git clone <tu-repo>
cd <tu-repo>
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows cmd
.\.venv\Scripts\activate.bat
# mac / linux
source .venv/bin/activate
```
2. Instalar dependencias:
```bash
python -m pip install --upgrade pip
python -m pip install google-cloud-texttospeech google-api-python-client google-auth requests
```

## Archivos y scripts importantes
- voces.py
Diccionario VOICE_INFO con metadatos de voces y la función resolve_voice(voice_key) que normaliza la entrada y devuelve (voice_name, language_code, voice_meta)
- voice_input.py
Variables de entrada que usa el sintetizador:
SSML (string) — SSML o texto a sintetizar.
VOICE (string) — clave de voz (debe corresponder a una entrada en VOICE_INFO)
- checkApi.py
Verifica:
Que el JSON de la service account exista y sea legible.
Que la API Text-to-Speech esté habilitada en el proyecto.
Usa gcloud si está disponible; si no, usa la Service Usage REST API con el JSON de la cuenta de servicio.
Uso: 
```bash
python checkApi.py
```
- synth_test.py
Script mínimo para generar un MP3 de prueba usando SSML. Ajustá key_path o la variable de entorno.
Uso: 
```bash
python synth_test.py
```
- sintetizador.py
Lee voice_input.SSML y voice_input.VOICE, resuelve la voz con voces.resolve_voice() y escribe el audio resultante.
Uso: 
```bash
python sintetizador.py
```
- .gitignore
Debe incluir la línea para ignorar la clave:
tts-sa-key.json
*.json
.venv/

## Variables de entorno y autenticación
1. Exportar el path del JSON de la service account:
- Windows PowerShell:
```bash
$env:GOOGLE_APPLICATION_CREDENTIALS = 'D:\Documentos\Proyectos\SSML\tts-sa-key.json'
python checkApi.py
```
- Windows cmd:
```bash
set GOOGLE_APPLICATION_CREDENTIALS=D:\Documentos\Proyectos\SSML\tts-sa-key.json
python checkApi.py
```
- mac / linux:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/home/usuario/tts-sa-key.json"
python checkApi.py
```
2. Alternativa: pasar key_path explícito en los scripts (checkApi.py, synth_test.py).

## Permisos recomendados para la Service Account
- roles/serviceusage.serviceUsageConsumer (permite consultar estado de APIs).
- roles/serviceusage.serviceUsageAdmin (si necesitás habilitar APIs programáticamente).
- Para sintetizar audio, la cuenta debe tener acceso al proyecto y la API habilitada.

## Comandos útiles (gcloud)
* Verificar instalación:
```bash
gcloud --version
where gcloud    # Windows
which gcloud    # mac/linux
```
* Habilitar API:
```bash
gcloud services enable texttospeech.googleapis.com --project=TU_PROJECT_ID
```
* Añadir rol a service account
```bash
gcloud projects add-iam-policy-binding TU_PROJECT_ID \
  --member="serviceAccount:MI_SA_EMAIL" \
  --role="roles/serviceusage.serviceUsageConsumer"
```

### Cómo listar voces disponibles
```python
from google.cloud import texttospeech
client = texttospeech.TextToSpeechClient()
voices = client.list_voices().voices
for v in voices:
    print(v.name, "-", v.language_codes)
```
 o ejecutar
```bash
python listar.py
```

---

## Consideraciones de uso y costes
* Google cobra por caracteres (incluye espacios, saltos de línea y la mayoría de tags SSML salvo <mark>).
* Free tier y costes (resumen)
  - Standard voices: free 0–4M caracteres / luego US4𝑝𝑜𝑟1𝑀𝑐ℎ𝑎𝑟𝑠𝑈𝑆4por1Mchars(US0.000004 por carácter).
  - WaveNet / Neural2: free 0–1M / luego US16𝑝𝑜𝑟1𝑀𝑐ℎ𝑎𝑟𝑠𝑈𝑆16por1Mchars(US0.000016 por carácter).
  - Chirp 3 (HD): free 0–1M / luego US30𝑝𝑜𝑟1𝑀𝑐ℎ𝑎𝑟𝑠𝑈𝑆30por1Mchars(US0.00003 por carácter)
  - Studio / algunas SKUs pueden cobrarse por byte y tener precios distintos.
  Consulta la tabla oficial: <a href="https://cloud.google.com/text-to-speech/pricing">Text-to-Speech pricing</a>

## Ejemplo de coste estimado para 10.000 caracteres
| Voz        | Precio por carácter (USD) | Coste para 10.000 caracteres (USD) |
|------------|---------------------------|-----------------------------------|
| Standard   | 0.000004                  | 0.04                              |
| WaveNet    | 0.000016                  | 0.16                              |
| Chirp 3 HD | 0.00003                   | 0.30                              |
| Studio     | ~0.00016 (por byte)       | ~1.60                             |

## Buenas prácticas y seguridad
- Nunca subas tu JSON de credenciales al repositorio. Añadilo a .gitignore.
- Usa roles mínimos necesarios en la service account.
- Para despliegues, usa Secret Manager o mecanismos seguros para credenciales.
- Documenta la voz usada y su disponibilidad.
- Controla el uso con alertas y presupuestos en Google Cloud Console.

## Errores comunes y soluciones rápidas
- FileNotFoundError al ejecutar gcloud → instalar Google Cloud SDK o ajustar PATH.
- ModuleNotFoundError: googleapiclient o google.cloud → instalar dependencias con pip.
- 403 Permission denied → asignar rol roles/serviceusage.serviceUsageConsumer a la service account.
- Voz no encontrada / error resolve_voice → asegurarse que VOICE en voice_input.py coincide con clave en VOICE_INFO.
- Audio "robótico" → probar voces avanzadas y mejorar SSML.

## Ejemplo de flujo mínimo para probar
- Habilitar billing y la API en el proyecto.
- Crear service account y descargar JSON.
- Exportar GOOGLE_APPLICATION_CREDENTIALS o pasar key_path a los scripts.
- Ejecutar:
```bash
python checkApi.py       # verifica credenciales y API habilitada
python synth_test.py     # genera voice-sample-10s.mp3 con SSML de ejemplo
python sintetizador.py   # sintetiza usando voice_input.py y voces.py
```

---

## Licencia
Este proyecto es para uso personal y educativo. No se permite su venta ni uso comercial sin autorización expresa.

---
```
¡Gracias por usar este proyecto para crear audios con voz natural y controlada!
👤 Autor
Santiago Romero / https://www.santiago-romero.online / https://www.linkedin.com/in/santiago-romero-santi4246/
```