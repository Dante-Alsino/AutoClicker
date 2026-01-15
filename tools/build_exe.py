import os
import subprocess
import sys
import customtkinter

def build():
    # 1. Localiza o caminho do CustomTkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    print(f"CustomTkinter encontrado em: {ctk_path}")
    
    # 2. Define o separador correto para o sistema operacional (--add-data)
    # Windows usa ';', Linux/Mac usa ':'
    sep = ';' if os.name == 'nt' else ':'
    
    # 3. Constrói o argumento --add-data
    add_data_arg = f"{ctk_path}{sep}customtkinter/"
    
    # 4. Define o comando
    # --noconsole: não abre janela preta do cmd
    # --onefile: cria um único .exe
    # --name: nome do arquivo final
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name", "AutoClicker",
        "--add-data", add_data_arg,
        "main.py"
    ]
    
    print("Iniciando Build...")
    print(f"Comando: {' '.join(cmd)}")
    
    # 5. Executa
    try:
        subprocess.check_call(cmd)
        print("\n\nBuild concluído com sucesso!")
        print("Seu executável está na pasta 'dist/'.")
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante o build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Garante que estamos na raiz do projeto (onde está main.py)
    # Se o script for rodado de dentro de 'tools/', sobe um nível
    if not os.path.exists("main.py") and os.path.exists("../main.py"):
        os.chdir("..")
        
    if not os.path.exists("main.py"):
        print("Erro: Não foi possível encontrar main.py. Execute este script da raiz do projeto.")
        sys.exit(1)
        
    build()
