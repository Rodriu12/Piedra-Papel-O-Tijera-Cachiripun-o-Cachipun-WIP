import random
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

# Constantes que permiten acceder a las variables más rápido y para fijar el puerto
# También se usa para que la imagen se reinicie cada 3 segundos después de haber elegido la opción 
# Según cliente o servidor

FACTOR = 3
PUERTO = 5000

# Interfaz del juego
ventana = tk.Tk()
ventana.title("CACHIPUN ONLINE")
ventana.geometry("650x620")
ventana.resizable(False, False)
ventana.config(bg="#e3f4f1")

# Cargar imágenes desde resources para mostrarlas en la interfaz del juego
rock_p = tk.PhotoImage(file="resources/rock_player.png").subsample(FACTOR, FACTOR)
paper_p = tk.PhotoImage(file="resources/paper_player.png").subsample(FACTOR, FACTOR)
scissor_p = tk.PhotoImage(file="resources/scissor_player.png").subsample(FACTOR, FACTOR)
rock_c = tk.PhotoImage(file="resources/rock_computer.png").subsample(FACTOR, FACTOR)
paper_c = tk.PhotoImage(file="resources/paper_computer.png").subsample(FACTOR, FACTOR)
scissor_c = tk.PhotoImage(file="resources/scissor_computer.png").subsample(FACTOR, FACTOR)


img_width = rock_p.width()
img_height = rock_p.height()
blank = tk.PhotoImage(width=img_width, height=img_height)
blank.put("#FFFFFF", to=(0, 0, img_width, img_height))


opciones_img = {
    1: ("Piedra", rock_p),
    2: ("Papel", paper_p),
    3: ("Tijera", scissor_p)
}


modo_actual = None
partida_activa = False
mi_eleccion = 0
eleccion_oponente = 0
socket_cliente = None
conexion_aceptada = None
resultado_mostrado = False
turno_local = True

# Funciones para esperar la conexión entrante del oponente
def iniciar_servidor_real(ip_escucha):
    global conexion_aceptada
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((ip_escucha, PUERTO))
        servidor.listen(1)
        ventana.after(0, lambda: status_label.config(text=f"Esperando oponente en {ip_escucha}:{PUERTO}..."))
        conexion_aceptada, dir_cliente = servidor.accept()
        servidor.close()
        ventana.after(0, lambda: status_label.config(text=f"Conectado con {dir_cliente[0]}"))
        ventana.after(0, lambda: habilitar_botones(True))
        global partida_activa
        partida_activa = True
        threading.Thread(target=recibir_datos, daemon=True).start()
    except Exception as e:
        ventana.after(0, lambda: messagebox.showerror("Error", f"No se pudo iniciar servidor:\n{e}"))
        ventana.after(0, volver_menu)

def conectar_cliente_real(ip):
    global socket_cliente
    try:
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.connect((ip, PUERTO))
        ventana.after(0, lambda: status_label.config(text=f"Conectado a {ip}"))
        ventana.after(0, lambda: habilitar_botones(True))
        global partida_activa
        partida_activa = True
        threading.Thread(target=recibir_datos, daemon=True).start()
    except Exception as e:
        ventana.after(0, lambda: messagebox.showerror("Error", f"No se pudo conectar:\n{e}"))
        ventana.after(0, volver_menu)

def recibir_datos():
    global eleccion_oponente, partida_activa, resultado_mostrado
    conn = conexion_aceptada if modo_actual == "servidor" else socket_cliente
    while partida_activa:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            eleccion = int(data)
            eleccion_oponente = eleccion
            if mi_eleccion == 0:
                ventana.after(0, lambda: status_label.config(text="El oponente ha elegido. Elige tu opcion."))
            ventana.after(0, verificar_ambos_elegidos)
        except:
            break
    partida_activa = False
    ventana.after(0, lambda: status_label.config(text="Conexión perdida"))
    ventana.after(0, lambda: habilitar_botones(False))
    ventana.after(0, lambda: boton_volver.config(state=tk.NORMAL))

def enviar_eleccion(eleccion):
    conn = conexion_aceptada if modo_actual == "servidor" else socket_cliente
    try:
        conn.send(str(eleccion).encode())
    except:
        pass

def verificar_ambos_elegidos():
    global resultado_mostrado, mi_eleccion, eleccion_oponente
    if resultado_mostrado:
        return
    if mi_eleccion != 0 and eleccion_oponente != 0:
        resultado_mostrado = True
        img_oponente = opciones_img[eleccion_oponente][1]
        canvas_oponente.itemconfig(oponente_img_id, image=img_oponente)
        img_propia = opciones_img[mi_eleccion][1]
        canvas_jugador.itemconfig(jugador_img_id, image=img_propia)
        if mi_eleccion == eleccion_oponente:
            res = "Empate"
        elif (mi_eleccion == 1 and eleccion_oponente == 3) or \
             (mi_eleccion == 2 and eleccion_oponente == 1) or \
             (mi_eleccion == 3 and eleccion_oponente == 2):
            res = "¡Ganaste!"
        else:
            res = "¡Perdiste!"
        status_label.config(text=res)
        ventana.after(2000, reiniciar_red)

def reiniciar_red():
    global mi_eleccion, eleccion_oponente, resultado_mostrado
    mi_eleccion = 0
    eleccion_oponente = 0
    resultado_mostrado = False
    canvas_jugador.itemconfig(jugador_img_id, image=blank)
    canvas_oponente.itemconfig(oponente_img_id, image=blank)
    status_label.config(text="Elige tu jugada")
    habilitar_botones(True)

# Funciones de la interfaz para su correcto funcionamiento
def habilitar_botones(estado):
    estado = tk.NORMAL if estado else tk.DISABLED
    btn_rock.config(state=estado)
    btn_paper.config(state=estado)
    btn_scissor.config(state=estado)

def volver_menu():
    """Cierra conexiones y vuelve al menú principal."""
    global partida_activa, socket_cliente, conexion_aceptada
    partida_activa = False
    if socket_cliente:
        try: socket_cliente.close()
        except: pass
        socket_cliente = None
    if conexion_aceptada:
        try: conexion_aceptada.close()
        except: pass
        conexion_aceptada = None
    mostrar_frame_menu()
    habilitar_botones(False)
    canvas_jugador.itemconfig(jugador_img_id, image=blank)
    canvas_oponente.itemconfig(oponente_img_id, image=blank)
    status_label.config(text="")
    boton_volver.config(state=tk.NORMAL)

def mostrar_frame_menu():
    frame_menu.grid()
    canvas_jugador.grid_remove()
    canvas_oponente.grid_remove()
    status_label.grid_remove()
    btn_rock.grid_remove()
    btn_paper.grid_remove()
    btn_scissor.grid_remove()
    boton_volver.grid_remove()

def mostrar_frame_juego():
    frame_menu.grid_remove()
    canvas_jugador.grid(row=2, column=1, padx=30, pady=20)
    canvas_oponente.grid(row=2, column=3, pady=20)
    status_label.grid(row=3, column=2)
    btn_rock.grid(row=4, column=1, pady=30)
    btn_paper.grid(row=4, column=2, pady=30)
    btn_scissor.grid(row=4, column=3, pady=30)
    boton_volver.grid(row=5, column=0, columnspan=5, pady=10)

def iniciar_servidor():
    ip = simpledialog.askstring(
        "Configurar servidor",
        "Ingresa la IP donde escucharás (0.0.0.0 para todas las interfaces):",
        initialvalue="0.0.0.0"
    )
    if ip is None:   # Canceló
        return
    ip = ip.strip()
    if not ip:
        messagebox.showerror("Error", "Debes ingresar una IP válida.")
        return
    global modo_actual
    modo_actual = "servidor"
    mostrar_frame_juego()
    status_label.config(text=f"Iniciando servidor en {ip}:{PUERTO}...")
    habilitar_botones(False)
    boton_volver.config(state=tk.NORMAL)
    threading.Thread(target=iniciar_servidor_real, args=(ip,), daemon=True).start()

def iniciar_cliente():
    ip = simpledialog.askstring("Conectar", "Ingresa la IP del servidor:")
    if not ip:
        return
    global modo_actual
    modo_actual = "cliente"
    mostrar_frame_juego()
    status_label.config(text="Conectando...")
    habilitar_botones(False)
    boton_volver.config(state=tk.NORMAL)
    threading.Thread(target=conectar_cliente_real, args=(ip,), daemon=True).start()

# ---------------------------- EVENTOS DE BOTONES (jugada) ----------------------------
def on_rock():
    global mi_eleccion, resultado_mostrado
    if not partida_activa or mi_eleccion != 0:
        return
    mi_eleccion = 1
    canvas_jugador.itemconfig(jugador_img_id, image=rock_p)
    habilitar_botones(False)
    enviar_eleccion(1)
    status_label.config(text="Esperando al oponente...")
    verificar_ambos_elegidos()

def on_paper():
    global mi_eleccion, resultado_mostrado
    if not partida_activa or mi_eleccion != 0:
        return
    mi_eleccion = 2
    canvas_jugador.itemconfig(jugador_img_id, image=paper_p)
    habilitar_botones(False)
    enviar_eleccion(2)
    status_label.config(text="Esperando al oponente...")
    verificar_ambos_elegidos()

def on_scissor():
    global mi_eleccion, resultado_mostrado
    if not partida_activa or mi_eleccion != 0:
        return
    mi_eleccion = 3
    canvas_jugador.itemconfig(jugador_img_id, image=scissor_p)
    habilitar_botones(False)
    enviar_eleccion(3)
    status_label.config(text="Esperando al oponente...")
    verificar_ambos_elegidos()

frame_menu = tk.Frame(ventana, bg="#e3f4f1")
frame_menu.grid(row=0, column=0, padx=50, pady=50)

tk.Label(frame_menu, text="CACHIPUN ONLINE", font=('Arial', 24, 'bold'), bg="#e3f4f1").pack(pady=20)
tk.Button(frame_menu, text="Servidor (LAN/Remoto)", font=('Arial', 14), command=iniciar_servidor, width=25, height=2).pack(pady=5)
tk.Button(frame_menu, text="Cliente (LAN/Remoto)", font=('Arial', 14), command=iniciar_cliente, width=25, height=2).pack(pady=5)
tk.Button(frame_menu, text="Salir", font=('Arial', 14), command=ventana.destroy, width=25, height=2, bg="red", fg="white").pack(pady=20)

# Widgets del juego
canvas_jugador = tk.Canvas(ventana, width=img_width, height=img_height, bg='white', highlightthickness=0)
canvas_oponente = tk.Canvas(ventana, width=img_width, height=img_height, bg='white', highlightthickness=0)
jugador_img_id = canvas_jugador.create_image(0, 0, anchor='nw', image=blank)
oponente_img_id = canvas_oponente.create_image(0, 0, anchor='nw', image=blank)

tk.Label(ventana, text="Tú", bg="#e8c1c7", fg="black", font=('Times New Roman', 18, 'bold')).grid(row=1, column=1)
tk.Label(ventana, text="Oponente", bg="#e8c1c7", fg="black", font=('Times New Roman', 18, 'bold')).grid(row=1, column=3)

status_label = tk.Label(ventana, text="", fg="black", font=('Times New Roman', 20, 'bold', 'italic'))
status_label.grid(row=3, column=2)

btn_rock = tk.Button(ventana, image=rock_p, command=on_rock)
btn_paper = tk.Button(ventana, image=paper_p, command=on_paper)
btn_scissor = tk.Button(ventana, image=scissor_p, command=on_scissor)
boton_volver = tk.Button(ventana, text="Volver al menú", command=volver_menu, bg="orange", font=('Arial', 12))

for w in (canvas_jugador, canvas_oponente, status_label, btn_rock, btn_paper, btn_scissor, boton_volver):
    w.grid_remove()

mostrar_frame_menu()

if __name__ == '__main__':
    ventana.mainloop()