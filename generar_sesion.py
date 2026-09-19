"""
Script de utilidad para generar una StringSession de Telethon.
Esta cadena te permite ejecutar tu bot en servidores en la nube (como Koyeb, Render, etc.)
sin tener que volver a iniciar sesión ni transferir archivos .session locales.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Asegurar compatibilidad UTF-8 en consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telethon import TelegramClient
from telethon.sessions import StringSession


load_dotenv()

async def main():
    print("=" * 65)
    print("🔑 GENERADOR DE SESIÓN EN CADENA (STRING SESSION) PARA CLOUD")
    print("=" * 65)
    
    api_id_env = os.getenv("TELEGRAM_API_ID")
    api_hash_env = os.getenv("TELEGRAM_API_HASH")

    if api_id_env and api_hash_env:
        use_env = input(f"¿Usar credenciales del archivo .env? (API_ID: {api_id_env}) [S/n]: ").strip().lower()
        if use_env in ("", "s", "si", "y", "yes"):
            api_id = int(api_id_env)
            api_hash = api_hash_env.strip()
        else:
            api_id = int(input("Introduce tu API_ID: ").strip())
            api_hash = input("Introduce tu API_HASH: ").strip()
    else:
        api_id = int(input("Introduce tu API_ID: ").strip())
        api_hash = input("Introduce tu API_HASH: ").strip()

    print("\nIniciando cliente de Telegram...")
    print("⚠️ Te pedirá tu número de teléfono (con código de país, ej: +34... o +52...)")
    print("⚠️ Luego Telegram te enviará un código numérico a tu app de Telegram.\n")

    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start()

    session_string = client.session.save()
    me = await client.get_me()

    print("\n" + "=" * 65)
    print(f"🎉 ¡Autenticado exitosamente como: {me.first_name}!")
    print("=" * 65)
    print("\nAquí tienes tu TELEGRAM_STRING_SESSION:")
    print("-" * 65)
    print(session_string)
    print("-" * 65)
    print("\n💡 Guarda este texto. Puedes colocarlo en tu .env o en las variables")
    print("de entorno de tu servidor Cloud (Koyeb, Render, etc.):")
    print(f"TELEGRAM_STRING_SESSION={session_string}\n")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
