import keyword
import re


class PythonHelperPlugin:
    def __init__(self, app):
        """Initialisation du plugin en lien avec l'application Legion."""
        self.app = app
        self.python_keywords = keyword.kwlist  # Liste des mots-clés Python

    def is_python_file(self, file_path):
        """Vérifie si le fichier ouvert est un fichier Python."""
        return file_path and file_path.endswith(".py")

    def analyze_code(self, content):
        """Analyse le contenu du fichier Python et retourne des suggestions."""
        suggestions = []
        
        # Vérifier les erreurs basiques
        if not content.endswith('\n'):
            suggestions.append("Le fichier ne se termine pas par une nouvelle ligne. Ajoutez une ligne vide à la fin.")

        # Vérification de l'indentation
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line and not line.startswith((' ', '\t')) and not re.match(r'^\s*#', line):
                suggestions.append(f"Ligne {i + 1} : L'indentation semble incorrecte.")
        return suggestions

    def get_current_code(self):
        """Récupère le contenu actuel de l'onglet Bloc Notes ou Projet."""
        notepad_tab = None
        for i in range(self.app.notebook.index("end")):
            tab_text = self.app.notebook.tab(i, "text")
            if "Bloc Notes" in tab_text or "Projet" in tab_text:
                notepad_tab = self.app.notebook.nametowidget(self.app.notebook.tabs()[i])

        if notepad_tab:
            text_widget = notepad_tab.winfo_children()[0]  # Supposons que le premier widget est Text
            return text_widget.get(1.0, "end-1c"), notepad_tab

        return None, None

    def provide_suggestions(self,app):
        """Fournit des suggestions de correction pour les fichiers Python."""
        content, notepad_tab = self.get_current_code()
        if content and self.is_python_file(self.app.current_notepad_file):
            suggestions = self.analyze_code(content)
            if suggestions:
                self.app.print_in_terminal("Suggestions :")
                for suggestion in suggestions:
                    self.app.print_in_terminal(f"- {suggestion}")
            else:
                self.app.print_in_terminal("Aucune suggestion de correction.")
        else:
            self.app.print_in_terminal("Ce n'est pas un fichier Python ou aucun fichier n'est ouvert.")

    def auto_complete(self,app, event=None,):
        """Fournit une auto-complétion basique pour Python."""
        content, notepad_tab = self.get_current_code()
        if content:
            # Récupère le mot partiellement tapé
            current_line = content.splitlines()[-1] if content.splitlines() else ""
            partial_word = current_line.split()[-1] if current_line.split() else ""

            # Fournit des suggestions basées sur les mots-clés Python
            matches = [kw for kw in self.python_keywords if kw.startswith(partial_word)]
            if len(matches) == 1:
                self.app.print_in_terminal(f"Auto-complétion : {matches[0]}")
                text_widget = notepad_tab.winfo_children()[0]
                text_widget.insert("insert", matches[0][len(partial_word):])  # Complète le mot
            elif len(matches) > 1:
                self.app.print_in_terminal(f"Suggestions : {', '.join(matches)}")
            else:
                self.app.print_in_terminal("Pas de suggestions.")
        return "break"

# Fonction d'enregistrement du plugin dans l'application Legion
def init_plugin(app):
    plugin = PythonHelperPlugin(app)
    app.print_in_terminal("Plugin PythonHelper activé.")
    app.commands.add_custom_command("/suggestions", plugin.provide_suggestions)
    app.commands.add_custom_command("/autocomplete", plugin.auto_complete)
