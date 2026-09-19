Set WshShell = CreateObject("WScript.Shell")
' Ejecuta el bot de Python en segundo plano (modo oculto 0)
WshShell.Run "python main.py", 0, False
