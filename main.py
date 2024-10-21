import tkinter as tk
from tkinter import ttk, filedialog

import socket
import threading
import socket

# Fonction qui se connecte à un serveur
def client_program(server_address,server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création du socket

    # Tentative de connexion au serveur
    try:
        client_socket.connect((server_address, server_port))
        print("En attente de l'acceptation du serveur...")

        # Recevoir la réponse du serveur (acceptation ou refus)
        message = client_socket.recv(1024).decode('utf-8')
        if message == "Connexion acceptée":
            print("Connexion acceptée par le serveur.")
        elif message == "Connexion refusée":
            print("Connexion refusée par le serveur.")
            client_socket.close()
            return

        while True:
            # Envoyer un message au serveur
            message = input("Votre message : ")
            client_socket.send(message.encode('utf-8'))

            # Recevoir une réponse du serveur
            response = client_socket.recv(1024).decode('utf-8')
            if not response:
                break
            print(f"Message du serveur : {response}")

    except socket.error as e:
        print(f"Erreur lors de la connexion : {e}")
    finally:
        client_socket.close()  # Fermer la connexion


# Fonction qui attend les connexions du client et les accepte
def server_program():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Création du socket
    server_socket.bind(('0.0.0.0', 8080))  # Le serveur écoute sur toutes les interfaces sur le port 8080
    server_socket.listen(1)  # Le serveur écoute pour une connexion

    print("En attente d'une connexion...")

    # Accepter la connexion d'un client
    conn, address = server_socket.accept()
    print(f"Connexion reçue de : {address}")

    # L'utilisateur doit accepter la connexion
    accept_connection = input("Accepter la connexion ? (y/n) : ")
    if accept_connection.lower() == 'y':
        conn.send("Connexion acceptée".encode('utf-8'))  # Encode la chaîne en UTF-8

        print("Connexion acceptée. Vous êtes maintenant connectés.")
    else:
        conn.send("Connexion acceptée".encode('utf-8'))  # Encode la chaîne en UTF-8

        conn.close()
        print("Connexion refusée.")

    while True:
        # Attendre des messages du client
        message = conn.recv(1024).decode('utf-8')
        if not message:
            break
        print(f"Message reçu: {message}")
        # Répondre au client
        response = input("Votre message : ")
        conn.send(response.encode('utf-8'))

    conn.close()  # Fermer la connexion une fois la communication terminée

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
            client_program(ip_address,port)
    elif "/server/" in command:
        output = "lauching server"
        text_box.insert(tk.END, f"\n{output}\n$ ")
        threading.Thread(target=server_program)
            
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

# Fonction pour créer un nouvel onglet de type bloc-notes
def create_notepad_tab(notebook):
    # Crée un nouvel onglet
    notepad_tab = ttk.Frame(notebook)
    notebook.add(notepad_tab, text="Bloc Notes")  # Ajoute le nouvel onglet avec un titre "Bloc Notes"

    # Ajout d'un widget Text dans cet onglet
    text_box_notepad = tk.Text(notepad_tab, height=20, width=80,bg="black", fg="green", font=("Courier", 12))
    text_box_notepad.pack(expand=True, fill=tk.BOTH)

    # Ajout d'un bouton pour sauvegarder le fichier
    save_button = tk.Button(notepad_tab, text="Sauvegarder", command=lambda: save_file(text_box_notepad))
    save_button.pack()
    
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

    # Démarrage de la boucle principale de l'application
    root.mainloop()

# Appel de la fonction principale
if __name__ == "__main__":
    main()