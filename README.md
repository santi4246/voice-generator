# Proyecto de Síntesis de Voz con Google Cloud Text-to-Speech

Este proyecto permite convertir texto en audio utilizando la API de Google Cloud Text-to-Speech (TTS), con soporte para SSML (Speech Synthesis Markup Language) para controlar la entonación, pausas y otros aspectos del habla. Está orientado a generar audios de alta calidad con voces neurales y personalizables.

---

## Características principales

- Soporte para múltiples voces y modelos (WaveNet, Neural2, Standard, Chirp3 HD, etc).
- Uso de SSML para mejorar la naturalidad y expresividad del audio.
- Estimación de costos basada en la cantidad de caracteres y tipo de voz.
- Flexibilidad para usar SSML desde archivo o variable en el código.
- Manejo seguro de credenciales mediante archivo JSON de cuenta de servicio.
- Scripts para facilitar la generación y control de audio.

---

## Configuración del entorno

1. **Crear proyecto en Google Cloud Platform (GCP)**  
   - Habilitar la API de Text-to-Speech.  
   - Configurar facturación (requerida para usar la API, aunque hay un nivel gratuito mensual).  
   - Crear una cuenta de servicio con permisos para Text-to-Speech.  
   - Descargar el archivo JSON con las credenciales.

2. **Configurar variables de entorno**  
   - Exportar la variable `GOOGLE_APPLICATION_CREDENTIALS` apuntando al archivo JSON descargado:  
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/ruta/a/tts-sa-key.json"
     ```

3. **Instalar dependencias**  
   - Usar Python 3.7+  
   - Instalar librerías necesarias:  
     ```bash
     pip install google-cloud-texttospeech
     ```

4. **Configurar el proyecto local**  
   - Colocar el archivo de credenciales en un lugar seguro y agregarlo a `.gitignore`.  
   - Definir las variables SSML y voz en `voice_input.py` o usar archivos externos.  
   - Ajustar parámetros de voz y modelo según necesidades.

---

## Modos de uso

- **Generar audio desde SSML en variable**  
  Definir la variable `SSML` en `voice_input.py` con el texto SSML y ejecutar el script principal.

- **Generar audio desde archivo SSML**  
  Definir la ruta en `voice_input.py` con `SSML_FILE = "archivo.ssml"` o pasar el archivo con argumento `--ssml-file`.

- **Estimar costos**  
  Usar el script `costs_models.py` para contar caracteres y estimar el costo según la voz y modelo seleccionado.

- **Ejemplo de ejecución**  
  ```bash
  python synthesize.py --voice es-AR-Wavenet-A --ssml-file mensaje.ssml
  ```

## Tecnologías aplicadas
```
Google Cloud Text-to-Speech API: Servicio de síntesis de voz en la nube con soporte para SSML y voces neurales.
Python 3: Lenguaje principal para los scripts y automatización.
SSML: Lenguaje XML para controlar la síntesis de voz.
Manejo de credenciales: Uso de cuentas de servicio y variables de entorno para seguridad.
Git: Control de versiones con exclusión de archivos sensibles mediante .gitignore.
```
---
### Notas importantes
```bash
Facturación en Google Cloud: La API requiere que tengas facturación habilitada en tu proyecto, aunque ofrece un nivel gratuito mensual (por ejemplo, 1 millón de caracteres para WaveNet). Revisa los límites y costos en la página oficial de precios.
Seguridad: Nunca subas el archivo JSON de credenciales a repositorios públicos. Usa .gitignore para evitarlo.
Licencia: Este proyecto está bajo una licencia personalizada para uso personal y no comercial. Consulta el archivo LICENSE para más detalles.
Extensibilidad: Podés adaptar los scripts para otros idiomas, voces o integrarlos en aplicaciones más grandes.
Contacto: Para dudas o sugerencias, podés abrir un issue o contactarme directamente.
```
---
```
¡Gracias por usar este proyecto para crear audios con voz natural y controlada!
👤 Autor
Santiago Romero / https://www.santiago-romero.online / https://www.linkedin.com/in/santiago-romero-santi4246/
```