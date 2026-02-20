import customtkinter as ctk
import pyautogui
import time
import threading
import keyboard
import logging
from logging.handlers import RotatingFileHandler
import os
import tkinter.messagebox as messagebox
import sys
from tkinter import filedialog

try:
    from .automation import AutomationEngine, ClickStep
    from .widgets import DraggableMarker, ProgressOverlay
    from .constants import *
except ImportError:
    if __name__ == "__main__":
        print("ERRO: Este arquivo não deve ser executado diretamente.")
        print("Por favor, execute o arquivo 'main.py' na raiz do projeto.")
        print("Comando: python main.py")
        sys.exit(1)
    raise


import queue

# Configuração de Logging
app_data = os.getenv('APPDATA')
log_dir = os.path.join(app_data, "AutoClicker", "logs")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(os.path.join(log_dir, "app.log"), maxBytes=1_000_000, backupCount=3, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")



class AutoClickerApp(ctk.CTk):
    """
    Janela Principal da aplicação AutoClicker.
    Gerencia a interface gráfica e a interação com o usuário.
    """
    def __init__(self):
        super().__init__()

        self.title("AutoClicker")
        self.geometry(WINDOW_SIZE)
        
        # Close Splash Screen if exists
        try:
            import pyi_splash
            pyi_splash.close()
        except ImportError:
            pass

        # Set Icon
        try:
            from PIL import Image, ImageTk
            icon_path = os.path.join("assets", "logo.png")
            if os.path.exists(icon_path):
                # self.iconbitmap(icon_path) # Requires .ico
                # Use iconphoto for PNG support
                 img = Image.open(icon_path)
                 self.iconphoto(False, ImageTk.PhotoImage(img))
        except Exception as e:
            print(f"Erro ao carregar icone: {e}")
        
        self.engine = AutomationEngine()
        self.markers = []
        self.markers_visible = False
        self.osd_overlay = None
        self.appearance_mode = "Dark" # Estado atual do tema
        self.ignore_bounds_warning = False # Supressão de alerta de coordenadas suspeitas
        
        # Filas para thread safety
        self.confirm_request_queue = queue.Queue()
        self.confirm_response_queue = queue.Queue()
        self.bind("<<ConfirmationRequest>>", self._handle_confirmation_request)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._init_ui()
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        try:
            keyboard.add_hotkey('F9', self.stop_execution)
            keyboard.add_hotkey('F8', self.toggle_pause) 
        except ImportError:
            print("Biblioteca keyboard não encontrada ou sem permissão.")

    def _init_ui(self):
        # Frame de Configuração (Inputs)
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self._build_input_area()
        self._build_action_buttons()
        self._build_file_operations()
        
        # Lista e Controles
        self._build_list_area()
        self._build_controls()
        self._build_status_footer()

    def _build_input_area(self):
        # Inputs HBox
        self.input_box = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.input_box.pack(pady=5, padx=5, fill="x")

        # X
        self.lbl_x = ctk.CTkLabel(self.input_box, text="X:")
        self.lbl_x.pack(side="left", padx=5)
        self.entry_x = ctk.CTkEntry(self.input_box, width=60)
        self.entry_x.pack(side="left", padx=5)
        
        # Y
        self.lbl_y = ctk.CTkLabel(self.input_box, text="Y:")
        self.lbl_y.pack(side="left", padx=5)
        self.entry_y = ctk.CTkEntry(self.input_box, width=60)
        self.entry_y.pack(side="left", padx=5)
        
        # Delay
        self.lbl_delay = ctk.CTkLabel(self.input_box, text="Delay (s):")
        self.lbl_delay.pack(side="left", padx=5)
        self.entry_delay = ctk.CTkEntry(self.input_box, width=60)
        self.entry_delay.insert(0, "1.0")
        self.entry_delay.pack(side="left", padx=5)
        
        # Ação (Tipo)
        self.lbl_btn = ctk.CTkLabel(self.input_box, text="Ação:")
        self.lbl_btn.pack(side="left", padx=5)
        self.opt_action = ctk.CTkOptionMenu(
            self.input_box, 
        values=["Clique Esquerdo", "Clique Direito", "Digitar Texto", "Pressionar Enter", "Atalho de Teclado", "Scroll"],
            command=self.on_action_change,
            width=120
        )
        self.opt_action.pack(side="left", padx=5)
        
        # Checkbox Duplo Clique
        self.chk_double_click = ctk.CTkCheckBox(self.input_box, text="Duplo Clique", width=60)
        self.chk_double_click.pack(side="left", padx=5)

        # Campo de Texto
        self.entry_text = ctk.CTkEntry(self.input_box, placeholder_text="Texto...", width=120)
        
        # Checkboxes para Texto
        self.text_opts_frame = ctk.CTkFrame(self.input_box, fg_color="transparent")
        
        self.chk_use_file = ctk.CTkCheckBox(self.text_opts_frame, text="Usar Arq.", width=60)
        self.chk_use_file.pack(side="left", padx=2)
        
        self.chk_clear_field = ctk.CTkCheckBox(self.text_opts_frame, text="Limpar", width=60)
        self.chk_clear_field.pack(side="left", padx=2)

        # Scroll Input (Inicialmente oculto)
        self.scroll_frame = ctk.CTkFrame(self.input_box, fg_color="transparent")
        self.lbl_scroll = ctk.CTkLabel(self.scroll_frame, text="Qtd:")
        self.lbl_scroll.pack(side="left", padx=2)
        self.entry_scroll = ctk.CTkEntry(self.scroll_frame, width=60)
        self.entry_scroll.insert(0, "500")
        self.entry_scroll.pack(side="left", padx=2)
        
        self.scroll_dir_var = ctk.StringVar(value="baixo")
        self.rad_scroll_up = ctk.CTkRadioButton(self.scroll_frame, text="Cima", variable=self.scroll_dir_var, value="cima", width=50)
        self.rad_scroll_up.pack(side="left", padx=5)
        self.rad_scroll_down = ctk.CTkRadioButton(self.scroll_frame, text="Baixo", variable=self.scroll_dir_var, value="baixo", width=50)
        self.rad_scroll_down.pack(side="left", padx=5)

        # Key Capture (Inicialmente oculto)
        self.key_frame = ctk.CTkFrame(self.input_box, fg_color="transparent")
        
        self.btn_capture_key = ctk.CTkButton(self.key_frame, text="Capturar Tecla", command=self.start_key_capture_thread, width=100, fg_color=COLOR_CAPTURE)
        self.btn_capture_key.pack(side="left", padx=2)
        
        self.entry_key = ctk.CTkEntry(self.key_frame, width=100, placeholder_text="Aguardando...")
        self.entry_key.pack(side="left", padx=2)

    def _build_action_buttons(self):
        # Actions Box
        self.action_box = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.action_box.pack(pady=5, padx=5, fill="x")

        self.btn_capture = ctk.CTkButton(self.action_box, text="Capturar (3s)", command=self.start_capture_thread, fg_color=COLOR_CAPTURE)
        self.btn_capture.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_add = ctk.CTkButton(self.action_box, text="Adicionar Passo", command=self.add_step)
        self.btn_add.pack(side="left", padx=5, expand=True, fill="x")

    def _build_file_operations(self):
        # Data & File Box
        self.file_box = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.file_box.pack(pady=5, padx=5, fill="x")
        
        self.btn_load_data = ctk.CTkButton(self.file_box, text="Carregar Dados (.txt)", command=self.load_data, fg_color=COLOR_LOAD, width=120)
        self.btn_load_data.pack(side="left", padx=5)
        
        self.lbl_data_info = ctk.CTkLabel(self.file_box, text="Dados: 0 linhas", text_color="gray")
        self.lbl_data_info.pack(side="left", padx=5)

        # File Operations
        self.op_box = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.op_box.pack(pady=5, padx=5, fill="x")

        self.btn_save = ctk.CTkButton(self.op_box, text="Salvar JSON", command=self.save_sequence, fg_color=COLOR_SUCCESS, width=80)
        self.btn_save.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_load = ctk.CTkButton(self.op_box, text="Carregar JSON", command=self.load_sequence, fg_color=COLOR_INFO, width=80)
        self.btn_load.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_clear = ctk.CTkButton(self.op_box, text="Limpar Lista", command=self.clear_list, fg_color=COLOR_GRAY, width=80)
        self.btn_clear.pack(side="left", padx=5, expand=True, fill="x")

        self.chk_markers = ctk.CTkCheckBox(self.op_box, text="Marcadores", command=self.toggle_markers)
        self.chk_markers.pack(side="right", padx=5)

        self.chk_osd = ctk.CTkCheckBox(self.op_box, text="Monitor Flutuante")
        self.chk_osd.pack(side="right", padx=5)

    def _build_list_area(self):
        # Lista de Passos
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Sequência de Passos")
        self.list_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def _build_controls(self):
        # Controles de Execução
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.btn_execute = ctk.CTkButton(self.control_frame, text="Executar Sequência", command=self.start_execution_thread, fg_color=COLOR_SUCCESS)
        self.btn_execute.pack(side="left", padx=5, pady=10, expand=True, fill="x")

        # Opções de Loop
        self.loop_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.loop_frame.pack(side="left", padx=5)

        self.chk_infinite = ctk.CTkCheckBox(self.loop_frame, text="Loop Infinito", command=self.toggle_infinite_loop)
        self.chk_infinite.pack(side="top", pady=2)
        
        self.chk_confirm = ctk.CTkCheckBox(self.loop_frame, text="Confirmar Loops")
        self.chk_confirm.pack(side="top", pady=2)
        
        self.loop_count_frame = ctk.CTkFrame(self.loop_frame, fg_color="transparent")
        self.loop_count_frame.pack(side="top", pady=2)
        
        self.lbl_loops = ctk.CTkLabel(self.loop_count_frame, text="Loops:")
        self.lbl_loops.pack(side="left", padx=2)
        
        self.entry_loops = ctk.CTkEntry(self.loop_count_frame, width=40)
        self.entry_loops.insert(0, "1")
        self.entry_loops.pack(side="left", padx=2)

        self.btn_stop = ctk.CTkButton(self.control_frame, text="PARAR (F9)", command=self.stop_execution, fg_color=COLOR_ERROR)
        self.btn_stop.pack(side="left", padx=5, pady=10, expand=True, fill="x")

    def _build_status_footer(self):
        # Status Bar
        self.lbl_status = ctk.CTkLabel(self, text="Pronto.")
        self.lbl_status.grid(row=3, column=0, sticky="w", padx=10, pady=5)

        # Botão de Tema (Canto Inferior Direito)
        self.btn_theme = ctk.CTkButton(self, text="Tema: Dark", command=self.toggle_theme, width=80, height=24, fg_color=COLOR_GRAY)
        self.btn_theme.grid(row=3, column=0, sticky="e", padx=10, pady=5)
        
        # Botão de Ajuda (Ao lado do tema)
        self.btn_help = ctk.CTkButton(self, text="Como funciona", command=self.show_help_window, width=80, height=24, fg_color=COLOR_INFO)
        self.btn_help.grid(row=3, column=0, sticky="e", padx=100, pady=5)

    def show_help_window(self):
        """Abre janela com instruções."""
        help_window = ctk.CTkToplevel(self)
        help_window.title("Como funciona")
        help_window.geometry("500x400")
        help_window.attributes("-topmost", True)
        
        textbox = ctk.CTkTextbox(help_window, width=480, height=380)
        textbox.pack(padx=10, pady=10)
        
        help_text = """MANUAL DO AUTOCLICKER

1. ADICIONANDO AÇÕES
--------------------
   - Coordenadas (X, Y): Digite manualmente ou use o botão "Capturar (3s)".
   - Capturar: Clique, leve o mouse ao alvo e espere 3 segundos.
    - Ação: Escolha entre Clique (Esq/Dir), Digitar Texto, Pressionar Enter ou Scroll.
    - Duplo Clique: Marque a caixa para realizar dois cliques rápidos.
    - Scroll: Defina a quantidade (ex: 100). Positivo sobe, negativo desce.
    - Pressionar Enter: Move o mouse, clica e pressiona Enter.
    - Adicionar: Clique em "Adicionar Passo" para inserir na lista.

2. GERENCIANDO A LISTA
----------------------
   - Reordenar: Use as setas (▲/▼) para mover passos para cima ou baixo.
   - Editar: Dê DUPLO CLIQUE em qualquer item da lista para alterar valores.
   - Excluir: Clique no botão (X) vermelho.
   - Marcadores: Ative a caixa "Marcadores" para ver pontos visuais na tela.

3. DIGITAÇÃO DE TEXTO
---------------------
   - Texto Simples: Digite o texto no campo e adicione o passo.
   - Usar Arquivo (.txt): Marque "Usar Arq." e carregue um arquivo .txt.
     Cada vez que o passo rodar, ele pegará a próxima linha do arquivo.
   - Limpar Campo: Marque "Limpar" para apagar o conteúdo atual antes de digitar (Ctrl+A + Del).

4. EXECUÇÃO E CONTROLE
----------------------
   - Iniciar: Clique em "Executar Sequência".
   - PAUSAR (F8): Pressione F8 para pausar. A borda fica Laranja.
   - RETOMAR (F8): Pressione F8 novamente para continuar.
   - PARAR (F9): Pressione F9 para abortar imediatamente (Emergência).
   - Loops: Defina a quantidade ou marque "Loop Infinito".
   - Confirmar: Se marcado, pede permissão para iniciar cada novo loop.

5. OUTROS
---------
   - Salvar/Carregar: Salve suas rotinas em JSON para não perder trabalho.
   - Tema: Alterne entre modo Claro e Escuro no botão inferior.
"""
        textbox.insert("0.0", help_text)
        textbox.configure(state="disabled")



    def on_action_change(self, choice):
        # Esconde/Mostra baseado na escolha
        self.entry_text.pack_forget()
        self.text_opts_frame.pack_forget()
        self.chk_double_click.pack_forget()
        self.scroll_frame.pack_forget()
        self.key_frame.pack_forget()

        if choice == "Digitar Texto":
            self.entry_text.pack(side="left", padx=5)
            self.text_opts_frame.pack(side="left", padx=5)
        elif choice == "Pressionar Enter":
            pass # Nada extra
        elif choice == "Scroll":
            self.scroll_frame.pack(side="left", padx=5)
        elif choice == "Atalho de Teclado":
            self.key_frame.pack(side="left", padx=5)
        else:
            self.chk_double_click.pack(side="left", padx=5)

    def load_data(self):
        """Carrega arquivo de dados para digitação linha a linha."""
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            try:
                # Verificação de arquivo vazio antes de carregar
                if os.path.getsize(filepath) == 0:
                    self.lbl_status.configure(text=f"Erro: Arquivo vazio!", text_color=COLOR_WARNING)
                    messagebox.showwarning("Arquivo Vazio", "O arquivo selecionado não contém dados.")
                    return

                count = self.engine.load_data_file(filepath)
                self.lbl_data_info.configure(text=f"Dados: {count} linhas")
                self.lbl_status.configure(text=f"Dados carregados: {filepath.split('/')[-1]}")
            except Exception as e:
                self.lbl_status.configure(text=f"Erro ao carregar dados: {e}", text_color=COLOR_ERROR)

    def toggle_infinite_loop(self):
        if self.chk_infinite.get():
            self.entry_loops.configure(state="disabled")
        else:
            self.entry_loops.configure(state="normal")
    
    def toggle_theme(self):
        if self.appearance_mode == "Dark":
            ctk.set_appearance_mode("Light")
            self.appearance_mode = "Light"
            self.btn_theme.configure(text="Tema: Light")
        else:
            ctk.set_appearance_mode("Dark")
            self.appearance_mode = "Dark"
            self.btn_theme.configure(text="Tema: Dark")

    def toggle_pause(self):
        if self.engine.is_running:
            self.engine.toggle_pause()
            # Atualização visual será feita via callback
    
    def _update_state_visuals(self, status_code: int):
        """Atualiza visual da janela baseado no estado (Pausa/Wait)."""
        if status_code == -2: # PAUSED
            self.configure(fg_color=COLOR_PAUSED)
            self.lbl_status.configure(text="PAUSADO (Pressione F8 para continuar)", text_color="black")
        elif status_code == -3: # WAITING
            self.configure(fg_color=COLOR_WAITING)
        else: # NORMAL (Reseta para cor do tema)
            # Hack para resetar cor de fundo do CTK (usando None ou re-setando mode as vezes não limpa borders)
            # Vamos apenas resetar para o padrão cinza escuro/claro do CTK se possível, mas CTK não expõe fácil
            # Alternativa: setar para transparent ou cor padrão manual
            bg = "gray10" if self.appearance_mode == "Dark" else "gray90"
            self.configure(fg_color=bg)

    def move_step_up(self, index):
        if index > 0:
            self.engine.swap_steps(index, index - 1)
            self._refresh_list()
            self.highlight_step(index - 1) # Mantém foco visual

    def move_step_down(self, index):
        if index < len(self.engine.steps) - 1:
            self.engine.swap_steps(index, index + 1)
            self._refresh_list()
            self.highlight_step(index + 1)

    def edit_step(self, index):
        """Abre dialogo simples para editar passo."""
        step = self.engine.steps[index]
        
        # Cria Janela TopLevel
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar Passo {index+1}")
        dialog.geometry("300x250")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="X:").pack(pady=5)
        entry_x = ctk.CTkEntry(dialog)
        entry_x.insert(0, str(step.x))
        entry_x.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Y:").pack(pady=5)
        entry_y = ctk.CTkEntry(dialog)
        entry_y.insert(0, str(step.y))
        entry_y.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Delay (s):").pack(pady=5)
        entry_delay = ctk.CTkEntry(dialog)
        entry_delay.insert(0, str(step.delay))
        entry_delay.pack(pady=5)
        
        chk_double = ctk.CTkCheckBox(dialog, text="Duplo Clique")
        if step.double_click: 
            chk_double.select()
        
        # Só mostra checkbox de duplo clique se for ação de clique
        if step.action_type == 'click':
            chk_double.pack(pady=5)
        
        # Opção de scroll no editor
        if step.action_type == 'scroll':
            scroll_dir_edit_var = ctk.StringVar(value="cima" if step.scroll_amount > 0 else "baixo")
            
            scroll_edit_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            scroll_edit_frame.pack(pady=5)
            
            ctk.CTkLabel(scroll_edit_frame, text="Qtd Scroll:").pack(side="left", padx=2)
            entry_scroll_edit = ctk.CTkEntry(scroll_edit_frame, width=60)
            entry_scroll_edit.insert(0, str(abs(step.scroll_amount)))
            entry_scroll_edit.pack(side="left", padx=2)
            
            ctk.CTkRadioButton(scroll_edit_frame, text="Cima", variable=scroll_dir_edit_var, value="cima", width=50).pack(side="left", padx=5)
            ctk.CTkRadioButton(scroll_edit_frame, text="Baixo", variable=scroll_dir_edit_var, value="baixo", width=50).pack(side="left", padx=5)

        def save():
            try:
                step.x = int(entry_x.get())
                step.y = int(entry_y.get())
                step.delay = float(entry_delay.get())
                step.double_click = bool(chk_double.get())
                
                if step.action_type == 'scroll':
                    amount = abs(int(entry_scroll_edit.get()))
                    step.scroll_amount = amount if scroll_dir_edit_var.get() == "cima" else -amount

                self.engine.update_step(index, step)
                self._refresh_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos.")

        ctk.CTkButton(dialog, text="Salvar", command=save, fg_color=COLOR_SUCCESS).pack(pady=20)


    def start_capture_thread(self):
        """Inicia a captura em uma thread separada para não travar a GUI."""
        self.lbl_status.configure(text="Capturando em 3 segundos...")
        threading.Thread(target=self._capture_position, daemon=True).start()

    def _capture_position(self):
        time.sleep(3)
        x, y = pyautogui.position()
        
        # Agenda a atualização da GUI para a thread principal
        self.after(0, lambda: self._update_capture_ui(x, y))

    def _update_capture_ui(self, x, y):
        self.entry_x.delete(0, "end")
        self.entry_x.insert(0, str(x))
        self.entry_y.delete(0, "end")
        self.entry_y.insert(0, str(y))
        self.lbl_status.configure(text=f"Capturado: {x}, {y}")

    def start_key_capture_thread(self):
        """Inicia thread para capturar atalho de teclado."""
        self.btn_capture_key.configure(state="disabled", text="Pressione...")
        self.entry_key.delete(0, "end")
        self.lbl_status.configure(text="Pressione o atalho desejado...", text_color="yellow")
        threading.Thread(target=self._capture_key_worker, daemon=True).start()

    def _capture_key_worker(self):
        """Worker que espera o hotkey."""
        try:
            # Lê o hotkey. Suppress=False para não bloquear o sistema.
            hotkey = keyboard.read_hotkey(suppress=False) 
            self.after(0, lambda: self._update_key_ui(hotkey))
        except Exception as e:
            print(f"Erro ao capturar tecla: {e}")
            self.after(0, lambda: self._reset_key_btn())

    def _update_key_ui(self, hotkey):
        self.entry_key.delete(0, "end")
        self.entry_key.insert(0, str(hotkey))
        self.lbl_status.configure(text=f"Atalho capturado: {hotkey}")
        self._reset_key_btn()

    def _reset_key_btn(self):
        self.btn_capture_key.configure(state="normal", text="Capturar Tecla")

    def add_step(self):
        try:
            # Validação simples
            x_str = self.entry_x.get()
            y_str = self.entry_y.get()
            delay_str = self.entry_delay.get()

            if not x_str or not y_str or not delay_str:
                self.lbl_status.configure(text="Erro: Preencha todos os campos!", text_color="red")
                return

            # Validação de Coordenadas
            screen_width, screen_height = pyautogui.size()
            x = int(x_str)
            y = int(y_str)
            
            if not self.ignore_bounds_warning:
                if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                    if not messagebox.askyesno("Coordenadas Suspeitas", f"As coordenadas ({x}, {y}) parecem estar fora da tela principal ({screen_width}x{screen_height}).\nDeseja adicionar mesmo assim?"):
                        return
                    else:
                        self.ignore_bounds_warning = True

            delay = float(delay_str)
            action_choice = self.opt_action.get()
            
            button = "left"
            action_type = "click"
            text_content = ""
            use_data_file = False
            clear_field = False
            double_click = False
            scroll_amount = 0
            
            if action_choice == "Clique Esquerdo":
                button = "left"
                double_click = bool(self.chk_double_click.get())
            elif action_choice == "Clique Direito":
                button = "right"
                double_click = bool(self.chk_double_click.get())
            elif action_choice == "Digitar Texto":
                action_type = "type"
                text_content = self.entry_text.get()
                use_data_file = bool(self.chk_use_file.get())
                clear_field = bool(self.chk_clear_field.get())
            elif action_choice == "Pressionar Enter":
                 action_type = "key"
                 text_content = "enter"
            elif action_choice == "Atalho de Teclado":
                 action_type = "key"
                 text_content = self.entry_key.get()
                 if not text_content:
                     self.lbl_status.configure(text="Erro: Capture ou digite um atalho!", text_color="red")
                     return
            elif action_choice == "Scroll":
                action_type = "scroll"
                try:
                    amount_raw = abs(int(self.entry_scroll.get()))
                    scroll_amount = amount_raw if self.scroll_dir_var.get() == "cima" else -amount_raw
                except ValueError:
                     self.lbl_status.configure(text="Erro: Valor de scroll inválido!", text_color="red")
                     return

            self.engine.add_step(x, y, delay, button, action_type, text_content, use_data_file, clear_field, double_click, scroll_amount)
            self._refresh_list()
            self.lbl_status.configure(text="Passo adicionado.", text_color="white")
        except ValueError:
            self.lbl_status.configure(text="Erro: Valores inválidos (digite apenas números).", text_color=COLOR_ERROR)

    def _refresh_list(self):
        # Limpa markers antigos
        self._clear_markers()
        
        # Limpa o frame atual
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        self.step_frames = [] # Armazena referências para highlight

        for i, step in enumerate(self.engine.steps):
            # Cria markers se checkbox ativo
            if self.markers_visible:
                m = DraggableMarker(self, i, step.x, step.y, self.on_marker_move)
                self.markers.append(m)
            
            # Container do item
            item_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            self.step_frames.append(item_frame)
            
            # Controles de Reordenação (Esquerda)
            reorder_box = ctk.CTkFrame(item_frame, fg_color="transparent")
            reorder_box.pack(side="left", padx=2)
            
            btn_up = ctk.CTkButton(reorder_box, text="▲", width=25, height=25, fg_color=COLOR_GRAY, command=lambda idx=i: self.move_step_up(idx))
            btn_up.pack(side="left", padx=1)
            btn_down = ctk.CTkButton(reorder_box, text="▼", width=25, height=25, fg_color=COLOR_GRAY, command=lambda idx=i: self.move_step_down(idx))
            btn_down.pack(side="left", padx=1)
            
            # Label do passo
            lbl = ctk.CTkLabel(item_frame, text=f"{i+1}. {step}", anchor="w")
            lbl.pack(side="left", fill="x", expand=True, padx=5)
            
            # Binding para Double Click (Editar)
            lbl.bind("<Double-Button-1>", lambda event, idx=i: self.edit_step(idx))
            
            # Botão de Remover (X)
            btn_remove = ctk.CTkButton(
                item_frame, 
                text="X", 
                width=30, 
                height=25, 
                fg_color="red", 
                command=lambda idx=i: self.remove_step_at(idx)
            )
            btn_remove.pack(side="right", padx=5)

    def _clear_markers(self):
        for m in self.markers:
            m.destroy()
        self.markers = []

    def toggle_markers(self):
        self.markers_visible = bool(self.chk_markers.get())
        self._refresh_list()

    def on_marker_move(self, index, new_x, new_y):
        """Callback chamado quando um marcador é solto."""
        if 0 <= index < len(self.engine.steps):
            step = self.engine.steps[index]
            step.x = new_x
            step.y = new_y
            print(f"Passo {index+1} atualizado para ({new_x}, {new_y})")
            # Recarrega a lista para mostrar novos valores
            self._refresh_list()

    def highlight_step(self, index):
        """
        Destaca o passo em execução ou atualiza estado visual.
        index >= 0: Highlight normal.
        index < 0: Códigos de status (-1=Fim, -2=Pause, -3=Wait).
        """
        if index < 0:
            if index == -1: # Fim / Reset
                 self._update_state_visuals(0) # 0 = Normal
            else:
                 self._update_state_visuals(index)
            # Remove highlight de list items se pausou/parou
            if index == -1: 
                for frame in self.step_frames:
                    try: frame.configure(fg_color="transparent")
                    except: pass
            return

        # Se estamos aqui, é um passo normal rodando (resetamos visual de pausa se houver)
        self._update_state_visuals(0)

        # Reseta cor de todos
        for frame in self.step_frames:
            try:
                frame.configure(fg_color="transparent")
            except:
                pass # Widget pode ter sido destruído
        
        # Destaca o atual se índice válido
        if 0 <= index < len(self.step_frames):
            try:
                self.step_frames[index].configure(fg_color=("gray75", "gray25"))
            except:
                pass
                
            if hasattr(self, 'osd_overlay') and self.osd_overlay and self.osd_overlay.winfo_exists():
                try:
                    total_loops = self.entry_loops.get() if not self.chk_infinite.get() else "Inf"
                    loop_text = f"Loop: {self.engine.current_loop} / {total_loops}"
                    
                    step_obj = self.engine.steps[index]
                    step_desc = str(step_obj)
                    if len(step_desc) > 42:
                        step_desc = step_desc[:40] + "..."
                    step_text = f"Passo {index+1}: {step_desc}"
                    
                    self.osd_overlay.update_info(loop_text, step_text)
                except Exception as e:
                    print(f"Erro ao atualizar OSD: {e}")

    def remove_step_at(self, index):
        self.engine.remove_step(index)
        self._refresh_list()
        self.lbl_status.configure(text="Passo removido.")

    def start_execution_thread(self):
        if not self.engine.steps:
            self.lbl_status.configure(text="A lista de passos está vazia!", text_color="yellow")
            return
            
        # Pega configurações de loop
        try:
            loops = int(self.entry_loops.get())
        except ValueError:
            self.lbl_status.configure(text="Número de loops inválido!", text_color="red")
            return
            
        infinite = self.chk_infinite.get()
        confirm_loops = bool(self.chk_confirm.get())
            
        self.lbl_status.configure(text="Executando...", text_color="white")
        self.btn_execute.configure(state="disabled")
        
        if hasattr(self, 'chk_osd') and self.chk_osd.get():
            try:
                self.osd_overlay = ProgressOverlay(self)
            except Exception as e:
                print(f"Erro ao iniciar OSD: {e}")
                
        self.iconify()
        threading.Thread(target=self._run_engine, args=(loops, infinite, confirm_loops), daemon=True).start()

    def _handle_confirmation_request(self, event):
        """Executa na thread principal (GUI) para mostrar o popup."""
        try:
            loop_num = self.confirm_request_queue.get_nowait()
            self.deiconify()
            result = messagebox.askyesno("Confirmar Loop", f"Loop {loop_num-1} finalizado.\nIniciar Loop {loop_num}?")
            if result:
                self.iconify()
            self.confirm_response_queue.put(result)
        except queue.Empty:
            pass

    def _run_engine(self, loops, infinite, confirm_loops):
        def confirmation_callback(loop_num):
            # Envia pedido para GUI
            self.confirm_request_queue.put(loop_num)
            self.event_generate("<<ConfirmationRequest>>")
            
            # Bloqueia esperando resposta
            return self.confirm_response_queue.get()

        self.engine.execute_sequence(
            loops=loops, 
            infinite=infinite, 
            on_step_callback=lambda i: self.after(0, self.highlight_step, i),
            confirm_between_loops=confirm_loops,
            confirm_callback=confirmation_callback
        )
        # Restaura estado ao finalizar
        self.after(0, self._on_execution_finished)

    def _on_execution_finished(self):
        self.deiconify()
        self.lbl_status.configure(text="Execução finalizada.")
        self.btn_execute.configure(state="normal")
        
        if hasattr(self, 'osd_overlay') and self.osd_overlay:
            try:
                self.osd_overlay.destroy()
            except:
                pass
            self.osd_overlay = None

    def stop_execution(self):
        if self.engine.is_running:
            self.engine.stop()
            self.lbl_status.configure(text="Parando...", text_color="yellow")

    def save_sequence(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                self.engine.save_to_file(filepath)
                self.lbl_status.configure(text=f"Salvo em {filepath.split('/')[-1]}")
            except Exception as e:
                self.lbl_status.configure(text=f"Erro ao salvar: {e}", text_color="red")


    def load_sequence(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                self.engine.load_from_file(filepath)
                self._refresh_list()
                self.lbl_status.configure(text=f"Carregado de {filepath.split('/')[-1]}")
            except Exception as e:
                self.lbl_status.configure(text=f"Erro ao carregar: {e}", text_color="red")

    def clear_list(self):
        self.engine.clear_steps()
        self._refresh_list()
        self.lbl_status.configure(text="Lista limpa.")

if __name__ == "__main__":
    print("ERRO: Este arquivo não deve ser executado diretamente.")
    print("Por favor, execute o arquivo 'main.py' na raiz do projeto.")
    print("Comando: python main.py")


