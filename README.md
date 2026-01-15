# Modular AutoClicker

Um automatizador de cliques modular e moderno, desenvolvido em Python. Permite criar sequências de cliques, digitação de texto, definir delays, repetir ações em loop e salvar suas configurações para uso posterior.

## 🚀 Novidades da Versão Atual
*   **Scroll do Mouse**: Adicione passos de rolagem (cima/baixo) para navegar em páginas e formulários.
*   **Duplo Clique**: Suporte nativo para cliques duplos em ações do mouse.
*   **Janela de Ajuda**: Manual completo integrado ao botão "Como funciona".
*   **Pausa Inteligente (Tecla F8)**: Pause e retome a automação a qualquer momento.
*   **Editor Rápido**: Dê duplo clique num passo para editar suas configurações.
*   **Reordenação**: Botões compactos (▲/▼) para organizar sua lista facilmente.
*   **Refatoração Técnica**: Código modularizado (GUI, Engine, Widgets) para maior estabilidade e facilidade de manutenção.
*   **Visual Moderno**: Tema Escuro/Claro (Dark/Light) e feedback visual (bordas coloridas) quando pausado.
*   **Validações**: Proteção contra coordenadas fora da tela e arquivos vazios.

---

## 💾 Instalação e Execução

Você pode usar o AutoClicker de duas formas:

### Opção 1: Executável (Recomendado para Usuários)
Não requer instalação de Python.
1. Baixe o arquivo `AutoClicker.exe` (gerado na pasta `dist/` após o build ou disponível nas Releases).
2. Dê dois cliques para abrir.
3. Pronto!

### Opção 2: Código Fonte (Para Desenvolvedores)
Requer Python 3.10+ instalado.

1. Clone o repositório ou baixe o código.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```bash
   python main.py
   ```

### Opção 3: Criando seu próprio Executável
Se você baixou o código fonte e quer gerar o arquivo `.exe`:
1. Certifique-se de ter instalado as dependências (`pip install -r requirements.txt`).
2. Rode o script de build:
   ```bash
   python tools/build_exe.py
   ```
3. O executável será criado na pasta `dist/`.

---

## 📂 Estrutura do Projeto

*   `main.py`: Ponto de entrada da aplicação.
*   `src/`: Código fonte modular.
    *   `gui.py`: Interface Gráfica (construída com CustomTkinter).
    *   `automation.py`: Motor de automação (lógica de cliques, teclado e scroll).
    *   `widgets.py`: Componentes visuais personalizados (ex: Marcadores).
    *   `constants.py`: Configurações globais (Cores, Tempos, Tamanhos).
*   `tools/`: Ferramentas utilitárias.
    *   `build_exe.py`: Script para gerar o executável automaticamente.
*   `json/`: Pasta sugerida para salvar suas rotinas.
*   `logs/`: Logs de execução para depuração.

---

## 📖 Manual de Instruções

### 1. Adicionando Passos
*   **Manual**: Digite as coordenadas X e Y e o tempo de Delay (espera após a ação).
*   **Captura (Recomendado)**:
    1.  Clique em **`Capturar (3s)`**.
    2.  Posicione o mouse no local desejado e espere 3 segundos.
    3.  As coordenadas serão preenchidas automaticamente.
*   **Tipos de Ação**:
    *   **Clique Esquerdo / Direito**: Clica com o mouse. (Opção **Duplo Clique** disponível).
    *   **Digitar Texto**: Digita uma frase ou conteúdo de um arquivo `.txt` linha por linha.
    *   **Pressionar Enter**: Move, clica para focar e pressiona a tecla `Enter`.
    *   **Scroll**: Realiza rolagem da página na posição alvo. (Positivo = Cima, Negativo = Baixo).

### 2. Gerenciando a Lista
*   **Editar**: Dê **Duplo Clique** no texto do passo na lista para alterar valores (Posição, Delay, Scroll, etc).
*   **Reordenar**: Use as setas **▲** e **▼** para mudar a ordem dos passos.
*   **Remover**: Clique no **`X`** vermelho para apagar.
*   **Marcadores**: Ative `Marcadores` para ver pontos visuais na tela. Você pode arrastá-los com o mouse para ajustar a posição fina.

### 3. Fila de Execução e Controle
*   **Loops**: Defina quantas vezes repetir a sequência ou marque `Loop Infinito`.
*   **Confirmar Loops**: Se marcado, o programa pausa e pede confirmação do usuário entre cada repetição.
*   **Iniciar**: Clique em **`Executar Sequência`**.
*   **PAUSAR (F8)**: Pressione **F8** para pausar. A borda da janela ficará LARANJA. Pressione F8 novamente para retomar.
*   **PARAR (F9)**: Pressione **F9** para abortar a execução imediatamente (Emergência).

### 4. Arquivos e Dados
*   **Salvar JSON**: Salve sua rotina atual para usar depois.
*   **Carregar JSON**: Carregue uma rotina salva anteriormente.
*   **Carregar Dados (.txt)**: Carregue uma lista de textos para usar na ação "Digitar Texto" (selecione a opção 'Usar Arq.').
