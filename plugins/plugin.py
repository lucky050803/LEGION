# Exemple de plugin Python (plugins/plugin_exemple.py)

def init_plugin(app):
    app.print_in_terminal("Le plugin exemple est chargé !")
    # Exemple d'interaction : ajouter une nouvelle commande
    app.commands.add_custom_command("/hello", say_hello)

def say_hello(app):
    app.print_in_terminal("Hello from the plugin!")

