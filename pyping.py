import socket
import time
import sys
import tkinter as tk
import threading

# --- CONFIGURAÇÕES DO SERVIDOR DO BDO ---
IP_SERVIDOR_BDO = "20.206.139.219" 
PORTA_BDO = 8884
INTERVALO_SEGUNDOS = 1.0
# ----------------------------------------

def disparar_ping(host, porta):
    timeout_segundos = 2.0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout_segundos)
            antes = time.time()
            s.connect((host, porta))
            s.sendall(b'\n')
            s.recv(1024)
            depois = time.time()
            return int((depois - antes) * 1000)
    except (socket.timeout, socket.error):
        return -1

class PingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BDO Ping Overlay")
        self.root.overrideredirect(True)      # Remove bordas da janela
        self.root.attributes("-topmost", True)  # Sempre no topo do jogo
        self.root.config(bg="black")
        self.root.attributes("-transparentcolor", "black") # Torna o fundo preto transparente
        
        # Posição inicial na tela (X=20, Y=20) - Altere se quiser mover o padrão
        self.root.geometry("+20+20")
        
        # Texto do Ping (Verde limão para destacar no jogo)
        self.label = tk.Label(
            self.root, 
            text="BDO Ping: -- ms", 
            font=("Consolas", 14, "bold"), 
            fg="#00FF00", 
            bg="black"
        )
        self.label.pack()
        
        # Permite arrastar o ping clicando e segurando com o mouse
        self.label.bind("<Button-1>", self.iniciar_arrasto)
        self.label.bind("<B1-Motion>", self.arrastar_janela)

        self.rodando = True
        self.thread_ping = threading.Thread(target=self.atualizar_ping, daemon=True)
        self.thread_ping.start()

    def iniciar_arrasto(self, event):
        self.x = event.x
        self.y = event.y

    def arrastar_janela(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        novo_x = self.root.winfo_x() + deltax
        novo_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{novo_x}+{novo_y}")

    def atualizar_ping(self):
        while self.rodando:
            tempo = disparar_ping(IP_SERVIDOR_BDO, PORTA_BDO)
            
            if tempo >= 0:
                texto = f"BDO Ping: {tempo} ms"
                if tempo < 40:
                    cor = "#00FF00"  # Verde (Bom)
                elif tempo < 90:
                    cor = "#FFFF00"  # Amarelo (Médio)
                else:
                    cor = "#FF3333"  # Vermelho (Ruim)
            else:
                texto = "BDO Ping: FALHA"
                cor = "#FF3333"
            
            try:
                self.root.after(0, lambda t=texto, c=cor: self.label.config(text=t, fg=c))
            except Exception:
                break
                
            time.sleep(INTERVALO_SEGUNDOS)

    def iniciar(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.rodando = False

if __name__ == "__main__":
    app = PingOverlay()
    app.iniciar()
