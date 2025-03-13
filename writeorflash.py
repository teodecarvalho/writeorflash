import tkinter as tk
import time
import threading
from tkinter import messagebox

class WriteOrFlash:
    def __init__(self, root):
        self.root = root
        self.root.title("Write or Die")
        self.root.state("zoomed")

        self.font_size = tk.IntVar(value=12)
        self.word_goal = tk.IntVar(value=500)
        self.time_limit = tk.IntVar(value=30)
        self.start_time = None
        self.last_typing_time = None
        self.stop_flag = False
        self.transition_steps = []
        self.flashing = False
        self.flash_state = False
        self.flash_task = None

        self.setup_ui()
        self.root.after(100, self.update_font_size)

    def setup_ui(self):
        tk.Label(self.root, text="Número de palavras:", font=("Verdana", 12)).pack()
        tk.Entry(self.root, textvariable=self.word_goal, font=("Verdana", 12)).pack()
        
        tk.Label(self.root, text="Tempo limite (minutos):", font=("Verdana", 12)).pack()
        tk.Entry(self.root, textvariable=self.time_limit, font=("Verdana", 12)).pack()
        
        tk.Label(self.root, text="Tamanho da fonte:", font=("Verdana", 12)).pack()
        font_entry = tk.Entry(self.root, textvariable=self.font_size, font=("Verdana", 12))
        font_entry.pack()
        font_entry.bind("<Return>", self.update_font_size)
        
        self.start_button = tk.Button(self.root, text="Iniciar", command=self.start_writing, font=("Verdana", 12))
        self.start_button.pack()
        
        self.text_area = tk.Text(self.root, wrap=tk.WORD, state=tk.DISABLED, font=("Verdana", self.font_size.get()))
        self.text_area.pack(expand=True, fill=tk.BOTH)

    def update_font_size(self, event=None):
        new_size = self.font_size.get()
        self.text_area.config(font=("Verdana", new_size))

    def start_writing(self):
        self.start_time = time.time()
        self.last_typing_time = self.start_time
        self.stop_flag = False
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.bind("<Key>", self.on_typing)
        self.text_area.focus_set()
        self.update_font_size()
        
        self.start_button.config(state=tk.DISABLED)
        
        threading.Thread(target=self.monitor_typing, daemon=True).start()
        threading.Thread(target=self.check_time_limit, daemon=True).start()

    def on_typing(self, event):
        self.last_typing_time = time.time()
        self.cancel_transition()

    def monitor_typing(self):
        while not self.stop_flag:
            time.sleep(1)
            if time.time() - self.last_typing_time > 5:
                self.root.after(0, self.start_red_transition)

    def start_red_transition(self):
        if time.time() - self.last_typing_time <= 5:
            return
        self.cancel_transition()
        self.animate_red(0)

    def animate_red(self, step):
        total_steps = 25
        delay = 100
        gb = int(255 * (1 - step / total_steps))
        color = f"#ff{gb:02x}{gb:02x}"
        
        self.root.config(bg=color)
        self.text_area.config(bg=color)
        
        if step < total_steps:
            next_step = step + 1
            task = self.root.after(delay, lambda: self.animate_red(next_step))
            self.transition_steps.append(task)
        else:
            # Quando a transição termina, definimos vermelho puro
            self.root.config(bg="red")
            self.text_area.config(bg="red")
            self.start_flashing()

    def start_flashing(self):
        if not self.flashing:
            self.flashing = True
            self.flash_state = True  # Começa no vermelho
            self.flash_cycle()

    def flash_cycle(self):
        if not self.flashing:
            return
        self.flash_state = not self.flash_state
        color = "red" if self.flash_state else "white"
        self.root.config(bg=color)
        self.text_area.config(bg=color)
        self.flash_task = self.root.after(500, self.flash_cycle)

    def cancel_transition(self):
        # Cancelar qualquer transição pendente
        for task in self.transition_steps:
            self.root.after_cancel(task)
        self.transition_steps.clear()

        # Parar a piscada, se estiver ocorrendo
        if self.flashing and self.flash_task:
            self.root.after_cancel(self.flash_task)
        
        self.flashing = False
        self.flash_task = None
        
        self.root.config(bg="white")
        self.text_area.config(bg="white")

    def check_time_limit(self):
        limit = self.time_limit.get() * 60
        while time.time() - self.start_time < limit and not self.stop_flag:
            time.sleep(1)
        self.stop_flag = True
        self.cancel_transition()
        self.evaluate_writing()

    def evaluate_writing(self):
        text = self.text_area.get("1.0", tk.END).strip()
        word_count = len(text.split())
        goal = self.word_goal.get()
        
        if word_count >= goal:
            messagebox.showinfo("Parabéns!", "Você atingiu sua meta!")
        else:
            messagebox.showwarning("Ops!", "Você não atingiu sua meta!")
        
        self.text_area.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = WriteOrFlash(root)
    root.mainloop()
