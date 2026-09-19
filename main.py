import asyncio
import logging
import re
import sys
from datetime import datetime

# Asegurar compatibilidad UTF-8 en consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telethon import TelegramClient, events

from telethon.sessions import StringSession

import config

# Configuración básica de logs
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("TelegramMonitor")


def message_matches(text: str) -> tuple[bool, str]:
    """
    Verifica si el texto cumple con los criterios de coincidencia de palabras clave.
    Retorna (coincide: bool, palabra_encontrada: str)
    """
    if not text:
        return False, ""

    # Si no se configuraron palabras clave, todos los mensajes coinciden
    if not config.KEYWORDS:
        return True, "Todos los mensajes (sin filtro)"

    search_text = text if config.CASE_SENSITIVE else text.lower()

    for kw in config.KEYWORDS:
        target_kw = kw if config.CASE_SENSITIVE else kw.lower()

        if config.EXACT_MATCH:
            if search_text.strip() == target_kw.strip():
                return True, kw
        else:
            if target_kw in search_text:
                return True, kw

    return False, ""


def get_message_link(chat_entity, message_id: int) -> str:
    """Genera el enlace directo al mensaje si está disponible."""
    username = getattr(chat_entity, "username", None)
    if username:
        return f"https://t.me/{username}/{message_id}"
    
    chat_id = getattr(chat_entity, "id", None)
    if chat_id:
        # Para canales privados o grupos con supergrupo
        str_id = str(chat_id)
        if str_id.startswith("-100"):
            clean_id = str_id[4:]
        elif str_id.startswith("-"):
            clean_id = str_id[1:]
        else:
            clean_id = str_id
        return f"https://t.me/c/{clean_id}/{message_id}"
    
import os

async def start_health_server():
    """
    Servidor HTTP ultraligero integrado para plataformas como Render.
    Permite que el servicio gratuito de Render detecte el bot como 'Live'
    sin requerir librerías externas ni planes de pago.
    """
    port = os.getenv("PORT")
    if not port:
        return

    async def handle_ping(reader, writer):
        try:
            await reader.read(512)
            body = "OK - Telegram Monitor Activo\n"
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain; charset=utf-8\r\n"
                f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                "Connection: close\r\n\r\n"
                f"{body}"
            )
            writer.write(response.encode("utf-8"))
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    try:
        server = await asyncio.start_server(handle_ping, "0.0.0.0", int(port))
        logger.info(f"🌐 Servidor Web de salud iniciado en el puerto {port} (Render / Cloud)")
        asyncio.create_task(server.serve_forever())
    except Exception as e:
        logger.warning(f"No se pudo iniciar el servidor web de salud: {e}")


async def main():
    if not config.validate_config():
        sys_exit = 1
        return

    # Iniciar servidor de salud si Render asignó un puerto
    await start_health_server()

    print("=" * 60)
    print("🚀 INICIANDO MONITOR DE CANALES DE TELEGRAM")
    print("=" * 60)


    # Inicializar cliente (StringSession para nube o archivo local)
    if config.STRING_SESSION:
        session = StringSession(config.STRING_SESSION)
        logger.info("Usando sesión basada en TELEGRAM_STRING_SESSION (ideal para Cloud).")
    else:
        session = "session_telegram"
        logger.info("Usando sesión en archivo local 'session_telegram.session'.")

    client = TelegramClient(session, config.API_ID, config.API_HASH)

    await client.start()
    me = await client.get_me()
    logger.info(f"✅ Conectado exitosamente como: {me.first_name} (@{me.username or me.id})")

    # Resolver todos los canales configurados
    target_entities = []
    channels_display = []

    for ch_raw in config.TARGET_CHANNELS:
        ch_clean = ch_raw
        if "t.me/" in ch_clean:
            ch_clean = ch_clean.split("t.me/")[-1].replace("+", "").strip("/")

        try:
            if ch_clean.lstrip("-").isdigit():
                entity = await client.get_entity(int(ch_clean))
            else:
                entity = await client.get_entity(ch_clean)

            target_entities.append(entity)
            title = getattr(entity, "title", str(entity))
            username = getattr(entity, "username", None)
            channels_display.append(f"{title} (@{username})" if username else title)
            logger.info(f"✅ Canal vinculado: {title}")
        except Exception as e:
            logger.error(f"❌ Error al vincular canal '{ch_raw}': {e}")
            logger.error("Asegúrate de haberte unido previamente a ese canal con tu cuenta de Telegram.")

    if not target_entities:
        logger.error("❌ No se pudo vincular ningún canal válido. Revisa tu archivo .env.")
        return

    active_now, current_reason = config.is_within_working_hours()
    tz_label = config.TIMEZONE_STR if config.TIMEZONE_STR else "Hora local del sistema"
    schedule_desc = (
        f"Lunes a Viernes de {config.START_HOUR:02d}:00 a {config.END_HOUR:02d}:00 ({tz_label})"
        if config.SCHEDULE_ENABLED else "24/7 (Sin restricción)"
    )

    print("\n" + "-" * 50)
    print(f"📡 Canales Monitoreados ({len(target_entities)}):")
    for ch_info in channels_display:
        print(f"   • {ch_info}")
    print(f"🎯 Palabras clave: {config.KEYWORDS if config.KEYWORDS else 'Todos los mensajes'}")
    print(f"🔍 Modo exacto: {'Sí' if config.EXACT_MATCH else 'No (coincidencia parcial)'}")
    print(f"🔤 Sensible a mayúsculas: {'Sí' if config.CASE_SENSITIVE else 'No'}")
    print(f"⏰ Horario de monitoreo: {schedule_desc}")
    print(f"🚦 Estado inicial: {'🟢 ACTIVO' if active_now else f'🟡 PAUSADO ({current_reason})'}")
    print(f"📩 Destino del aviso: {config.ALERT_DESTINATION} (tus Mensajes Guardados)")
    print("-" * 50 + "\n")
    print("🟢 Bot a la escucha de nuevos mensajes en todos los canales. Esperando eventos...\n")

    # Configurar listener de eventos de nuevos mensajes para todos los canales
    @client.on(events.NewMessage(chats=target_entities))
    async def handler(event):
        # 1. Verificar si está dentro del horario permitido
        is_active, schedule_reason = config.is_within_working_hours()
        if not is_active:
            logger.info(f"⏸️ Mensaje ignorado fuera de horario: {schedule_reason}")
            return

        msg = event.message
        text = msg.text or msg.message or (msg.media and "[Mensaje con archivo/multimedia sin texto]") or ""
        
        matches, matched_keyword = message_matches(text)
        if not matches:
            return

        # Identificar el canal de origen del mensaje
        chat = await event.get_chat()
        origin_title = getattr(chat, "title", "Canal de Telegram")

        now_str = config.get_current_time().strftime("%Y-%m-%d %H:%M:%S")
        msg_link = get_message_link(chat, msg.id)

        logger.info(f"⚡ [COINCIDENCIA ENCONTRADA]: '{matched_keyword}' en [{origin_title}] (mensaje #{msg.id})")

        alert_text = (
            f"🚨 **ALERTA DE MENSAJE DETECTADO** 🚨\n\n"
            f"📢 **Canal de origen:** {origin_title}\n"
            f"🔑 **Coincidencia:** `{matched_keyword}`\n"
            f"🕒 **Fecha/Hora:** `{now_str}`\n"
            f"🔗 **Enlace directo:** [Ver mensaje en el canal]({msg_link})\n\n"

            f"📝 **Contenido del mensaje:**\n"
            f"----------------------------------------\n"
            f"{text[:1500] if text else '[Sin contenido de texto]'}\n"
            f"----------------------------------------"
        )

        destination = config.ALERT_DESTINATION
        if destination.lower() in ("me", "saved", "saved_messages"):
            destination = "me"

        try:
            # Enviar aviso estructurado
            await client.send_message(destination, alert_text, link_preview=False)
            
            # Reenviar el mensaje original para poder verlo con formato original, fotos, etc.
            try:
                await msg.forward_to(destination)
            except Exception as fw_err:
                logger.warning(f"No se pudo reenviar el mensaje original (quizás el canal prohíbe reenvíos): {fw_err}")
                
            logger.info("✅ Notificación enviada con éxito a tu chat de Telegram.")
        except Exception as send_err:
            logger.error(f"❌ Error al enviar la alerta a '{destination}': {send_err}")

    # Mantener el cliente activo permanentemente
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente.")
