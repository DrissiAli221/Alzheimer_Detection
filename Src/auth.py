"""
Système d'authentification pour l'application Alzheimer Detection
Gestion des utilisateurs : login, register, roles
"""

import sqlite3
import hashlib
import os
from datetime import datetime

# CORRECTION : Chemin absolu de la base de données
DB_PATH = 'users.db'  # Simplifié : dans le même dossier que le script

class AuthSystem:
    """Gère l'authentification des utilisateurs."""
    
    def __init__(self):
        """Initialise la base de données."""
        self.init_database()
    
    def init_database(self):
        """Crée la table users si elle n'existe pas."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✅ Base de données initialisée : {os.path.abspath(DB_PATH)}")
        except Exception as e:
            print(f"❌ Erreur init database : {e}")
    
    def hash_password(self, password):
        """Hache le mot de passe avec SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, password, full_name, role="doctor"):
        """
        Enregistre un nouvel utilisateur.
        
        Args:
            username: Nom d'utilisateur (unique)
            email: Email (unique)
            password: Mot de passe en clair
            full_name: Nom complet
            role: Role (doctor, admin)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validation des données
        if len(username) < 3:
            return False, "Le nom d'utilisateur doit contenir au moins 3 caractères"
        
        if len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères"
        
        if '@' not in email:
            return False, "Email invalide"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Vérifier si l'utilisateur existe déjà
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                         (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "Nom d'utilisateur ou email déjà utilisé"
            
            # Insérer le nouvel utilisateur
            password_hash = self.hash_password(password)
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, full_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, full_name, created_at))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Utilisateur créé : {username}")
            return True, "Inscription réussie ! Vous pouvez vous connecter."
            
        except Exception as e:
            print(f"❌ Erreur register : {e}")
            return False, f"Erreur lors de l'inscription : {str(e)}"
    
    def login_user(self, username, password):
        """
        Connecte un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe en clair
        
        Returns:
            tuple: (success: bool, user_data: dict or message: str)
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, email, role, full_name, created_at
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Mettre à jour la dernière connexion
                last_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                             (last_login, user[0]))
                conn.commit()
                conn.close()
                
                # Retourner les données de l'utilisateur
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'role': user[3],
                    'full_name': user[4],
                    'created_at': user[5],
                    'last_login': last_login
                }
                
                print(f"✅ Connexion réussie : {username}")
                return True, user_data
            else:
                conn.close()
                return False, "Nom d'utilisateur ou mot de passe incorrect"
                
        except Exception as e:
            print(f"❌ Erreur login : {e}")
            return False, f"Erreur lors de la connexion : {str(e)}"
    
    def get_user_stats(self):
        """Retourne les statistiques des utilisateurs (pour admin)."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE role = "doctor"')
            total_doctors = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
            total_admins = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total': total_users,
                'doctors': total_doctors,
                'admins': total_admins
            }
        except Exception as e:
            print(f"❌ Erreur get_user_stats : {e}")
            return {'total': 0, 'doctors': 0, 'admins': 0}
    
    def change_password(self, username, old_password, new_password):
        """Change le mot de passe d'un utilisateur."""
        if len(new_password) < 6:
            return False, "Le nouveau mot de passe doit contenir au moins 6 caractères"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            old_hash = self.hash_password(old_password)
            
            # Vérifier l'ancien mot de passe
            cursor.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?',
                         (username, old_hash))
            
            if not cursor.fetchone():
                conn.close()
                return False, "Ancien mot de passe incorrect"
            
            # Mettre à jour le mot de passe
            new_hash = self.hash_password(new_password)
            cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?',
                         (new_hash, username))
            
            conn.commit()
            conn.close()
            
            return True, "Mot de passe changé avec succès"
            
        except Exception as e:
            print(f"❌ Erreur change_password : {e}")
            return False, f"Erreur : {str(e)}"