# plugins/plugin_game.py

import random

def init_plugin(app):
    app.print_in_terminal("Le plugin de jeu est chargé !")
    # Ajouter une commande personnalisée pour démarrer le jeu
    app.commands.add_custom_command("/play", start_game)

def start_game(app):
    app.print_in_terminal("Bienvenue dans le jeu de devinette !")
    number_to_guess = random.randint(1, 100)
    attempts = 0

    def guess():
        nonlocal attempts
        app.print_in_terminal("Devinez un nombre entre 1 et 100 : ")
        user_input = app.handle_command() 
        try:
            guess = int(user_input)
            attempts += 1
            if guess < number_to_guess:
                app.print_in_terminal("C'est plus grand !")
                guess()
            elif guess > number_to_guess:
                app.print_in_terminal("C'est plus petit !")
                guess()
            else:
                app.print_in_terminal(f"Bravo ! Vous avez trouvé en {attempts} essais.")
        except ValueError:
            app.print_in_terminal("Veuillez entrer un nombre valide.")
            guess()

    guess()
