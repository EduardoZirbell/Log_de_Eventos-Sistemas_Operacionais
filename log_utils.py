import subprocess
import json
import os
import platform

def obter_eventos_log(qtd=100):
    sistema = platform.system()
    if sistema == "Windows":
        # Monta o caminho do executável do leitor de logs para Windows
        caminho_exe = os.path.join("LogReaderApp", "bin", "Release", "net8.0", "LogReaderApp.exe")
        # Verifica se o executável existe
        if not os.path.exists(caminho_exe):
            raise FileNotFoundError(f"Executável não encontrado: {caminho_exe}")
        # Executa o programa e captura a saída
        resultado = subprocess.run([caminho_exe, str(qtd)], capture_output=True, text=True)
    else:
        # Monta o caminho da DLL para Linux/macOS
        caminho_dll = os.path.join("LogReaderApp", "bin", "Release", "net8.0", "LogReaderApp.dll")
        # Verifica se a DLL existe
        if not os.path.exists(caminho_dll):
            raise FileNotFoundError(f"Arquivo DLL não encontrado: {caminho_dll}")
        # Executa usando dotnet e captura a saída
        resultado = subprocess.run(['dotnet', caminho_dll, str(qtd)], capture_output=True, text=True)
    # Se a execução foi bem-sucedida, retorna a lista de eventos convertida de JSON
    if resultado.returncode == 0:
        return json.loads(resultado.stdout)
    else:
        # Em caso de erro, exibe a mensagem e retorna lista vazia
        print("Erro ao executar LogReader:", resultado.stderr)
        return []