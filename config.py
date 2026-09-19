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


# Cargar variables del archivo .env si existe
load_dotenv()

def get_env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "si")

API_ID_RAW = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()
STRING_SESSION = os.getenv("TELEGRAM_STRING_SESSION", "").strip()

# Canales a monitorear (soporta uno o varios separados por comas)
TARGET_CHANNELS_RAW = os.getenv("TARGET_CHANNELS") or os.getenv("TARGET_CHANNEL", "")
TARGET_CHANNELS = [ch.strip() for ch in TARGET_CHANNELS_RAW.split(",") if ch.strip()]


from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

# Procesar palabras clave
KEYWORDS_RAW = os.getenv("KEYWORDS", "")
KEYWORDS = [k.strip() for k in KEYWORDS_RAW.split(",") if k.strip()]

EXACT_MATCH = get_env_bool("EXACT_MATCH", False)
CASE_SENSITIVE = get_env_bool("CASE_SENSITIVE", False)
ALERT_DESTINATION = os.getenv("ALERT_DESTINATION", "me").strip()

# Configuración de Horario (Lunes a Viernes de 7:00 AM a 8:00 PM)
SCHEDULE_ENABLED = get_env_bool("SCHEDULE_ENABLED", True)
START_HOUR = int(os.getenv("START_HOUR", "7"))   # 7 AM
END_HOUR = int(os.getenv("END_HOUR", "20"))      # 8 PM (20:00)
TIMEZONE_STR = os.getenv("TIMEZONE", "").strip()

def get_current_time() -> datetime:
    """Obtiene la fecha y hora actual según la zona horaria configurada o local."""
    if TIMEZONE_STR and ZoneInfo:
        try:
            return datetime.now(ZoneInfo(TIMEZONE_STR))
        except Exception as e:
            pass
    return datetime.now()

def is_within_working_hours() -> tuple[bool, str]:
    """
    Verifica si estamos dentro del horario activo:
    - Lunes (0) a Viernes (4).
    - Entre START_HOUR (07:00) y END_HOUR (20:00).
    Retorna (activo: bool, razon: str)
    """
    if not SCHEDULE_ENABLED:
        return True, "Horario sin restricciones"

    now = get_current_time()
    weekday = now.weekday()  # 0 = Lunes, 5 = Sábado, 6 = Domingo
    
    # 1. Verificar fines de semana
    if weekday in (5, 6):
        dia = "Sábado" if weekday == 5 else "Domingo"
        return False, f"Fin de semana ({dia})"

    # 2. Verificar rango de horas (ej: 7 a 20)
    current_time_str = now.strftime("%H:%M")
    if now.hour < START_HOUR or now.hour >= END_HOUR:
        return False, f"Fuera de horario ({current_time_str} - activo de {START_HOUR:02d}:00 a {END_HOUR:02d}:00)"

    return True, f"Horario activo ({current_time_str})"


def validate_config():
    errors = []
    
    if not API_ID_RAW:
        errors.append("Falta 'TELEGRAM_API_ID' en el archivo .env")
    else:
        try:
            int(API_ID_RAW)
        except ValueError:
            errors.append("'TELEGRAM_API_ID' debe ser un número entero.")
            
    if not API_HASH:
        errors.append("Falta 'TELEGRAM_API_HASH' en el archivo .env")
        
    if not TARGET_CHANNELS:
        errors.append("Falta indicar al menos un canal a monitorear en 'TARGET_CHANNELS' (en .env)")

        
    if errors:
        print("\n❌ Error en la configuración (.env):")
        for err in errors:
            print(f"  - {err}")
        print("\nPor favor, edita tu archivo .env con los datos correctos.\n")
        return False
    return True

API_ID = int(API_ID_RAW) if API_ID_RAW and API_ID_RAW.isdigit() else None
