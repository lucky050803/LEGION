import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import pyflakes.api
import re

def send_query():
    """Simule une interaction avec un modèle Ollama et gère les erreurs si Ollama n'est pas configuré."""
    user_input = chat_entry.get()
    if user_input.strip():
        chat_log.insert(tk.END, f"You: {user_input}\n", "user")
        try:
            # Simule une requête à Ollama (remplace ici par l'API réelle si disponible)
            response = f"Ollama: Simulated response to '{user_input}'."  # Simule une réponse
            # Si Ollama n'est pas configuré, lève une exception
            if not ollama_is_configured():  # Fonction fictive, à remplacer par ta vérification réelle
                raise Exception("Ollama model is not configured.")
            chat_log.insert(tk.END, response + "\n", "ollama")
        except Exception as e:
            chat_log.insert(tk.END, f"Error: {str(e)}\n", "error")
            messagebox.showerror("Ollama Error", f"Failed to connect to Ollama: {str(e)}")
        chat_entry.delete(0, tk.END)

def ollama_is_configured():
    """Vérifie si Ollama est configuré (fonction simulée)."""
    return True  # Change à True si configuré pour tester le flux réussi.

def save_notes():
    """Enregistre le contenu de la zone de texte dans un fichier."""
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_editor.get("1.0", tk.END))

def load_notes():
    """Charge le contenu d'un fichier dans la zone de texte."""
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            content = file.read()
        text_editor.delete("1.0", tk.END)
        text_editor.insert(tk.END, content)

def open_terminal():
    """Ouvre un terminal en fonction de l'OS."""
    try:
        if os.name == "nt":  # Windows
            subprocess.run("start", shell=True)
        elif os.name == "posix":  # macOS/Linux
            subprocess.run("gnome-terminal" if "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP", "") else "xterm")
        else:
            raise OSError("Unsupported OS for terminal launch.")
    except Exception as e:
        messagebox.showerror("Terminal Error", f"Failed to open terminal: {str(e)}")

def check_syntax():
    """Vérifie la syntaxe du code selon le langage sélectionné."""
    code = text_editor.get("1.0", tk.END)
    language = language_var.get()  # Récupère le langage sélectionné
    
    if language == "Python":
        return check_python_syntax(code)
    elif language == "C" or language == "C++":
        return check_c_cpp_syntax(code, language)
    elif language == "VHDL":
        return check_vhdl_syntax(code)
    else:
        messagebox.showinfo("Syntax Check", "Unsupported language.")
        return True

def check_python_syntax(code):
    """Vérifie la syntaxe Python en utilisant pyflakes."""
    try:
        pyflakes.api.check(code, filename="code.py")
        messagebox.showinfo("Syntax Check", "Python code is valid!")
        return True
    except pyflakes.api.SyntaxError as e:
        messagebox.showerror("Syntax Error", f"Python Syntax Error: {str(e)}")
        return False

def check_c_cpp_syntax(code, language):
    """Vérifie la syntaxe C/C++ via gcc (en supposant que gcc est installé)."""
    try:
        with open("temp_code.c", "w") as temp_file:
            temp_file.write(code)
        if language == "C":
            subprocess.check_call(["gcc", "-fsyntax-only", "temp_code.c"])
        elif language == "C++":
            subprocess.check_call(["g++", "-fsyntax-only", "temp_code.c"])
        os.remove("temp_code.c")
        messagebox.showinfo("Syntax Check", f"{language} code is valid!")
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Syntax Error", f"{language} Syntax Error: {e}")
        return False

def check_vhdl_syntax(code):
    """Vérifie la syntaxe VHDL via un outil externe (par exemple, ghdl)."""
    try:
        with open("temp_code.vhdl", "w") as temp_file:
            temp_file.write(code)
        subprocess.check_call(["ghdl", "-a", "temp_code.vhdl"])  # Si ghdl est installé
        os.remove("temp_code.vhdl")
        messagebox.showinfo("Syntax Check", "VHDL code is valid!")
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Syntax Error", f"VHDL Syntax Error: {e}")
        return False

def apply_syntax_highlighting():
    """Applique la mise en forme syntaxique au texte du code."""
    code = text_editor.get("1.0", tk.END)
    text_editor.mark_set("range_start", "1.0")
    
    # Applique la coloration des mots-clés en Python
    keywords = r"\b(def|class|return|if|else|elif|for|while|import|from|try|except|finally)\b"
    operators = r"(\+|\-|\*|\/|\=|\<|\>)"
    functions = r"\b(print|len|range|input)\b"
    
    # Exemple de mise en couleur des mots-clés
    highlight_pattern(text_editor, keywords, "keyword")
    highlight_pattern(text_editor, operators, "operator")
    highlight_pattern(text_editor, functions, "function")
    
    # Pour d'autres langages, il faut ajouter les motifs et les couleurs correspondantes

def highlight_pattern(editor, pattern, tag):
    """Met en surbrillance un motif spécifique dans le texte."""
    start_idx = "1.0"
    while True:
        start_idx = editor.search(pattern, start_idx, stopindex=tk.END, regexp=True)
        if not start_idx:
            break
        end_idx = f"{start_idx}+{len(editor.get(start_idx, start_idx+1))}c"
        editor.tag_add(tag, start_idx, end_idx)
        editor.tag_config(tag, foreground="blue" if tag == "keyword" else "red")
        start_idx = end_idx

def toggle_dark_mode():
    """Active ou désactive le mode sombre."""
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.configure(bg="#2e2e2e")
        text_editor.config(bg="#3a3a3a", fg="white")
        chat_log.config(bg="#3a3a3a", fg="white")
        language_var.config(bg="#3a3a3a", fg="white")
        terminal_button.config(bg="#3a3a3a", fg="white")
        save_button.config(bg="#3a3a3a", fg="white")
        load_button.config(bg="#3a3a3a", fg="white")
        syntax_button.config(bg="#3a3a3a", fg="white")
        chat_entry.config(bg="#3a3a3a", fg="white")
        send_button.config(bg="#3a3a3a", fg="white")
        terminal_button.config(bg="#3a3a3a", fg="white")
    else:
        root.configure(bg="#f4f4f9")
        text_editor.config(bg="#ffffff", fg="black")
        chat_log.config(bg="#ffffff", fg="black")
        language_var.config(bg="#ffffff", fg="black")
        terminal_button.config(bg="#ffffff", fg="black")
        save_button.config(bg="#ffffff", fg="black")
        load_button.config(bg="#ffffff", fg="black")
        syntax_button.config(bg="#ffffff", fg="black")
        chat_entry.config(bg="#ffffff", fg="black")
        send_button.config(bg="#ffffff", fg="black")
        terminal_button.config(bg="#ffffff", fg="black")

# Initialisation de la fenêtre principale
root = tk.Tk()
root.title("Bloc-Notes Booster")
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

# Entrée et bouton de chat
chat_entry = ttk.Entry(root)
chat_entry.place(relx=0.65, rely=0.64, relwidth=0.28, relheight=0.05)
send_button = ttk.Button(root, text="Send", command=send_query)
send_button.place(relx=0.94, rely=0.64, relwidth=0.08, relheight=0.05)

# Menu de sélection de langage
language_var = tk.StringVar(value="Python")  # Définir la valeur par défaut
language_menu = ttk.Combobox(root, textvariable=language_var, values=["Python", "C", "C++", "VHDL"], state="readonly")
language_menu.place(relx=0.02, rely=0.88, relwidth=0.2, relheight=0.05)

# Boutons
save_button = ttk.Button(root, text="Save", command=save_notes)
save_button.place(relx=0.02, rely=0.92, relwidth=0.2, relheight=0.05)

load_button = ttk.Button(root, text="Load", command=load_notes)
load_button.place(relx=0.02, rely=0.98, relwidth=0.2, relheight=0.05)

syntax_button = ttk.Button(root, text="Check Syntax", command=check_syntax)
syntax_button.place(relx=0.7, rely=0.81, relwidth=0.28, relheight=0.05)

terminal_button = ttk.Button(root, text="Open Terminal", command=open_terminal)
terminal_button.place(relx=0.02, rely=0.94, relwidth=0.2, relheight=0.05)

# Bouton pour le mode sombre
dark_mode = False
dark_mode_button = ttk.Button(root, text="Toggle Dark Mode", command=toggle_dark_mode)
dark_mode_button.place(relx=0.02, rely=0.94, relwidth=0.2, relheight=0.05)

root.mainloop()
