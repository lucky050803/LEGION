import tkinter as tk
from tkinter import ttk, filedialog
import socket
import threading
import os

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
    def send_file(self):
        if not self.connected:
            self.print_in_terminal("Erreur : Vous n'êtes pas connecté à un serveur.")
            return
        
        # Sélection du fichier à envoyer
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            self.print_in_terminal(f"Envoi du fichier : {file_name} ({file_size} octets)")
            
            # Envoyer les métadonnées du fichier
            try:
                self.client_socket.send(f"FILE:{file_name}:{file_size}".encode('utf-8'))
                with open(file_path, 'rb') as file:
                    # Envoi du fichier par paquets de 1024 octets
                    while True:
                        file_data = file.read(1024)
                        if not file_data:
                            break
                        self.client_socket.send(file_data)
                self.print_in_terminal(f"Fichier {file_name} envoyé avec succès.")
            except Exception as e:
                self.print_in_terminal(f"Erreur lors de l'envoi du fichier : {e}")

    # Fonction pour recevoir des fichiers sur le serveur
    def receive_file(self, conn):
        try:
            # Réception des métadonnées du fichier
            metadata = conn.recv(1024).decode('utf-8')
            if metadata.startswith("FILE:"):
                _, file_name, file_size = metadata.split(":")
                file_size = int(file_size)
                self.print_in_terminal(f"Réception du fichier : {file_name} ({file_size} octets)")

                # Réception du fichier
                with open(file_name, 'wb') as file:
                    received_size = 0
                    while received_size < file_size:
                        file_data = conn.recv(1024)
                        if not file_data:
                            break
                        file.write(file_data)
                        received_size += len(file_data)
                self.print_in_terminal(f"Fichier {file_name} reçu avec succès.")
        except Exception as e:
            self.print_in_terminal(f"Erreur lors de la réception du fichier : {e}")
            
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
    
    # Envoi de message au serveur
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
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', LISTEN_PORT))
        server_socket.listen(1)
        ip_address = self.get_local_ip()
        self.print_in_terminal(f"Serveur démarré sur l'adresse IP {ip_address} et le port {LISTEN_PORT}")
        self.print_in_terminal("En attente d'une connexion...")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_client_connection, args=(conn, addr)).start()

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
            self.send_msg(command)
            self.print_in_terminal("\n")
        elif command == ("/envf"):
            self.send_file()
        elif command == "/quit":
            self.quit_conv()
            self.root.quit()
        else:
            self.print_in_terminal(f"Commande non reconnue : {command}")
            
        return "break"

# Fonction principale pour démarrer l'application
def main():
    app = App()

if __name__ == "__main__":
    main()
