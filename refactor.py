import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import time
import random
import json

# Configuration réseau
BROADCAST_PORT = 37020
LISTEN_PORT = 8080
BROADCAST_ADDRESS = '<broadcast>'


# Classe principale de l'application
class App:
    def __init__(self):
        self.util = "Utilisateur"
        self.util_setup = False
        self.connected = False
        self.client_socket = None
        self.server_socket = None
        self.notebook = None
        self.command_history = []  # Initialisation de la liste de l'historique des commandes
        self.history_index = -1 
        self.current_notepad_file = None
        self.init_ui()

    # Initialisation de l'interface utilisateur
    def init_ui(self):
        self.root = tk.Tk()
        self.root.title("LEGION")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Premier onglet (Terminal)
        self.first_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.first_tab, text="Terminal")

        # Configuration du widget Text pour le terminal
        self.text_box = tk.Text(self.first_tab, height=20, width=80, bg="black", fg="green", insertbackground="white", font=("Courier", 9))
        self.text_box.pack(expand=True, fill=tk.BOTH)
        self.text_box.bind("<Return>", self.handle_command)
        self.text_box.bind("<Up>", self.navigate_history_up)
        self.text_box.bind("<Down>", self.navigate_history_down)
        self.text_box.bind("<Tab>", self.autocomplete_command)
        self.text_box.config(state=tk.NORMAL)
        self.text_box.mark_set("insert", "end-1c")
        self.text_box.focus()
        self.show_legion_intro()
        # Démarrage de la boucle principale de l'application
        #self.print_in_terminal("-----------------------------------------")
        self.root.mainloop()

    def navigate_history_up(self, event):
        """Charge la commande précédente dans l'historique lorsque la flèche haut est pressée."""
        if self.command_history:
            # Si l'index est au début de l'historique, ne remonte pas plus haut
            if self.history_index == -1:
                self.history_index = len(self.command_history) - 1
            elif self.history_index > 0:
                self.history_index -= 1

            # Charger la commande correspondante dans la zone de texte
            self.load_command_from_history()

        return "break"  # Empêche le comportement par défaut de la flèche

    def navigate_history_down(self, event):
        """Charge la commande suivante dans l'historique lorsque la flèche bas est pressée."""
        if self.command_history and self.history_index != -1:
            # Avancer dans l'historique
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
            else:
                self.history_index = -1  # Revient au champ vide s'il n'y a plus de commandes

            # Charger la commande correspondante dans la zone de texte
            self.load_command_from_history()

        return "break"  # Empêche le comportement par défaut de la flèche

    def load_command_from_history(self):
        """Charge la commande dans la zone de texte en fonction de l'index de l'historique."""
        # Supprimer le texte actuel de la zone de texte
        self.text_box.delete("end-1c linestart", tk.END)

        # Charger la commande actuelle depuis l'historique
        if self.history_index != -1:
            self.text_box.insert(tk.END, self.command_history[self.history_index])


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
        self.text_box.config(bg="black", fg="green", font=("Courier", 14))  # Changer le style

        # Effet de pluie numérique inspiré de Matrix
        lines = [
            "LEGION SYSTEM BOOT",
            "Initializing ...",
            "Loading modules ...",
            "Running diagnostics ...",
            "LEGION SYSTEM READY"
        ]

        # Animation de l'effet Matrix
        for i in range(50):
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
        |                WELCOME TO                  |
        |                                            |
        |                  LEGION                    |
        |                                            |
        |                   ∅  0                     |
        |                   ____                     |
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


    def send_file(self):
        if not self.connected:
            self.print_in_terminal("Erreur : Vous n'êtes pas connecté à un serveur.")
            return

        # Sélection du fichier à envoyer
        file_path = filedialog.askopenfilename()
        if not file_path:
            self.print_in_terminal("Erreur : Aucun fichier sélectionné.")
            return

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        self.print_in_terminal(f"Envoi du fichier : {file_name} ({file_size} octets)")

        try:
            # Envoyer les métadonnées du fichier (nom et taille)
            self.client_socket.send(f"FILE:{file_name}:{file_size}".encode('utf-8'))
            
            with open(file_path, 'rb') as file:
                total_sent = 0  # Suivi de la progression de l'envoi

                while total_sent < file_size:
                    # Lire un bloc de données de 1024 octets
                    file_data = file.read(1024)
                    if not file_data:
                        break  # Fin du fichier

                    try:
                        # Envoyer les données lues
                        sent = self.client_socket.send(file_data)
                        total_sent += sent

                        # Affichage de la progression de l'envoi
                        self.print_in_terminal(f"Envoi en cours : {total_sent}/{file_size} octets envoyés")

                        # Ajouter une petite pause pour éviter la surcharge réseau
                        time.sleep(0.01)

                    except socket.error as e:
                        self.print_in_terminal(f"Erreur lors de l'envoi des données : {e}")
                        break

            # Vérification si tout le fichier a été envoyé
            if total_sent == file_size:
                self.print_in_terminal(f"Fichier {file_name} envoyé avec succès.")
            else:
                self.print_in_terminal(f"Erreur : Seuls {total_sent}/{file_size} octets ont été envoyés.")

        except socket.error as e:
            if e.errno == 10053:
                self.print_in_terminal("Erreur : La connexion a été fermée par l'hôte local.")
            else:
                self.print_in_terminal(f"Erreur lors de l'envoi du fichier : {e}")




    # Fonction pour choisir un répertoire de sauvegarde
    def choose_save_directory(self, file_name):
        directory = filedialog.askdirectory()  # Ouvre une boîte de dialogue pour choisir le répertoire
        if directory:
            return os.path.join(directory, file_name)  # Chemin personnalisé
        return file_name  # Chemin par défaut (dans le répertoire courant)
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

    # Fonction pour télécharger et sauvegarder le fichier
# Fonction pour télécharger et sauvegarder le fichier
    def save_file(self, conn, save_path, file_size):
        try:
            with open(save_path, 'wb') as file:
                received_size = 0
                while received_size < file_size:
                    try:
                        # Vérification si le socket est encore valide avant de recevoir des données
                        if conn.fileno() == -1:
                            self.print_in_terminal(f"Le socket a été fermé avant la réception complète.")
                            break
                        
                        file_data = conn.recv(1024)
                        
                        # Si aucun fichier reçu, on stoppe
                        if not file_data:
                            break
                        
                        file.write(file_data)
                        received_size += len(file_data)
                    
                    except socket.error as e:
                        self.print_in_terminal(f"Erreur lors de la réception des données : {e}")
                        break

            if received_size == file_size:
                self.print_in_terminal(f"Fichier {save_path} reçu avec succès.")
            else:
                self.print_in_terminal(f"Le fichier n'a pas été complètement reçu. Taille reçue : {received_size}/{file_size}")
            
        except Exception as e:
            self.print_in_terminal(f"Erreur lors du téléchargement du fichier : {e}")


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

        while True:
            conn, addr = self.server_socket.accept()
            self.print_in_terminal(f"Nouvelle connexion depuis {addr}")

            threading.Thread(target=self.handle_client_connection, args=(conn, addr)).start()

            # Réception des métadonnées du fichier
            metadata = conn.recv(1024).decode('utf-8')
            if metadata.startswith("FILE:"):
                _, file_name, file_size = metadata.split(":")
                file_size = int(file_size)
                self.print_in_terminal(f"Réception proposée : {file_name} ({file_size} octets)")

                # Demander à l'utilisateur s'il veut accepter le fichier
                self.print_in_terminal(f"Acceptez-vous la réception de {file_name} ? (y/n) : ")

                def confirm_reception(event):
                    command = self.text_box.get("end-1c linestart", "end-1c").strip()
                    if command.lower() == 'y':
                        self.print_in_terminal("Choisissez un chemin de sauvegarde ou utilisez le chemin par défaut.")
                        save_path = self.choose_save_directory(file_name)
                        self.save_file(conn, save_path, file_size)
                    else:
                        self.print_in_terminal("Réception annulée.")
                    self.text_box.bind("<Return>", self.handle_command)

                self.text_box.bind("<Return>", confirm_reception)
            else:
                self.print_in_terminal("Aucune demande de fichier détectée.")

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
                
    def create_notepad_tab(self):
        """Crée un nouvel onglet Bloc Notes avec des boutons pour ouvrir, sauvegarder et fermer l'onglet."""
        # Créer un nouvel onglet
        notepad_tab = ttk.Frame(self.notebook)
        self.notebook.add(notepad_tab, text="Bloc Notes")  # Ajoute l'onglet au notebook

        # Ajout d'un widget Text dans cet onglet
        text_box_notepad = tk.Text(notepad_tab, height=20, width=80, bg="black", fg="green", font=("Courier", 12))
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
        self.print_in_terminal("Terminal nettoyé.")



    def autocomplete_command(self, event=None):
    # Empêcher l'insertion du caractère tab
          # Supprime le caractère Tab inséré automatiquement

        current_input = self.text_box.get("end-1c linestart", "end-1c").strip()
        #if event:
        #    self.text_box.delete("insert-1c")
        # Liste des commandes disponibles
        available_commands = ["/user", "/connect", "/serv", "/clear", "/histo", "/quit", "/enva", "/envf", "/shutdown", "/macros", "/quit_conv"]

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
        
    def handle_command(self, event):
        command = self.text_box.get("end-1c linestart", "end-1c").strip()
        self.save_command_history(command)
        
        self.return_command(command)
        return "break"
        
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
        elif command == "/envf":
            self.send_file()
            self.print_in_terminal("\n")
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
            self.print_in_terminal("\n")
        elif command == "/run_script":
            self.run_script()
            self.print_in_terminal("\n")
        elif command == "/histo":
            self.show_command_history()
            self.print_in_terminal("\n")
        elif command == "/macros":
            self.run_macro()
        else:
            self.print_in_terminal(f"Commande non reconnue : {command}")
       


# Fonction principale pour démarrer l'application
def main():
    app = App()

if __name__ == "__main__":
    main()
