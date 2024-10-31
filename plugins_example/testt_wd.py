# Exemple de plugin Python (plugins/plugin_exemple.py)
import tkinter as tk
from tkinter import ttk, filedialog

def init_plugin(app):
    app.print_in_terminal("Le plugin exemple est chargé !")
    # Exemple d'interaction : ajouter une nouvelle commande
    app.commands.add_custom_command("/wd", wd)

def wd(app):
    wd_tab = ttk.Frame(app.notebook)
    app.notebook.add(wd_tab, text="YES")  # Ajoute l'onglet au notebook

