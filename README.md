# Modular AutoClicker

Um automatizador de cliques modular e moderno, desenvolvido em Python. Permite criar sequências de cliques, digitação de texto, definir delays, repetir ações em loop e salvar suas configurações para uso posterior.

## 🚀 Novidades da Versão Atual
*   **Pausa Inteligente (Tecla F8)**: Pause e retome a automação a qualquer momento.
*   **Editor Rápido**: Dê duplo clique num passo para editar suas configurações.
*   **Reordenação**: Botões de subir/descer para organizar sua lista facilmente.
*   **Visual Moderno**: Tema Escuro/Claro (Dark/Light) e feedback visual (bordas coloridas) quando pausado.
*   **Validações**: Proteção contra coordenadas fora da tela e arquivos vazios.

---

## 🛠 Como Usar

### Pré-requisitos
- Python 3.10 ou superior instalado.
- Dependências instaladas (`pip install -r requirements.txt`).

### Executando
No terminal, execute:
```bash
python main.py
```

---

## 📖 Manual de Instruções

### 1. Adicionando Passos
*   **Manual**: Digite as coordenadas X e Y e o tempo de Delay (espera após o clique).
*   **Captura (Recomendado)**:
    1.  Clique em **`Capturar (3s)`**.
    2.  Posicione o mouse no local desejado e espere 3 segundos.
    3.  As coordenadas serão preenchidas automaticamente.
*   **Tipos de Ação**:
    *   **Clique Esquerdo / Direito**: Clica com o mouse.
    *   **Digitar Texto**: Digita uma frase ou conteúdo de um arquivo `.txt` linha por linha.

### 2. Gerenciando a Lista
*   **Editar**: Dê **Duplo Clique** no texto do passo na lista para alterar valores.
*   **Reordenar**: Use as setas **↑** e **↓** para mudar a ordem dos passos.
*   **Remover**: Clique no **`X`** vermelho para apagar.
*   **Marcadores**: Ative `Marcadores` para ver pontos na tela. Você pode arrastá-los para ajustar a posição fina.

### 3. Fila de Execução e Controle
*   **Loops**: Defina quantas vezes repetir ou marque `Loop Infinito`.
*   **Confirmar Loops**: Se marcado, o programa pausa e pede confirmação entre cada repetição.
*   **Iniciar**: Clique em **`Executar Sequência`**.
*   **PAUSAR (F8)**: Pressione **F8** para pausar. A borda ficará LARANJA. Pressione F8 novamente para retomar.
*   **PARAR (F9)**: Pressione **F9** para abortar a execução imediatamente.

### 4. Arquivos
*   **Salvar JSON**: Salve sua rotina para usar depois.
*   **Carregar JSON**: Carregue uma rotina salva.
*   **Carregar Dados (.txt)**: Carregue uma lista de textos para usar na ação "Digitar Texto" (opção 'Usar Arq.').

## 📂 Estrutura do Projeto
*   `main.py`: Ponto de entrada.
*   `src/`: Código fonte modular (`gui.py`, `automation.py`, `widgets.py`, `constants.py`).
*   `json/`: Pasta sugerida para salvar suas rotinas.
*   `logs/`: Logs de execução para depuração.
