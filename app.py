from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar_123'

DATA_FILE = "database.json"

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f: 
        return json.load(f)

# --- ROTALAR ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        # 1. ADMIN KONTROLÜ
        if username == "admin" and password == "ily123":
            session['username'] = "admin"
            return redirect(url_for('admin_dashboard'))
        
        # 2. ÖĞRENCİ KONTROLÜ
        students = load_data()
        if username in students and students[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
            
        return "Hatalı Giriş!", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session['username'] == 'admin':
        return redirect(url_for('login'))
    
    students = load_data()
    user_data = students.get(session['username'])
    return render_template('dashboard.html', user_data=user_data)

@app.route('/admin')
def admin_dashboard():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    return render_template('admin.html', students=load_data())

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)