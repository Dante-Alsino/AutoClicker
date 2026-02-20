import time
import pyautogui
import dataclasses
import json
import logging
import os
from typing import List, Literal, Optional
try:
    from .constants import MOUSE_DURATION, KEY_DELAY, ACTION_DELAY
except ImportError:
    # Fallback caso não consiga importar (embora o try global no main deva resolver)
    MOUSE_DURATION = 0.1
    KEY_DELAY = 0.1
    ACTION_DELAY = 0.1

@dataclasses.dataclass
class ClickStep:
    """Representa um único passo de automação."""
    x: int
    y: int
    delay: float  # Tempo de espera APÓS a ação
    button: Literal['left', 'right', 'middle'] = 'left'
    action_type: Literal['click', 'type', 'key'] = 'click'
    text_content: str = ""
    use_data_file: bool = False # Se True, usa linha do arquivo carregado
    clear_field: bool = False # Se True, envia Ctrl+A + Del antes de digitar
    double_click: bool = False # Se True, realiza clique duplo
    scroll_amount: int = 0 # Quantidade de scroll (Positivo=Cima, Negativo=Baixo)
    
    def __str__(self) -> str:
        """Retorna representação string do passo."""
        if self.action_type == 'type':
            src = " (ARQUIVO)" if self.use_data_file else f" '{self.text_content}'"
            clear = " [LIMPAR]" if self.clear_field else ""
            return f"DIGITAR em ({self.x}, {self.y}):{src}{clear} - Delay: {self.delay}s"
        
        if self.action_type == 'scroll':
            direction = "CIMA" if self.scroll_amount > 0 else "BAIXO"
            return f"SCROLL {direction} ({abs(self.scroll_amount)}) em ({self.x}, {self.y}) - Delay: {self.delay}s"
        
        if self.action_type == 'key':
             return f"TECLA '{self.text_content.upper()}' em ({self.x}, {self.y}) - Delay: {self.delay}s"
        
        btn_pt = "ESQUERDO" if self.button == 'left' else "DIREITO" if self.button == 'right' else "MEIO"
        click_type = " (DUPLO)" if self.double_click else ""
        return f"CLIQUE {btn_pt}{click_type} em ({self.x}, {self.y}) - Delay: {self.delay}s"

class AutomationEngine:
    """Gerencia a sequência de passos e a execução."""
    def __init__(self):
        self.steps: List[ClickStep] = []
        self.is_running = False
        self.is_paused = False
        self.logger = logging.getLogger(__name__)
        self.data_lines: List[str] = []
        self.current_loop = 0

    def load_data_file(self, filepath: str) -> int:
        """
        Carrega linhas de dados de um arquivo txt.
        Retorna a quantidade de linhas carregadas.
        Raise Exception se houver erro de leitura.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data_lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if not self.data_lines:
                self.logger.warning("Arquivo de dados carregado mas está vazio.")
            
            self.logger.info(f"Dados carregados: {len(self.data_lines)} linhas.")
            return len(self.data_lines)
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo de dados: {e}")
            raise e


    def add_step(self, x: int, y: int, delay: float, button: str = 'left', action_type: str = 'click', text_content: str = "", use_data_file: bool = False, clear_field: bool = False, double_click: bool = False, scroll_amount: int = 0):
        """Adiciona um novo passo à sequência."""
        step = ClickStep(x, y, delay, button, action_type, text_content, use_data_file, clear_field, double_click, scroll_amount) # type: ignore
        self.steps.append(step)
        self.logger.info(f"Passo adicionado: {step}")
        print(f"Passo adicionado: {step}")

    def clear_steps(self) -> None:
        """Remove todos os passos da sequência atual."""
        self.steps.clear()
        self.logger.info("Sequência limpa.")
        print("Sequência limpa.")

    
    def get_steps(self) -> List[ClickStep]:
        return self.steps

    def remove_step(self, index: int) -> None:
        """
        Remove o passo no índice especificado.
        Registra warning se índice for inválido.
        """
        if 0 <= index < len(self.steps):
            removed = self.steps.pop(index)
            self.logger.info(f"Passo removido: {removed}")
            print(f"Passo removido: {removed}")
        else:
            self.logger.warning(f"Tentativa de remover índice inválido: {index}")
            print(f"Índice inválido para remoção: {index}")

    def swap_steps(self, index1: int, index2: int) -> None:
        """Troca dois passos de posição (para reordenação)."""
        if 0 <= index1 < len(self.steps) and 0 <= index2 < len(self.steps):
            self.steps[index1], self.steps[index2] = self.steps[index2], self.steps[index1]
            self.logger.info(f"Passos trocados: {index1} <-> {index2}")

    def update_step(self, index: int, new_step: ClickStep) -> None:
        """Atualiza um passo existente."""
        if 0 <= index < len(self.steps):
            self.steps[index] = new_step
            self.logger.info(f"Passo {index} atualizado: {new_step}")

    def toggle_pause(self):
        """Alterna entre pausado e rodando."""
        self.is_paused = not self.is_paused
        state = "PAUSADO" if self.is_paused else "RETOMANDO"
        self.logger.info(f"Estado alterado para: {state}")
        print(f"--- {state} ---")




    def _execute_click(self, step: ClickStep):
        """Executa a ação de clique do passo."""
        btn = step.button if step.action_type == 'click' else 'left'
        self.logger.info(f"Executando ação no ponto ({step.x}, {step.y}) com botão: {btn.upper()}")
        
        # Garante movimento antes do clique
        pyautogui.moveTo(step.x, step.y)
        
        # Pequeno delay para garantir que o mouse "assentou"
        time.sleep(ACTION_DELAY)
        
        if step.double_click and step.action_type == 'click':
                self.logger.info("Realizando clique duplo.")
                pyautogui.doubleClick(button=btn) 
        else:
            # Usa duration para segurar o clique por alguns milissegundos
            if btn == 'right':
                pyautogui.rightClick(duration=MOUSE_DURATION)
            elif btn == 'middle':
                pyautogui.middleClick(duration=MOUSE_DURATION)
            else:
                pyautogui.click(duration=MOUSE_DURATION)

    def _execute_type(self, step: ClickStep, text_to_type: str):
        """Executa a ação de digitar texto."""
        # Limpar campo antes de digitar?
        time.sleep(ACTION_DELAY)
        if step.clear_field:
            self.logger.info("Limpando campo (Ctrl+A + Del)...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(ACTION_DELAY)
            pyautogui.press('del')
            time.sleep(ACTION_DELAY)

        if text_to_type:
            time.sleep(ACTION_DELAY) # Delay antes de digitar
            pyautogui.write(text_to_type, interval=KEY_DELAY) 

    def _execute_key(self, step: ClickStep):
        """Executa a ação de pressionar uma tecla ou atalho."""
        keys_str = step.text_content.lower()
        self.logger.info(f"Pressionando tecla(s): {keys_str}")
        
        # Garante foco com clique
        pyautogui.click(step.x, step.y)
        time.sleep(ACTION_DELAY)
        
        # Se houver '+', trata como combinação (hotkey)
        if '+' in keys_str:
            keys = keys_str.split('+')
            # Remove espaços em branco que possam existir (ex: ctrl + c)
            keys = [k.strip() for k in keys]
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(keys_str)

    def _execute_scroll(self, step: ClickStep):
        """Executa a ação de scroll."""
        self.logger.info(f"Executando scroll de {step.scroll_amount} em ({step.x}, {step.y})")
        
        # Garante movimento para a área de scroll
        pyautogui.moveTo(step.x, step.y)
        time.sleep(ACTION_DELAY)
        
        # Executa o scroll
        pyautogui.scroll(step.scroll_amount)

    def execute_sequence(self, loops: int = 1, infinite: bool = False, on_step_callback=None, confirm_between_loops: bool = False, confirm_callback=None):
        """
        Executa a lista de passos.
        :param confirm_between_loops: Se True, pede confirmação antes do próximo loop.
        :param confirm_callback: Função que retorna Bool (True=Continua, False=Para).
        """
        if not self.steps:
            self.logger.warning("Tentativa de executar lista vazia.")
            print("Nenhum passo para executar.")
            return

        loop_type = 'Infinito' if infinite else loops
        self.logger.info(f"Iniciando execução. Loops: {loop_type}, Total Passos: {len(self.steps)}")
        print(f"Iniciando execução. Loops: {loop_type}")
        
        self.is_running = True
        
        self.current_loop = 0
        
        try:
            while self.is_running:
                if not infinite and self.current_loop >= loops:
                    break
                
                # Pausa
                while self.is_paused and self.is_running:
                     time.sleep(0.1)
                     if on_step_callback:
                         on_step_callback(-2) # -2 = Código para status PAUSADO (simbolico)

                # Confirmação entre loops (exceto o primeiro)
                if self.current_loop > 0 and confirm_between_loops and confirm_callback:
                    if on_step_callback: on_step_callback(-3) # -3 = WAITING/CONFIRM
                    self.logger.info("Aguardando confirmação do usuário para próximo loop...")
                    should_continue = confirm_callback(self.current_loop + 1)
                    if not should_continue:
                        self.logger.info("Usuário cancelou no diálogo de confirmação.")
                        break

                self.current_loop += 1
                print(f"--- Loop {self.current_loop} ---")
                self.logger.info(f"Iniciando Loop {self.current_loop}")

                for i, step in enumerate(self.steps):
                    if not self.is_running:
                        self.logger.info("Execução interrompida pelo usuário (loop interno).")
                        break
                    
                    # Checagem de pausa dentro do loop de passos
                    while self.is_paused and self.is_running:
                        time.sleep(0.1)
                        if on_step_callback: on_step_callback(-2)

                    
                    # Notifica a interface sobre o passo atual
                    if on_step_callback:
                        on_step_callback(i)
                    
                    # Resolve texto a ser digitado (Fixo ou do Arquivo)
                    text_to_type = step.text_content
                    if step.action_type == 'type' and step.use_data_file:
                        if self.data_lines:
                            # Usa índice do loop (0-based) mod len(lines) para ciclar se acabar
                            data_idx = (self.current_loop - 1) % len(self.data_lines)
                            text_to_type = self.data_lines[data_idx]
                            self.logger.info(f"Usando dados da linha {data_idx+1}: '{text_to_type}'")
                        else:
                            self.logger.warning("Passo configurado para usar arquivo, mas lista de dados está vazia!")
                            text_to_type = "SEM DADOS"

                    print(f"Executando passo {i+1}: {step}")
                    
                    # Move e Clica
                    print(f"Executando passo {i+1}: {step}")
                    
                    try:
                        # Verifica e executa clique/movimento
                        self._execute_click(step)
                        
                        # Se for ação de digitar, chama o método específico
                        if step.action_type == 'type':
                             self._execute_type(step, text_to_type)
                        
                        if step.action_type == 'key':
                             self._execute_key(step)

                        if step.action_type == 'scroll':
                             self._execute_scroll(step)
                            
                    except Exception as e:
                        self.logger.error(f"Erro ao executar ação PyAutoGUI no passo {i+1}: {e}")
                        raise e
                    
                    # Aguarda o delay definido
                    time.sleep(step.delay)
            
            # Limpa destaque ao final
            if on_step_callback:
                on_step_callback(-1)
                
        except Exception as e:
            self.logger.error(f"Erro crítico durante a execução: {e}", exc_info=True)
            print(f"Erro durante a execução: {e}")
            if on_step_callback: on_step_callback(-1)
        finally:
            self.is_running = False
            self.logger.info("Execução finalizada.")
            print("Execução finalizada.")

    def stop(self) -> None:
        """
        Sinaliza para parar a execução.
        A engine irá parar no início do próximo passo ou loop.
        """
        self.is_running = False
        self.logger.info("Sinal de parada recebido.")
        print("Parando execução...")


    def save_to_file(self, filepath: str):
        """Salva a sequência atual em um arquivo JSON."""
        data = [dataclasses.asdict(step) for step in self.steps]
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            self.logger.info(f"Sequência salva em {filepath}")
            print(f"Sequência salva em {filepath}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar arquivo: {e}")
            raise e

    def load_from_file(self, filepath: str):
        """Carrega uma sequência de um arquivo JSON."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.steps.clear()
            for item in data:
                # Garante que os tipos estão corretos ao carregar
                # Compatibilidade com versões antigas (sem action_type)
                action = item.get('action_type', 'click')
                text = item.get('text_content', '')
                use_file = item.get('use_data_file', False) # Default False para retrocompatibilidade
                clear = item.get('clear_field', False)
                double = item.get('double_click', False)
                
                self.add_step(
                    x=int(item['x']),
                    y=int(item['y']),
                    delay=float(item['delay']),
                    button=str(item['button']),
                    action_type=str(action),
                    text_content=str(text),
                    use_data_file=bool(use_file),
                    clear_field=bool(clear),
                    double_click=bool(double),
                    scroll_amount=int(item.get('scroll_amount', 0))
                )
            self.logger.info(f"Sequência carregada de {filepath}")
            print(f"Sequência carregada de {filepath}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo: {e}")
            raise e
