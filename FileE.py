import os
import tkinter as tk
from tkinter import ttk, filedialog


class FileExplorer:
    def __init__(self, app):
        self.app = app
        self.tree = None  # Arborescence des fichiers
        self.directory = None

    def open_directory(self):
        """Ouvre une boîte de dialogue pour choisir un répertoire à afficher dans l'explorateur de fichiers."""
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.populate_tree(self.directory)
            self.directory = os.path.dirname(self.directory)
                     
    def populate_tree(self, directory):
        """Peuple l'arborescence des fichiers avec le contenu du répertoire donné."""
        if self.tree is None:
            # Créer l'arborescence (Treeview) seulement si elle n'existe pas
            self.tree = ttk.Treeview(self.app.file_tree)
            self.tree.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

            # Configuration des colonnes
            self.tree.heading("#0", text="Nom", anchor=tk.W)
            self.tree.bind("<Double-1>", self.on_item_double_click)  # Ouvrir un fichier en double-cliquant
        else:
            # Si l'arborescence existe déjà, vider son contenu
            self.tree.delete(*self.tree.get_children())

        # Remplir l'arborescence avec le nouveau répertoire
        self.insert_node('', directory)

    def insert_node(self, parent, path):
        """Ajoute les nœuds d'un répertoire (fichiers et sous-dossiers) dans l'arborescence."""
        node = self.tree.insert(parent, 'end', text=os.path.basename(path), open=True)
        if os.path.isdir(path):
            for item in os.listdir(path):
                self.insert_node(node, os.path.join(path, item))

    def on_item_double_click(self, event):
        """Gestion de l'ouverture d'un fichier lorsque l'utilisateur double-clique sur un élément dans l'arborescence."""
        try:
            item = self.tree.selection()[0]  # Récupérer l'élément sélectionné

            # Récupérer le chemin complet de l'élément sélectionné
            file_path = self.get_full_path(item)

            if os.path.isfile(file_path):  # Vérifie si le chemin est bien un fichier
                self.app.create_project_tab(file_path)  # Ouvrir le fichier dans un onglet Notepad
            else:
                print("L'élément sélectionné n'est pas un fichier.")
        except IndexError:
            print("Aucun élément sélectionné.")  # Si aucun élément n'est sélectionné
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier : {e}")  # Gestion des autres erreurs
       
    def get_full_path(self, item):
        """Récupère le chemin complet de l'élément sélectionné dans l'arborescence Treeview en retirant la racine."""
        path = self.tree.item(item, "text")  # Texte de l'élément sélectionné
        parent = self.tree.parent(item)  # Récupère le parent de l'élément

        # Remonte dans l'arborescence en ajoutant les parents au chemin, mais ignore la racine
        while parent:
            parent_text = self.tree.item(parent, "text")  # Texte du parent

            # Ajoute le parent au chemin, sauf si c'est la racine (self.directory)
            path = os.path.join(parent_text, path)
            parent = self.tree.parent(parent)  # Passe au parent suivant (remonte l'arborescence)

        # Le chemin obtenu est relatif à self.directory, donc inutile de l'ajouter à nouveau
        full_path = os.path.normpath(os.path.join(self.directory, path)).replace("\\", "/")

        print(full_path)  # Affiche le chemin final (pour débogage)
        return full_path
