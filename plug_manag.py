
import os
import importlib.util


class PluginManager:
    def __init__(self, app):
        self.app = app
        self.plugins_directory = "plugins"  # Dossier où se trouvent les plugins

    def load_plugins(self):
        """Charge et exécute tous les plugins présents dans le répertoire des plugins."""
        if not os.path.exists(self.plugins_directory):
            os.makedirs(self.plugins_directory)  # Crée le dossier s'il n'existe pas encore

        # Parcourt tous les fichiers .py dans le dossier des plugins
        for filename in os.listdir(self.plugins_directory):
            if filename.endswith(".py"):
                self.load_plugin(filename)

    def load_plugin(self, filename):
        """Charge un plugin Python à partir d'un fichier."""
        plugin_path = os.path.join(self.plugins_directory, filename)

        # Charger dynamiquement le module
        spec = importlib.util.spec_from_file_location(filename[:-3], plugin_path)
        plugin_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(plugin_module)
            self.app.print_in_terminal(f"Plugin '{filename}' chargé avec succès.")
            # Appel d'une fonction d'initialisation dans le plugin, si elle existe
            if hasattr(plugin_module, "init_plugin"):
                plugin_module.init_plugin(self.app)
        except Exception as e:
            self.app.print_in_terminal(f"Erreur lors du chargement du plugin '{filename}': {e}")
# Classe principale de l'application