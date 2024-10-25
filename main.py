import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import time
import random
import importlib.util
from FileE import *
from plug_manag import *
from Commands_m import *

LISTEN_PORT = 8080

class App:
    def __init__(self):
        self.util = "Utilisateur"
        self.util_setup = False
        self.connected = False
        
        self.client_socket = None
        self.server_socket = None
        self.command_history = []  # Initialisation de la liste de l'historique des commandes
        self.history_index = -1 
        self.current_notepad_file = None
        self.notebook = None
        self.left_frame = None
        self.file_explorer = FileExplorer(self)
        self.plugin_manager = PluginManager(self)
        self.custom_commands = {}

        self.commands = CommandsModule(self) 

        self.root = tk.Tk()
        self.root.title("L.E.G.I.O.N")

        # Création de la frame principale avec une disposition en deux colonnes
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame pour l'arborescence et les boutons (colonne de gauche)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Arborescence des fichiers
        self.file_tree = ttk.Treeview(left_frame)
        self.file_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des boutons (en dessous de l'arborescence)
        open_button = tk.Button(left_frame, text="Ouvrir Explorateur", command=self.file_explorer.open_directory)
        open_button.pack(fill=tk.X, padx=5, pady=5)

        # Autres boutons (ajoute des boutons supplémentaires si nécessaire)
        #save_button = tk.Button(left_frame, text="Sauvegarder", command=lambda: self.save_file_np(self.text_box))
        #save_button.pack(fill=tk.X, padx=5, pady=5)

        # Frame pour le terminal (colonne de droite)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Ajout du notebook dans le frame de droite (qui contient le terminal)
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(expand=True, fill=tk.BOTH)


        self.animation_label = tk.Label(self.left_frame, text="", font=("Courier", 12), fg="black")
        self.animation_label.pack(padx=5, pady=5)
        
        # Premier onglet (Terminal)
        self.first_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.first_tab, text="Terminal")

        # Configuration du widget Text pour le terminal
        self.text_box = tk.Text(self.first_tab, height=20, width=80, bg="black", fg="green", insertbackground="green", font=("Courier", 9))
        self.text_box.pack(expand=True, fill=tk.BOTH)
        self.text_box.bind("<Return>", self.handle_command)
        self.text_box.bind("<Tab>", self.autocomplete_command)
        self.text_box.config(state=tk.NORMAL)
        self.text_box.mark_set("insert", "end-1c")
        self.text_box.focus()

        # Afficher l'intro dans le terminal
        self.show_legion_intro()
        self.plugin_manager.load_plugins()
        # Démarrage de la boucle principale de l'application
        self.root.mainloop()

    def add_custom_command(self, command_name, callback):
        """Ajoute une nouvelle commande personnalisée via un plugin."""
        self.custom_commands[command_name] = callback
            
    def run_plugin(self):
        """Exécute un plugin donné par son nom."""
        #plugin_file = f"{plugin_name}.py"
        plugin_file = filedialog.askopenfilename(
            title="Sélectionner un script Python",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        plugin_path = os.path.join(self.plugin_manager.plugins_directory, plugin_file)

        if os.path.exists(plugin_path):
            self.plugin_manager.load_plugin(plugin_file)  # Charger le plugin spécifié
        else:
            self.print_in_terminal(f"Plugin non trouvé.")

    def save_command_history(self, command):
        """Enregistre la commande dans l'historique."""
        if command:  # N'ajoute pas de commandes vides
            self.command_history.append(command)
            self.history_index = -1  # Réinitialise l'index après chaque nouvelle commande

    def show_command_history(self):
        """Affiche l'historique des commandes."""
        self.print_in_terminal("Historique des commandes :")
        for idx, cmd in enumerate(self.command_history, 1):
            self.print_in_terminal(f"{idx}: {cmd}")

    def show_legion_intro(self):

        # Configuration de l'écran de présentation
        self.text_box.config(state=tk.NORMAL)  # Permettre l'édition du texte
        self.text_box.delete(1.0, tk.END)  # Effacer tout le contenu de la zone de texte
        self.text_box.config(bg="black", fg="green", font=("Courier", 9))  # Changer le style

        # Effet de pluie numérique inspiré de Matrix
        lines = [
            "DÉMARRAGE DU SYSTÈME L.E.G.I.O.N.",
            "Initialisation ...",
            "Chargement des modules ...",
            "Exécution des diagnostics ...",
            "SYSTÈME L.E.G.I.O.N. PRÊT"
        ]


        # Animation de l'effet Matrix
        for i in range(20):
            random_line = ''.join(random.choice("01") for _ in range(80))  # Générer une ligne de "pluie"
            self.text_box.insert(tk.END, random_line + "\n")
            self.text_box.see(tk.END)
            self.text_box.update()  # Mettre à jour l'affichage
            time.sleep(0.05)  # Ajouter un délai pour l'effet d'animation

        # Affichage des messages système
        for line in lines:
            self.text_box.insert(tk.END, "\n" + line)
            self.text_box.see(tk.END)
            self.text_box.update()
            time.sleep(1)  # Pause entre les messages

        # Affichage final du titre LEGION
        final_message = """
        ==============================================
        |             |L.E.G.I.O.N. v1.0|            |
        ==============================================
        """
        self.text_box.insert(tk.END, final_message)
        self.text_box.see(tk.END)
        self.text_box.update()

        time.sleep(3)  # Pause avant de permettre à l'utilisateur de continuer
        self.text_box.delete(1.0, tk.END)  # Effacer l'écran d'intro pour revenir à l'interface normale
        
        self.text_box.see(tk.END)

    # Fonction pour afficher des messages dans le terminal
    def print_in_terminal(self, output):
        self.text_box.insert(tk.END, f"\n{output}\n")
        self.text_box.see(tk.END)

    # Fonction pour définir le nom d'utilisateur
    def define_util(self, name):
        self.util = name
        self.util_setup = True
        self.print_in_terminal(f"Nom d'utilisateur : {self.util}")

    # Fonction pour fermer le serveur proprement
    def shutdown_server(self):
        if self.server_socket:
            try:
                self.print_in_terminal("Fermeture du serveur...")
                self.server_socket.close()  # Fermer le socket du serveur
                self.server_socket = None
                self.print_in_terminal("Le serveur a été fermé avec succès.")
            except Exception as e:
                self.print_in_terminal(f"Erreur lors de la fermeture du serveur : {e}")
        else:
            self.print_in_terminal("Erreur : Aucun serveur n'est actuellement en cours d'exécution.")

    # Fonction pour se connecter à un serveur
    def client_program(self, server_address, server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((server_address, server_port))
            self.print_in_terminal("En attente de l'acceptation du serveur...")
            message = self.client_socket.recv(1024).decode('utf-8')
            if message == "Connexion acceptée":
                self.connected = True
                self.print_in_terminal("Connexion acceptée par le serveur.")
            elif message == "Connexion refusée":
                self.print_in_terminal("Connexion refusée par le serveur.")
                self.client_socket.close()
        except Exception as e:
            self.print_in_terminal(f"Erreur de connexion : {e}")

    # Fonction pour envoyer un message au serveur
    def send_msg(self, msg):
        if self.client_socket and self.connected:
            try:
                self.client_socket.send(msg.encode('utf-8'))
                self.print_in_terminal(f"Message envoyé : {msg}")
            except BrokenPipeError:
                self.print_in_terminal("Erreur : La connexion au serveur est perdue.")
            except socket.error as e:
                self.print_in_terminal(f"Erreur lors de l'envoi du message : {e}")
        else:
            self.print_in_terminal("Erreur : Vous n'êtes pas connecté à un serveur.")
    
    def check_connection_status(self):
        if self.client_socket is None:
            self.print_in_terminal("Erreur : Aucun socket n'a été initialisé.")
            return False

        try:
            # Tentative d'envoi de données vides pour vérifier si le socket est actif
            self.client_socket.send(b'')
            self.print_in_terminal("Le client est toujours connecté.")
            return True

        except socket.error as e:
            # Si une exception se produit, cela signifie que le socket n'est plus connecté
            self.print_in_terminal(f"Erreur de connexion : {e}. Le socket est déconnecté.")
            self.client_socket.close()  # Fermer le socket pour libérer les ressources
            self.client_socket = None  # Réinitialiser le socket
            self.connected = False  # Mettre à jour le statut de connexion
            return False

    # Fonction pour arrêter la conversation
    def quit_conv(self):
        if self.client_socket:
            self.client_socket.close()
            self.connected = False
            self.print_in_terminal("Connexion fermée.")

    # Fonction qui gère les connexions clients
    def handle_client_connection(self, conn, addr):
        self.print_in_terminal(f"Connexion reçue de : {addr}")
        self.print_in_terminal("Accepter la connexion ? (y/n) : ")

        def accept_connection(event):
            command = self.text_box.get("end-1c linestart", "end-1c").strip()
            if command.lower() == 'y':
                conn.send("Connexion acceptée".encode('utf-8'))
                self.print_in_terminal("Connexion acceptée. Vous êtes maintenant connectés.")
            else:
                conn.send("Connexion refusée".encode('utf-8'))
                conn.close()
                self.print_in_terminal("Connexion refusée.")
            self.text_box.bind("<Return>", self.handle_command)

        self.text_box.bind("<Return>", accept_connection)

        while True:
            try:
                print("oui")
                message = conn.recv(1024).decode('utf-8')
                if not message:
                    break
                self.print_in_terminal(f"Message reçu : {message}")
            except:
                break
        conn.close()
            
    # Fonction pour démarrer le serveur
    def server_program(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', LISTEN_PORT))
        self.server_socket.listen(1)
        ip_address = self.get_local_ip()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.print_in_terminal(f"Serveur démarré sur l'adresse IP {ip_address} et le port {LISTEN_PORT}")
        self.print_in_terminal("En attente d'une connexion...")

        while self.server_socket != None:
            if self.server_socket != None :
                conn, addr = self.server_socket.accept()
                self.print_in_terminal(f"Nouvelle connexion depuis {addr}")

                threading.Thread(target=self.handle_client_connection, args=(conn, addr), daemon=True).start()
            
            # Réception des métadonnées du fichier
           
    # Fonction pour récupérer l'adresse IP locale
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    
    def save_file_np(self, text_box):
        """Sauvegarde le fichier actuellement ouvert, ou demande où sauvegarder si aucun fichier n'est encore ouvert."""
        if self.current_notepad_file:
            # Sauvegarder directement sur le fichier ouvert
            with open(self.current_notepad_file, 'w') as file:
                file.write(text_box.get(1.0, tk.END))  # Sauvegarder le contenu du widget Text
            self.print_in_terminal(f"Fichier sauvegardé : {self.current_notepad_file}")
        else:
            # Si aucun fichier n'est ouvert, demander où sauvegarder
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(text_box.get(1.0, tk.END))  # Sauvegarder le contenu du widget Text
                self.current_notepad_file = file_path  # Mémoriser le chemin du fichier ouvert
                self.print_in_terminal(f"Fichier sauvegardé : {file_path}")
            else:
                self.print_in_terminal("Sauvegarde annulée.")
            
    def open_file(self, text_box):
        """Ouvre un fichier et charge son contenu dans la zone de texte Bloc Notes."""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, content)
            self.current_notepad_file = file_path  # Mémoriser le chemin du fichier ouvert
            self.print_in_terminal(f"Fichier ouvert : {file_path}")
        else:
            self.print_in_terminal("Aucun fichier sélectionné.")

    def open_file_in_prj(self, file_path, text_box):
        """Ouvre un fichier et charge son contenu dans la zone de texte Bloc Notes."""
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, content)
            self.current_notepad_file = file_path  # Mémoriser le chemin du fichier ouvert
            self.print_in_terminal(f"Fichier ouvert : {file_path}")
        else:
            self.print_in_terminal("Aucun fichier sélectionné.")
             
    def create_notepad_tab(self):
        """Crée un nouvel onglet Bloc Notes avec des boutons pour ouvrir, sauvegarder et fermer l'onglet."""
        # Créer un nouvel onglet
        notepad_tab = ttk.Frame(self.notebook)
        self.notebook.add(notepad_tab, text="Bloc Notes")  # Ajoute l'onglet au notebook

        # Ajout d'un widget Text dans cet onglet
        text_box_notepad = tk.Text(notepad_tab, height=20, width=80, bg="black", fg="green",insertbackground="green", font=("Courier", 9))
        text_box_notepad.pack(expand=True, fill=tk.BOTH)

        # Frame pour les boutons (en bas de l'onglet)
        button_frame = tk.Frame(notepad_tab)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Bouton pour ouvrir un fichier
        open_button = tk.Button(button_frame, text="Ouvrir", command=lambda: self.open_file(text_box_notepad), bg="black", fg="green")
        open_button.pack(side=tk.LEFT, padx=5)

        # Bouton pour sauvegarder le fichier
        save_button = tk.Button(button_frame, text="Sauvegarder", command=lambda: self.save_file_np(text_box_notepad), bg="black", fg="green")
        save_button.pack(side=tk.LEFT, padx=5)

        # Bouton pour fermer l'onglet
        close_button = tk.Button(button_frame, text="Fermer", command=lambda: self.close_notepad_tab(notepad_tab), bg="black", fg="green")
        close_button.pack(side=tk.RIGHT, padx=5)
        
        text_box_notepad.bind('<Control-s>', lambda event: self.save_file_np(text_box_notepad))
        
    def create_project_tab(self, file_path):
        """Crée un nouvel onglet Bloc Notes avec des boutons pour ouvrir, sauvegarder et fermer l'onglet."""
        # Créer un nouvel onglet
        notepad_tab = ttk.Frame(self.notebook)
        self.notebook.add(notepad_tab, text="Projet")  # Ajoute l'onglet au notebook

        # Ajout d'un widget Text dans cet onglet
        text_box_notepad = tk.Text(notepad_tab, height=20, width=80, bg="black", fg="green",insertbackground="green", font=("Courier", 9))
        text_box_notepad.pack(expand=True, fill=tk.BOTH)

        # Frame pour les boutons (en bas de l'onglet)
        button_frame = tk.Frame(notepad_tab)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Bouton pour sauvegarder le fichier
        save_button = tk.Button(button_frame, text="Sauvegarder", command=lambda: self.save_file_np(text_box_notepad), bg="black", fg="green")
        save_button.pack(side=tk.LEFT, padx=5)

        # Bouton pour fermer l'onglet
        close_button = tk.Button(button_frame, text="Fermer", command=lambda: self.close_notepad_tab(notepad_tab), bg="black", fg="green")
        close_button.pack(side=tk.RIGHT, padx=5)
        
        text_box_notepad.bind('<Control-s>', lambda event: self.save_file_np(text_box_notepad))
        self.open_file_in_prj(file_path, text_box_notepad)
        
    def close_notepad_tab(self, tab):
        """Ferme l'onglet Bloc Notes."""
        try:
            tab_index = self.notebook.index(tab)
            self.notebook.forget(tab_index)  # Supprime l'onglet via son index
        except Exception as e:
            self.print_in_terminal(f"Erreur lors de la fermeture de l'onglet : {e}")

    def clear(self):
        
        self.text_box.config(state=tk.NORMAL)  # Permettre l'édition du texte
        self.text_box.delete(1.0, tk.END)  # Supprimer tout le texte de la zone
        # Réinsérer le prompt initial si nécessaire
        self.text_box.see(tk.END)  # Assurer que la vue défile jusqu'à la fin

    def autocomplete_command(self, event=None):
    # Empêcher l'insertion du caractère tab
          # Supprime le caractère Tab inséré automatiquement

        current_input = self.text_box.get("end-1c linestart", "end-1c").strip()
        #if event:
        #    self.text_box.delete("insert-1c")
        # Liste des commandes disponibles
        
        available_commands = ["/user", "/connect", "/serv", "/clear", "/histo", "/quit", "/enva", "/shutdown", "/quit_conv","/netw","/run_script","/run_plugin","/histo","/macros","/show_custom","/open_prj"]
        # Chercher une correspondance avec les commandes disponibles
        matches = [cmd for cmd in available_commands if cmd.startswith(current_input)]
        
        if len(matches) == 1:  # Une seule correspondance trouvée
            self.text_box.delete("insert linestart", "insert")  # Supprimer la partie en cours de saisie
            self.text_box.insert(tk.INSERT, matches[0])
        elif len(matches) > 1:  # Plusieurs correspondances
            self.print_in_terminal("Suggestions : " + ", ".join(matches))

        return "break"  # Empêcher le comportement par défaut de la touche Tab

    def run_script(self):
        """Demande à l'utilisateur de sélectionner un script Python à exécuter, puis l'exécute."""
        # Demander à l'utilisateur de sélectionner un fichier .py
        script_path = filedialog.askopenfilename(
            title="Sélectionner un script Python",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        
        if script_path:
            try:
                # Lire le contenu du fichier script Python
                with open(script_path, "r") as script_file:
                    script_code = script_file.read()

                # Exécuter le script Python
                exec(script_code)
                self.print_in_terminal(f"Script '{script_path}' exécuté avec succès.")
            
            except Exception as e:
                self.print_in_terminal(f"Erreur dans le script : {e}")
        else:
            self.print_in_terminal("Aucun script sélectionné.")
            
    def run_macro(self):
        """Exécute une suite de commandes depuis un fichier de macros avec l'extension .kfk."""
        # Demander à l'utilisateur de sélectionner un fichier .kfk
        macro_path = filedialog.askopenfilename(
            title="Sélectionner un fichier de macros",
            filetypes=[("Macro Files", "*.kfk"), ("All Files", "*.*")]
        )

        if macro_path:
            try:
                # Lire le contenu du fichier de macros .kfk
                with open(macro_path, "r") as macro_file:
                    commands = macro_file.readlines()

                # Exécuter chaque commande dans le fichier
                self.print_in_terminal(f"Exécution des macros depuis '{macro_path}'...")
                for command in commands:
                    command = command.strip()  # Supprimer les espaces et les sauts de ligne
                    if command:
                        self.print_in_terminal(f"Exécution de la commande : {command}")
                        self.handle_command_direct(command)  # Appeler la méthode pour exécuter la commande

                self.print_in_terminal(f"Macros terminées avec succès depuis '{macro_path}'.")

            except Exception as e:
                self.print_in_terminal(f"Erreur lors de l'exécution des macros : {e}")
        else:
            self.print_in_terminal("Aucun fichier de macros sélectionné.")

    def handle_command_direct(self, command):
        """Gère directement l'exécution des commandes depuis un fichier de macros."""
        # Ici, nous passons directement la commande au handler des commandes
        self.save_command_history(command)  # Sauvegarder la commande dans l'historique
        # Tu peux personnaliser ici l'exécution des commandes selon les besoins
        self.return_command(command)
        # Fonction qui gère les commandes utilisateur
        
    def handle_command(self, event = None):
        command = self.text_box.get("end-1c linestart", "end-1c").strip()
        self.save_command_history(command)
        if ("/") in command :
            self.return_command(command)
            return "break"
        else : 
            print(command)
            return command
               
    def return_command(self,command):
        if command.startswith("/user "):
            name = command.split("/user ")[1].strip()
            self.define_util(name)
        elif command.startswith("/connect "):
            address_info = command.split("/connect ")[1].split(":")
            ip_address = address_info[0]
            port = int(address_info[1].replace("/", ""))
            threading.Thread(target=self.client_program, args=(ip_address, port), daemon=True).start()
        elif command == "/serv":
            threading.Thread(target=self.server_program, daemon=True).start()
            self.print_in_terminal("Serveur lancé...")
        elif command.startswith("/enva "):
            self.send_msg(command.split("/enva ")[1])
        elif command == "/quit_conv":
            self.quit_conv()
            self.print_in_terminal("\n")
        elif command == "/quit":
            self.root.quit()
            self.print_in_terminal("\n")
        elif command == "/notepad" :
            self.create_notepad_tab()
            self.print_in_terminal("\n")
        elif command == "/shutdown":
            self.shutdown_server()  # Appel de la nouvelle fonction pour fermer le serveur
            self.print_in_terminal("\n")
        elif command == "/netw":
            self.check_connection_status()
            self.print_in_terminal("\n")
        elif command == "/clear":
            self.clear()
        elif command == "/run_script":
            self.run_script()
            self.print_in_terminal("\n")
        elif command == "/histo":
            self.show_command_history()
            self.print_in_terminal("\n")
        elif command == "/macros":
            self.run_macro()
        elif command == "/run_plugin":
            self.run_plugin()
        elif command in self.custom_commands:
            self.custom_commands[command](self)
        elif command == "/show_custom":
            self.commands.show_custom_commands()
        elif command == "/open_prj":
            self.file_explorer.open_directory()
        else:
            self.print_in_terminal(f"Commande non reconnue : {command}")
       
       # Fonction principale pour démarrer l'application

def main():
    app = App()

if __name__ == "__main__":
    main()
