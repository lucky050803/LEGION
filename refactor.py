import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import time

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
        self.text_box = tk.Text(self.first_tab, height=20, width=80, bg="black", fg="green", insertbackground="white", font=("Courier", 12))
        self.text_box.pack(expand=True, fill=tk.BOTH)
        self.text_box.bind("<Return>", self.handle_command)

        self.text_box.config(state=tk.NORMAL)
        self.text_box.mark_set("insert", "end-1c")
        self.text_box.focus()

        # Démarrage de la boucle principale de l'application
        self.root.mainloop()

    # Fonction pour afficher des messages dans le terminal
    def print_in_terminal(self, output):
        self.text_box.insert(tk.END, f"\n{output}\n")
        self.text_box.see(tk.END)

    # Fonction pour définir le nom d'utilisateur
    def define_util(self, name):
        self.util = name
        self.util_setup = True
        self.print_in_terminal(f"Nom d'utilisateur : {self.util}")

    # Envoi de fichier
    import time  # Import pour ajouter des pauses entre les envois

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
    
    def save_file_np(self, text_widget):
        # Ouvre la boîte de dialogue pour sauvegarder le fichier
        file = filedialog.asksaveasfilename(defaultextension=".*", 
                                            filetypes=[("All Files", "*.*"), 
                                                    ("Text Files", "*.txt"), 
                                                    ("Python Files", "*.py"), 
                                                    ("HTML Files", "*.html"), 
                                                    ("Markdown Files", "*.md")])
        if file:
            # Récupère le contenu du bloc note et l'écrit dans le fichier choisi
            with open(file, "w") as file_to_save:
                file_to_save.write(text_widget.get(1.0, tk.END))  # Sauvegarde le contenu du widget Text
            
    def open_file(self, text_widget):
        file = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), 
                                                    ("Text Files", "*.txt"), 
                                                    ("Python Files", "*.py"), 
                                                    ("HTML Files", "*.html"), 
                                                    ("Markdown Files", "*.md")])
        if file:
            with open(file, "r") as file_to_open:
                content = file_to_open.read()  # Lire le contenu du fichier
                text_widget.delete(1.0, tk.END)  # Efface le contenu actuel
                text_widget.insert(tk.END, content)  # Insère le nouveau contenu
                
    def create_notepad_tab(self):
    # Crée un nouvel onglet
        notepad_tab = ttk.Frame(self.notebook)
        self.notebook.add(notepad_tab, text="Bloc Notes")  # Ajoute le nouvel onglet avec un titre "Bloc Notes"

    # Ajout d'un widget Text dans cet onglet
        text_box_notepad = tk.Text(notepad_tab, height=20, width=80, bg="black", fg="green", font=("Courier", 12))
        text_box_notepad.pack(expand=True, fill=tk.BOTH)

    # Ajout d'un bouton pour ouvrir un fichier
        open_button = tk.Button(notepad_tab, text="Ouvrir", command=lambda: self.open_file(text_box_notepad))
        open_button.pack(side=tk.LEFT, padx=5)

    # Ajout d'un bouton pour sauvegarder le fichier
        save_button = tk.Button(notepad_tab, text="Sauvegarder", command=lambda: self.save_file_np(text_box_notepad))
        save_button.pack(side=tk.LEFT, padx=5)
    
    # Fonction qui gère les commandes utilisateur
    def handle_command(self, event):
        command = self.text_box.get("end-1c linestart", "end-1c").strip()

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
        elif command == "/quit_conv":
            self.quit_conv()
        elif command == "/quit":
            self.root.quit()
        elif command == "/notepad" :
            self.create_notepad_tab()
        elif command == "/shutdown":
            self.shutdown_server()  # Appel de la nouvelle fonction pour fermer le serveur
        else:
            self.print_in_terminal(f"Commande non reconnue : {command}")
       
        return "break"


# Fonction principale pour démarrer l'application
def main():
    app = App()


if __name__ == "__main__":
    main()
