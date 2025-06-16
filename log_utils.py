import subprocess
import json
import os

def get_log_events(qtd=100):
    exe = os.path.join("LogReaderApp", "bin", "Release", "net9.0", "LogReaderApp.exe")
    if not os.path.exists(exe):
        raise FileNotFoundError(f"Executável não encontrado: {exe}")
    result = subprocess.run([exe, str(qtd)], capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print("Erro ao executar LogReader:", result.stderr)
        return []