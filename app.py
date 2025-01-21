import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import re

def toggle_dark_mode():
    """Active ou désactive le mode sombre."""
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.configure(bg="#2e2e2e")
        text_editor.config(bg="#3a3a3a", fg="white")
        chat_log.config(bg="#3a3a3a", fg="white")
        language_var.config(bg="#3a3a3a", fg="white")

    else:
        root.configure(bg="#f4f4f9")
        text_editor.config(bg="#ffffff", fg="black")
        chat_log.config(bg="#ffffff", fg="black")
        language_var.config(bg="#ffffff", fg="black")

# Initialisation de la fenêtre principale
root = tk.Tk()
root.title("LEGION")
root.geometry("1000x600")
root.configure(bg="#f4f4f9")

# Variables et style
style = ttk.Style(root)
style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))

# Widgets pour l'éditeur de texte
text_editor = tk.Text(root, wrap="word", font=("Consolas", 12))
text_editor.place(relwidth=0.6, relheight=0.8, relx=0.02, rely=0.02)

# Chat log
chat_log = tk.Text(root, height=15, wrap="word", font=("Arial", 10))
chat_log.place(relx=0.65, rely=0.02, relwidth=0.33, relheight=0.6)
chat_log.config(state=tk.DISABLED)

# Menu de sélection de langage
language_var = tk.StringVar(value="VHDL")  # Définir la valeur par défaut
language_menu = ttk.Combobox(root, textvariable=language_var, values=["C", "C++", "VHDL"], state="readonly")
language_menu.place(relx=0.02, rely=0.88, relwidth=0.2, relheight=0.05)

# Bouton pour le mode sombre
dark_mode = False
dark_mode_button = ttk.Button(root, text="Toggle Dark Mode", command=toggle_dark_mode)
dark_mode_button.place(relx=0.02, rely=0.94, relwidth=0.2, relheight=0.05)

root.mainloop()
