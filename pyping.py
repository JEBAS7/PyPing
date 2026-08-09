import socket
import time
import tkinter as tk
import threading

# --- CONFIGURAÇÕES DO SERVIDOR DO BDO ---
IP_SERVIDOR_BDO = "20.206.139.219"
PORTA_BDO = 8884
INTERVALO_MILISSEGUNDOS = 1000  # O Tkinter trabalha melhor com milissegundos (1000ms = 1s)


def disparar_ping(host, porta):
    timeout_segundos = 1.5
    try:
        # Usa AF_INET e SOCK_STREAM para testar a porta TCP aberta do servidor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout_segundos)
            antes = time.time()
            s.connect((host, porta))
            s.sendall(b'\n')
            s.recv(32)  # Baixado para 32 bytes apenas para validar a resposta rápida
            depois = time.time()
            return int((depois - antes) * 1000)
    except (socket.timeout, socket.error):
        return -1


class PingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BDO Ping Overlay")
        self.root.overrideredirect(True)  # Remove bordas da janela
        self.root.attributes("-topmost", True)  # Sempre no topo do jogo
        self.root.config(bg="black")
        self.root.attributes("-transparentcolor", "black")  # Fundo preto fica transparente

        # Posição inicial na tela (X=1500, Y=50)
        self.root.geometry("+1500+50")

        # Texto do Ping
        self.label = tk.Label(
            self.root,
            text="BDO Ping: -- ms",
            font=("Consolas", 14, "bold"),
            fg="#00FF00",
            bg="black"
        )
        self.label.pack()

        # Arrastar a janela com o mouse
        self.label.bind("<Button-1>", self.iniciar_arrasto)
        self.label.bind("<B1-Motion>", self.arrastar_janela)

        # Inicia o ciclo de atualização seguro
        self.atualizar_ping_seguro()

    def iniciar_arrasto(self, event):
        self.x = event.x
        self.y = event.y

    def arrastar_janela(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        novo_x = self.root.winfo_x() + deltax
        novo_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{novo_x}+{novo_y}")

    def executar_ping_async(self):
        """Executa o teste de rede em uma Thread isolada para não travar a interface"""
        tempo = disparar_ping(IP_SERVIDOR_BDO, PORTA_BDO)

        # Agenda a atualização visual na Thread Principal com segurança
        if self.root.winfo_exists():
            self.root.after(0, self.atualizar_interface, tempo)

    def atualizar_interface(self, tempo):
        """Aplica o texto e as cores na interface de maneira limpa"""
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

        if self.root.winfo_exists():
            self.label.config(text=texto, fg=cor)

    def atualizar_ping_seguro(self):
        """Gerenciador de loop nativo do Tkinter que impede vazamento de memória"""
        # Cria a thread pontual apenas para o disparo atual
        t = threading.Thread(target=self.executar_ping_async, daemon=True)
        t.start()

        # Agenda a próxima execução de forma limpa, liberando a memória da atual
        if self.root.winfo_exists():
            self.root.after(INTERVALO_MILISSEGUNDOS, self.atualizar_ping_seguro)

    def iniciar(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PingOverlay()
    app.iniciar()
