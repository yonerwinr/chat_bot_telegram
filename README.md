# 📡 Bot de Monitoreo de Canales de Telegram en Vivo

Este bot se encarga de escuchar en tiempo real cualquier canal de Telegram (público o privado) del que seas miembro, y cuando detecta un mensaje específico o palabras clave, te envía una alerta instantánea directamente a tus **Mensajes Guardados** en Telegram.

---

## 💡 ¿Por qué no en Vercel?
**Vercel es una plataforma *Serverless*:** sus funciones solo se ejecutan cuando reciben una petición web y se apagan en pocos segundos.
Para escuchar mensajes de un canal ajeno de Telegram en tiempo real, se requiere una conexión continua (**24/7 permanente**) con los servidores de Telegram. Por ello, más abajo te dejamos opciones **100% gratuitas** adecuadas para esto (como **Koyeb** o en tu propia PC).

---

## 🛠️ Paso 1: Obtener tus credenciales oficiales de Telegram

Telegram permite a cualquier usuario crear una aplicación para conectarse:

1. Entra en tu navegador a: **[https://my.telegram.org](https://my.telegram.org)**
2. Inicia sesión con el número de teléfono de tu cuenta de Telegram (recibirás un código dentro de tu app de Telegram).
3. Haz clic en **"API development tools"**.
4. Llena los campos (puedes poner cualquier nombre, por ejemplo en App title: `MonitorBot` y en Short name: `monbot`).
5. Copia tu **`api_id`** (número) y tu **`api_hash`** (cadena alfanumérica).

---

## ⚙️ Paso 2: Configurar tu archivo `.env`

1. En esta carpeta, copia o renombra el archivo `.env.example` a `.env`:
   ```bash
   copy .env.example .env
   ```
2. Abre `.env` con cualquier editor y rellena tus datos:
   ```env
   TELEGRAM_API_ID=12345678
   TELEGRAM_API_HASH=tu_api_hash_aqui

   # Canales a monitorear (puedes poner 1, 2 o más separados por comas)
   TARGET_CHANNELS=canal_uno,canal_dos


   # Palabras que activarán la alerta (separadas por coma)
   # Si lo dejas vacío, te notificará de TODOS los mensajes del canal
   KEYWORDS=urgente,descuento,bitcoin,oferta

   # Coincidencia exacta (True/False)
   EXACT_MATCH=False

   # Sensible a mayúsculas/minúsculas (True/False)
   CASE_SENSITIVE=False

   # Dónde recibir el aviso: 'me' son tus Mensajes Guardados de Telegram
   ALERT_DESTINATION=me

   # Horario de funcionamiento (Lunes a Viernes de 7:00 AM a 8:00 PM)
   SCHEDULE_ENABLED=True
   START_HOUR=7
   END_HOUR=20
   # Zona horaria (Opcional, por defecto toma la hora de tu sistema)
   TIMEZONE=
   ```


---

## 🚀 Paso 3: Probar el Bot en tu PC

1. Abre la terminal en esta carpeta y ejecuta:
   ```bash
   python main.py
   ```
2. La **primera vez**, Telegram te pedirá en la terminal:
   - Tu número de teléfono con prefijo internacional (ejemplo: `+34...` o `+52...`).
   - El código de confirmación que te llegará a la app de Telegram.
   - Si tienes verificación en dos pasos (contraseña en Telegram), te la pedirá.
3. Se generará un archivo `session_telegram.session`. **A partir de ahí, no volverá a pedirte el código.**
4. Verás en pantalla:
   ```
   🟢 Bot a la escucha de nuevos mensajes. Esperando eventos...
   ```
5. En cuanto se publique un mensaje en el canal que contenga tus palabras clave, recibirás una notificación en tus **Mensajes Guardados** con el enlace directo y el mensaje original reenviado.

---

## ☁️ Paso 4: Cómo alojarlo 100% GRATIS 24/7 (En la Nube)

Si no quieres tener tu computadora encendida todo el tiempo, la mejor opción 100% gratuita es **Koyeb**:

### A) Generar tu sesión para la nube
En la nube no se pueden guardar archivos locales permanentemente en el plan gratuito, así que usamos una **StringSession**:
1. En tu PC ejecuta:
   ```bash
   python generar_sesion.py
   ```
2. Sigue las instrucciones. Te imprimirá una clave larga (`TELEGRAM_STRING_SESSION=...`).
3. Guarda esa clave.

### B) Desplegar en Koyeb (Gratis 24/7)
1. Sube tu carpeta a un repositorio privado en **GitHub** (el archivo `.gitignore` ya protege tus claves y sesiones).
2. Entra en **[https://www.koyeb.com](https://www.koyeb.com)** y crea una cuenta gratis.
3. Haz clic en **"Create App"** -> **"GitHub"** y selecciona tu repositorio.
4. En **Instance type**, elige el tamaño gratuito (**Eco Free / Nano**).
5. En la sección **Environment Variables**, añade:
   - `TELEGRAM_API_ID`: tu api_id
   - `TELEGRAM_API_HASH`: tu api_hash
   - `TARGET_CHANNEL`: canal a monitorear
   - `KEYWORDS`: palabras clave
   - `ALERT_DESTINATION`: me
   - `TELEGRAM_STRING_SESSION`: la clave larga generada en el paso A.
6. Haz clic en **"Deploy"**.

¡Listo! Tu bot estará escuchando los mensajes 24/7 sin costo alguno.
