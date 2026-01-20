# AutoClicker

Um automatizador eficiente para Windows, desenvolvido em Python. Automatize cliques, digitação, atalhos de teclado e scrolls com facilidade.

![GitHub release (latest by date)](https://img.shields.io/github/v/release/Dante-Alsino/AutoClicker?style=flat-square)
![GitHub license](https://img.shields.io/github/license/Dante-Alsino/AutoClicker?style=flat-square)

## 🚀 Novidades da Versão 1.0.0
*   **Instalador Profissional**: Setup simples que configura tudo para você.
*   **Captura de Atalhos**: Grave e reproduza atalhos de teclado (ex: `Ctrl+C`, `Alt+Tab`) de forma nativa.
*   **Identidade Visual**: Novo ícone moderno e Splash Screen de carregamento.
*   **Logs Otimizados**: Sistema de logs salvo corretamente em `%APPDATA%`, sem erros de permissão.
*   **Pausa Inteligente (F8)**: Pause e retome a automação a qualquer momento com feedback visual.
*   **Editor Completo**: Edite passos, reordene a lista e use marcadores visuais na tela.

---

## 💾 Download e Instalação

### Usuário Final (Recomendado)
Vá até a aba **[Releases](https://github.com/Dante-Alsino/AutoClicker/releases)** e baixe o arquivo:
*   📦 **`AutoClickerSetup.exe`**: Instala o programa, cria atalhos na Área de Trabalho e Menu Iniciar.

### Versão Portátil
*   🚀 **`AutoClicker.exe`**: Execute diretamente sem instalar (ideal para pen drives).

---

## 🛠️ Para Desenvolvedores (Código Fonte)

Requer Python 3.10+ instalado.

1. Clone o repositório:
   ```bash
   git clone https://github.com/Dante-Alsino/AutoClicker.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```bash
   python main.py
   ```
4. Gerar executável e instalador:
   ```bash
   python build.py      # Gera o .exe em dist/ e Output/
   # Para o instalador, compile o arquivo 'setup.iss' com o Inno Setup Compiler.
   ```

---

## 📖 Como Usar

### 1. Adicionando Ações
*   **Captura de Mouse**: Clique em `Capturar (3s)`, posicione o mouse e espere.
*   **Captura de Teclado**: Selecione `Atalho de Teclado`, clique em `Capturar` e pressione a combinação (ex: `Ctrl+Shift+Del`).
*   **Texto e Digitação**: O robô pode digitar textos fixos ou ler linha-por-linha de um arquivo `.txt` externo.

### 2. Controles
*   **Executar**: Inicia a sequência.
*   **F8**: Pausa/Retoma a execução.
*   **F9**: Parada de Emergência (Stop).

---

## 🤝 Contribuindo
Sinta-se livre para abrir **Issues** ou enviar **Pull Requests**. Consulte o [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## 📄 Licença
Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
