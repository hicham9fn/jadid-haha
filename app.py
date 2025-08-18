from flask import Flask, request, render_template, redirect, session, flash, g
import sqlite3
from googletrans import Translator
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici!123'
DATABASE = 'database.db'

# Gestion base de données
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                translation TEXT,
                explanation TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        db.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT id, password FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        if user and hash_password(password) == user['password']:
            session['user_id'] = user['id']
            flash('Connexion réussie!', 'success')
            return redirect('/')
        else:
            flash('Identifiants incorrects', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            db.commit()
            flash('Inscription réussie! Connectez-vous', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Nom d\'utilisateur déjà pris', 'error')
    
    return render_template('register.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return redirect('/login')
    
    text = request.form['text'].strip()
    if not text:
        flash('Veuillez entrer un texte', 'error')
        return redirect('/')
    
    try:
        # Traduction
        translator = Translator()
        translation = translator.translate(text, dest='fr').text
        
        # Explication automatique
        explanations = {
            "hello": "Salutation anglaise",
            "bonjour": "Salutation française",
            "python": "Langage de programmation",
            "hicham": "howa li 9ad had lboot dyal l3bar b idafa l chatgptt  .-.",
            "issam ": "sa7eb hicham"
          
        }
        explanation = explanations.get(text.lower(), "Aucune explication spécifique disponible")
        
        # Sauvegarde
        db = get_db()
        db.execute('''
            INSERT INTO searches (user_id, text, translation, explanation)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], text, translation, explanation))
        db.commit()
        
        return render_template('index.html',
                            original=text,
                            translation=translation,
                            explanation=explanation)
    
    except Exception as e:
        flash(f"Erreur: {str(e)}", 'error')
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    