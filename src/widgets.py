import customtkinter as ctk
import pyautogui
import time

class DraggableMarker(ctk.CTkToplevel):
    """Marcador visual que pode ser arrastado (segure 1s) ou clica através (toque rápido)."""
    def __init__(self, parent, step_index, x, y, on_move_callback):
        super().__init__(parent)
        self.step_index = step_index
        self.on_move_callback = on_move_callback
        
        # Remove barra de título e bordas
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry(f"20x20+{x-10}+{y-10}") # Centraliza no ponto
        
        # Cor visual
        self.frame = ctk.CTkFrame(self, fg_color="red", corner_radius=10)
        self.frame.pack(expand=True, fill="both")
        
        # Label com número
        self.lbl = ctk.CTkLabel(self.frame, text=str(step_index + 1), text_color="white", font=("Arial", 10, "bold"))
        self.lbl.pack(expand=True)
        
        # Bindings de arraste e clique
        self.frame.bind("<Button-1>", self.start_click)
        self.frame.bind("<B1-Motion>", self.do_move)
        self.frame.bind("<ButtonRelease-1>", self.stop_click)
        self.lbl.bind("<Button-1>", self.start_click)
        self.lbl.bind("<B1-Motion>", self.do_move)
        self.lbl.bind("<ButtonRelease-1>", self.stop_click)
        
        self.x_offset = 0
        self.y_offset = 0
        self.start_time = 0
        self.is_dragging = False

    def start_click(self, event):
        self.start_time = time.time()
        self.is_dragging = False
        self.x_offset = event.x
        self.y_offset = event.y

    def do_move(self, event):
        # Só permite mover se segurou por mais de 1 segundo
        if time.time() - self.start_time < 0.5: # Reduzi um pouco para teste, mas o user pediu 1s
             # User pediu 1s, vou manter 1s na logica real, mas para UX as vezes 1s é muito. 
             # O prompt diz "segurar por 1s", vou respeitar estritamente.
             pass

        if time.time() - self.start_time < 1.0:
            return 
            
        self.is_dragging = True
        self.frame.configure(fg_color="#ff6666") # Feedback visual (vermelho mais claro)
        
        x = self.winfo_x() + event.x - self.x_offset
        y = self.winfo_y() + event.y - self.y_offset
        self.geometry(f"+{x}+{y}")

    def stop_click(self, event):
        self.frame.configure(fg_color="red") # Restaura cor
        
        # Se não arrastou e foi rápido (<1s), então é pass-through
        if not self.is_dragging and (time.time() - self.start_time < 1.0):
            self.withdraw() # Esconde janela
            self.update() # Garante que sumiu visualmente
            
            # Clica no ponto atual onde o mouse está (que agora vê o app de baixo)
            pyautogui.click()
            
            self.deiconify() # Mostra de volta
            return

        # Se estava arrastando, finaliza e salva a nova posição
        if self.is_dragging:
            center_x = self.winfo_x() + 10
            center_y = self.winfo_y() + 10
            self.on_move_callback(self.step_index, center_x, center_y)
