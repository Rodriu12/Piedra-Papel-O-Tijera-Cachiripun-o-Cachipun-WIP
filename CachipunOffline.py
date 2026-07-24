import random
from tkinter import *

ventana = Tk()
ventana.title("CACHIPUN GAME")
width, height = 350, 408
window_width = ventana.winfo_screenwidth()
window_height = ventana.winfo_screenheight()
x = (window_width // 2) - (width // 2)
y = (window_height // 2) - (height // 2)
ventana.geometry(f"{width}x{height}+{x}+{y}")
ventana.resizable(False, False)
ventana.config(bg="#e3f4f1")


FACTOR = 3


rock_p = PhotoImage(file="resources/rock_player.png").subsample(FACTOR, FACTOR)
paper_p = PhotoImage(file="resources/paper_player.png").subsample(FACTOR, FACTOR)
scissor_p = PhotoImage(file="resources/scissor_player.png").subsample(FACTOR, FACTOR)
rock_c = PhotoImage(file="resources/rock_computer.png").subsample(FACTOR, FACTOR)
paper_c = PhotoImage(file="resources/paper_computer.png").subsample(FACTOR, FACTOR)
scissor_c = PhotoImage(file="resources/scissor_computer.png").subsample(FACTOR, FACTOR)


img_width = rock_p.width()
img_height = rock_p.height()


blank = PhotoImage(width=img_width, height=img_height)
blank.put("#FFFFFF", to=(0, 0, img_width, img_height))


canvas_player = Canvas(ventana, width=img_width, height=img_height, bg='white', highlightthickness=0)
canvas_computer = Canvas(ventana, width=img_width, height=img_height, bg='white', highlightthickness=0)
canvas_player.grid(row=2, column=1, padx=30, pady=20)
canvas_computer.grid(row=2, column=3, pady=20)


player_img_id = canvas_player.create_image(0, 0, anchor='nw', image=blank)
computer_img_id = canvas_computer.create_image(0, 0, anchor='nw', image=blank)


Label(ventana, text="Jugador", bg="#e8c1c7", fg="black",
      font=('Times New Roman', 18, 'bold')).grid(row=1, column=1)
Label(ventana, text="IA", bg="#e8c1c7", fg="black",
      font=('Times New Roman', 18, 'bold')).grid(row=1, column=3)

status_label = Label(ventana, text="", fg="black",
                     font=('Times New Roman', 20, 'bold', 'italic'))
status_label.grid(row=3, column=2)


btn_rock = Button(ventana, image=rock_p, command=lambda: jugar(1))
btn_paper = Button(ventana, image=paper_p, command=lambda: jugar(2))
btn_scissor = Button(ventana, image=scissor_p, command=lambda: jugar(3))
btn_quit = Button(ventana, text="Salir", bg="red", fg="white",
                  font=('Times New Roman', 25, 'bold'), command=lambda: (ventana.destroy(), exit()))

btn_rock.grid(row=4, column=1, pady=30)
btn_paper.grid(row=4, column=2, pady=30)
btn_scissor.grid(row=4, column=3, pady=30)
btn_quit.grid(row=5, column=2)


opciones = {
    1: ("Piedra", rock_p, rock_c),
    2: ("Papel", paper_p, paper_c),
    3: ("Tijera", scissor_p, scissor_c)
}

def jugar(eleccion_jugador):
    # Deshabilitar botones mientras se muestra el resultado
    btn_rock.config(state=DISABLED)
    btn_paper.config(state=DISABLED)
    btn_scissor.config(state=DISABLED)

    canvas_player.itemconfig(player_img_id, image=opciones[eleccion_jugador][1])

    eleccion_ia = random.randint(1, 3)
    canvas_computer.itemconfig(computer_img_id, image=opciones[eleccion_ia][2])

    if eleccion_jugador == eleccion_ia:
        resultado = "Empate"
    elif (eleccion_jugador == 1 and eleccion_ia == 3) or \
         (eleccion_jugador == 2 and eleccion_ia == 1) or \
         (eleccion_jugador == 3 and eleccion_ia == 2):
        resultado = "¡Ganaste!"
    else:
        resultado = "¡Perdiste!"

    status_label.config(text=resultado)
    ventana.after(1500, reiniciar)

def reiniciar():
    canvas_player.itemconfig(player_img_id, image=blank)
    canvas_computer.itemconfig(computer_img_id, image=blank)
    status_label.config(text="")
    btn_rock.config(state=NORMAL)
    btn_paper.config(state=NORMAL)
    btn_scissor.config(state=NORMAL)

if __name__ == '__main__':
    ventana.mainloop()