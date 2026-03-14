from customtkinter import *
from socket import *
import threading

set_appearance_mode("Dark")
set_default_color_theme("blue")

class Window(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Мій чат")
        self.minsize(400, 400)

        # --- Ім'я користувача ---
        self.name = "Kamila"

        # --- БІЧНЕ МЕНЮ ---
        self.sidebar = CTkFrame(self, width=180)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        CTkLabel(self.sidebar, text="Ваш нік", font=("Arial", 16)).pack(pady=20)
        self.pole = CTkEntry(self.sidebar)
        self.pole.pack(pady=10)

        self.btn_theme = CTkButton(self.sidebar, text="🌙 / ☀️", command=self.change_theme)
        self.btn_theme.pack(pady=10)

        self.show_menu = True  # меню спочатку відкрите

        # --- Кнопка для відкриття/закриття меню (завжди зверху, поза меню) ---
        self.menu_toggle_btn = CTkButton(self, text="🔱", width=40, height=40, command=self.toggle_menu)
        self.menu_toggle_btn.place(x=5, y=5)  # завжди видно

        # --- ОСНОВНИЙ ЧАТ ---
        self.chat_frame = CTkFrame(self)
        self.chat_frame.pack(side="right", fill="both", expand=True)

        self.messages = CTkTextbox(self.chat_frame, state="disabled")
        self.messages.pack(fill="both", expand=True, padx=10, pady=10)

        # --- ПОЛЕ ВВЕДЕННЯ ---
        self.input_frame = CTkFrame(self.chat_frame, height=50)
        self.input_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        self.message_input = CTkEntry(self.input_frame, placeholder_text="Введіть повідомлення")
        self.message_input.pack(side="left", fill="x", expand=True, padx=5)
        self.message_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = CTkButton(self.input_frame, text="▶️", width=40, command=self.send_message)
        self.send_btn.pack(side="right")

        # --- Підключення до сервера ---
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            self.sock.send(self.name.encode("utf-8"))

            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитись до сервера {e}", is_self=False)

    # --- ЗМІНА ТЕМИ ---
    def change_theme(self):
        if get_appearance_mode() == "Dark":
            set_appearance_mode("Light")
        else:
            set_appearance_mode("Dark")

    # --- ВІДКРИТТЯ/ЗАКРИТТЯ МЕНЮ ---
    def toggle_menu(self):
        if self.show_menu:
            self.show_menu = False
            self.sidebar.pack_forget()  # ховаємо меню
        else:
            self.show_menu = True
            self.sidebar.pack(side="left", fill="y")  # показуємо меню знову

    # --- ДОДАЄМО ПОВІДОМЛЕННЯ ---
    def add_message(self, author, message="", is_self=False):
        self.messages.configure(state='normal')
        lines = message.split("\n")
        if is_self:
            for line in lines:
                self.messages.insert(END, f"{' ' * 30}{author}: {line}\n")
        else:
            for line in lines:
                self.messages.insert(END, f"{author}: {line}\n")
        self.messages.insert(END, "\n")
        self.messages.configure(state='disabled')
        self.messages.see(END)

    # --- ВІДПРАВКА ПОВІДОМЛЕННЯ ---
    def send_message(self):
        # Оновлюємо нік перед відправкою
        self.name = self.pole.get() if self.pole.get().strip() != "" else self.name

        message = self.message_input.get()
        if message:
            self.add_message(self.name, message, is_self=True)
            data = f"TEXT@{self.name}@{message}\n"
            try:
                self.sock.sendall(data.encode("utf-8"))
            except:
                pass
        self.message_input.delete(0, END)

    # --- ОТРИМАННЯ ПОВІДОМЛЕНЬ ---
    def receive_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    # --- ОБРОБКА ПОВІДОМЛЕНЬ ---
    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT" and len(parts) >= 3:
            author = parts[1]
            message = parts[2]
            if author != self.name:
                self.add_message(author, message, is_self=False)
        elif msg_type == "IMAGE" and len(parts) >= 4:
            author = parts[1]
            filename = parts[2]
            self.add_message(author, f"надіслав(ла) зображення: {filename}", is_self=False)
        else:
            self.add_message("Сервер", line, is_self=False)


win = Window()
win.mainloop()