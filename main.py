import tkinter as tk
from tkinter import ttk, filedialog

import socket
import threading
import socket

BROADCAST_PORT = 37020  
LISTEN_PORT = 8080  
BROADCAST_ADDRESS = '<broadcast>'

def broadcast_status(ip_address, port):
    message = f"Utilisateur connecté à {ip_address}:{port}"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode('utf-8'), (BROADCAST_ADDRESS, BROADCAST_PORT))
        print_in_terminal(f"Diffusion : {message}")

# Fonction pour écouter les diffusions et notifier les utilisateurs de nouvelles connexions
def listen_for_broadcast():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', BROADCAST_PORT))
        print_in_terminal("En attente de notifications de connexion sur le réseau...")

        while True:
            data, addr = sock.recvfrom(1024)
            print_in_terminal(f"Notification de connexion reçue : {data.decode('utf-8')}")
            
            
# Fonction qui se connecte à un serveur
def client_program(server_address,server_port):
    global connected
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création du socket

    # Tentative de connexion au serveur
    try:
        client_socket.connect((server_address, server_port))
        print_in_terminal("En attente de l'acceptation du serveur...")

        # Recevoir la réponse du serveur (acceptation ou refus)
        message = client_socket.recv(1024).decode('utf-8')
        if message == "Connexion acceptée":
            connected = 1
            print_in_terminal("Connexion acceptée par le serveur.")
        elif message == "Connexion refusée":
            print_in_terminal("Connexion refusée par le serveur.")
            client_socket.close()
            return
    except:
        print_in_terminal("\nCONNECTION ERROR\n")
        
        
        
def send_msg(msg):
    try:
        # Encodage du message avant l'envoi
        encoded_msg = msg.encode('utf-8')
        client_socket.send(encoded_msg)  # Envoi du message au serveur
        print_in_terminal(f"Message envoyé : {msg}")
    except BrokenPipeError:
        print_in_terminal("Erreur : La connexion au serveur est perdue.")
    except socket.error as e:
        print_in_terminal(f"Erreur lors de l'envoi du message : {e}")

    

def quit_conv():
    pass

def print_in_terminal(output):
    text_box.insert(tk.END, f"\n{output}\n")
    text_box.see(tk.END)
    
    
    
def handle_client_connection(conn, addr):
    print_in_terminal(f"Connexion reçue de : {addr}")
    # Demande d'acceptation de la connexion via l'interface
    print_in_terminal("Accepter la connexion ? (y/n) : ")

    # Attend la commande de l'utilisateur pour accepter ou refuser
    def accept_connection():
        command = text_box.get("end-1c linestart", "end-1c").strip()  # Récupère la dernière ligne de commande
        if command.lower() == 'y':
            conn.send("Connexion acceptée".encode('utf-8'))  # Encode la chaîne en UTF-8
            print_in_terminal("Connexion acceptée. Vous êtes maintenant connectés.")
        else:
            conn.send("Connexion refusée".encode('utf-8'))  # Encode la chaîne en UTF-8
            conn.close()
            print_in_terminal("Connexion refusée.")
        text_box.bind("<Return>", handle_command)  # Réactive l'écoute des commandes utilisateur

    text_box.bind("<Return>", lambda event: accept_connection())

    while True:
        # Attendre des messages du client
        message = conn.recv(1024).decode('utf-8')
        if not message:
            break
        print_in_terminal(f"Message reçu: {message}")
        # Répondre au client
        response = input("Votre message : ")
        conn.send(response.encode('utf-8'))

    conn.close()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # On se connecte à un serveur pour récupérer l'IP locale (Google Public DNS dans cet exemple)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # En cas d'erreur, retourne l'IP localhost
    finally:
        s.close()
    return ip

# Fonction qui attend les connexions du client et les accepte
def server_program():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création du socket
    server_socket.bind(('0.0.0.0', LISTEN_PORT))  # Le serveur écoute sur toutes les interfaces sur le port 8080
    server_socket.listen(1)  # Le serveur écoute pour une connexion
    ip_address = get_local_ip()
    port = server_socket.getsockname()[1]
    print_in_terminal(f"Serveur démarré sur l'adresse IP {ip_address} et le port {port}")
    print_in_terminal("En attente d'une connexion...")

    while True:
        # Accepter la connexion d'un client
        conn, addr = server_socket.accept()
        broadcast_status(ip_address,port)
        threading.Thread(target=handle_client_connection, args=(conn, addr)).start()  # Démarre un thread pour gérer chaque client


# Fonction de traitement des commandes
def handle_command(event):
    rtcommand = text_box.get("end-1c linestart", "end-1c").strip()  # Récupère la dernière ligne de commande
    command = rtcommand.strip()  # Appelle la fonction de traitement des commandes
    
    if "/exit/" in command:
        output = "EXITING"
        text_box.insert(tk.END, f"\n{output}\n")
        root.quit()  # Quitte l'application si la commande est "exit"
    elif "/help/" in command:
        output = "Implemented commands : /help/, /TAB/, /exit/ "
        text_box.insert(tk.END, f"\n{output}\n$ ")  
    elif "/TAB/" in command:
        output = "creating second tab..."
        text_box.insert(tk.END, f"\n{output}\n$ ")
        create_second_tab(notebook)
    elif "/notepad/" in command:
        output = "creating notepadtab tab..."
        text_box.insert(tk.END, f"\n{output}\n$ ")
        create_notepad_tab(notebook)
    elif command.startswith("/connect"):
            # Extraire l'adresse IP et le port
            address_info = command.split("/connect ")[1].split(":")
            ip_address = address_info[0]
            port = int(address_info[1].replace("/", ""))
            threading.Thread(target=client_program, args=(ip_address, port), daemon=True).start()
            

            
    elif "/server/" in command:
        output = "lauching server"
        text_box.insert(tk.END, f"\n{output}\n$ ")
        #threading.Thread(target=server_program, args=('notebook', notebook)) 
        #server_program()
        threading.Thread(target=server_program, daemon=True).start()
    elif "/sendto/" in command:
        send_msg(command)
        
        
         
            
    else :
        output = "unknown command"
        text_box.insert(tk.END, f"\n{output}\n$ ")
    
    text_box.see(tk.END)  # Fait défiler le texte jusqu'à la fin pour voir la nouvelle ligne
    return "break"  # Empêche l'insertion d'un retour à la ligne par défaut

def save_file(text_widget):
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
            
def open_file(text_widget):
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

# Fonction pour créer un nouvel onglet de type bloc-notes
def create_notepad_tab(notebook):
    # Crée un nouvel onglet
    notepad_tab = ttk.Frame(notebook)
    notebook.add(notepad_tab, text="Bloc Notes")  # Ajoute le nouvel onglet avec un titre "Bloc Notes"

    # Ajout d'un widget Text dans cet onglet
    text_box_notepad = tk.Text(notepad_tab, height=20, width=80, bg="black", fg="green", font=("Courier", 12))
    text_box_notepad.pack(expand=True, fill=tk.BOTH)

    # Ajout d'un bouton pour ouvrir un fichier
    open_button = tk.Button(notepad_tab, text="Ouvrir", command=lambda: open_file(text_box_notepad))
    open_button.pack(side=tk.LEFT, padx=5)

    # Ajout d'un bouton pour sauvegarder le fichier
    save_button = tk.Button(notepad_tab, text="Sauvegarder", command=lambda: save_file(text_box_notepad))
    save_button.pack(side=tk.LEFT, padx=5)
    
def create_second_tab(notebook ):
    second_tab = ttk.Frame(notebook)
    notebook.add(second_tab, text="Terminal")  # Ajoute le deuxième onglet

    # Ajout d'un Text widget dans le deuxième onglet
    text_box_tab2 = tk.Text(second_tab, height=20, width=80, bg="black", fg="green", insertbackground="white", font=("Courier", 12))
    text_box_tab2.pack(expand=True, fill=tk.BOTH)
    
    # Insertion d'un texte initial dans le deuxième onglet

    text_box_tab2.insert(tk.END, "This is the second tab!\n")
    
# Fonction principale qui crée la fenêtre
def main():
    global root, text_box  # On utilise des variables globales pour accéder au terminal et à la fenêtre

    # Création de la fenêtre principale
    root = tk.Tk()
    root.title("LEGION")

    # Création du widget Notebook (les onglets)
    global notebook 
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill=tk.BOTH)

    # Premier onglet (Terminal)
    first_tab = ttk.Frame(notebook)
    notebook.add(first_tab, text="Terminal")  # Ajoute le premier onglet

    # Configuration du widget Text dans le premier onglet (le terminal)
    text_box = tk.Text(first_tab, height=20, width=80, bg="black", fg="green", insertbackground="white", font=("Courier", 12))
    text_box.pack(expand=True, fill=tk.BOTH)

    # Insertion de l'invite initiale
    text_box.insert(tk.END, "$ ")

    # Liage de la touche Entrée à la fonction de traitement de commande
    text_box.bind("<Return>", handle_command)

    # Désactivation de l'édition du texte avant la dernière ligne
    text_box.config(state=tk.NORMAL)
    text_box.mark_set("insert", "end-1c")
    text_box.focus()

    # Création du deuxième onglet
    #create_second_tab(notebook)
    threading.Thread(target=listen_for_broadcast, daemon=True).start()
    # Démarrage de la boucle principale de l'application
    root.mainloop()

# Appel de la fonction principale
if __name__ == "__main__":
    
    main()