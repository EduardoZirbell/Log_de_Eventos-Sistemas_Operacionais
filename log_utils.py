import json
import os
import platform
import subprocess

def obter_eventos_log(qtd=100):
    sistema = platform.system()
    if sistema == "Windows":
        # Caminho do executável compilado para Windows (sem subpasta win-x64)
        caminho_exe = os.path.join("LogReaderApp", "bin", "Release", "net9.0", "LogReaderApp.exe")
        if not os.path.exists(caminho_exe):
            raise FileNotFoundError(f"Executável não encontrado: {caminho_exe}")
        resultado = subprocess.run([caminho_exe, str(qtd)], capture_output=True, text=True)
    else:
        # Caminho da DLL para Linux/macOS
        caminho_dll = os.path.join("LogReaderApp", "bin", "Release", "net9.0", "LogReaderApp.dll")
        if not os.path.exists(caminho_dll):
            raise FileNotFoundError(f"Arquivo DLL não encontrado: {caminho_dll}")
        resultado = subprocess.run(['dotnet', caminho_dll, str(qtd)], capture_output=True, text=True)

    if resultado.returncode == 0:
        try:
            eventos = json.loads(resultado.stdout)
            # Mapeamento dos campos do JSON para inglês, conforme esperado pela interface
            eventos_corrigidos = []
            for evt in eventos:
                eventos_corrigidos.append({
                    "Source": evt.get("Fonte", ""),
                    "DateTime": evt.get("DataHora", ""),
                    "Id": evt.get("Identificador", ""),
                    "Type": evt.get("Tipo", ""),
                    "Message": evt.get("Mensagem", "")
                })
            return eventos_corrigidos
        except Exception as e:
            print("Erro ao fazer parse do JSON:", e)
            return []
    else:
        print("Erro ao executar LogReader:", resultado.stderr)
        return []