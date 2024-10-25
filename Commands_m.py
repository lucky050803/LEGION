
import tkinter as tk



class CommandsModule:
    def __init__(self, app):
        self.app = app

    def add_custom_command(self, command_name, callback):
        """Ajoute une nouvelle commande personnalisée."""
        self.app.custom_commands[command_name] = callback

    def execute(self, command):
        if command in self.app.custom_commands:
            self.app.custom_commands[command](self.app)  # Appeler la commande personnalisée
        else:
            self.app.print_in_terminal(f"Commande inconnue : {command}")

    def show_custom_commands(self):
        """Affiche toutes les commandes personnalisées disponibles."""
        if not self.app.custom_commands:
            self.app.print_in_terminal("Aucune commande personnalisée n'a été ajoutée.")
        else:
            self.app.print_in_terminal("Commandes personnalisées disponibles :")
            for command in self.app.custom_commands:
                self.app.print_in_terminal(f"- {command}")