from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar_123'

# BURAYI HİÇ DEĞİŞTİRME, KENDİ BİN_ID VE MASTER_KEY'İNİ SADECE İÇİNE YAZ
BIN_ID = '6a452d96f5f4af5e294e2344'
MASTER_KEY = '$2a$10$Vm/z9QlARXZ/0VCmOwuF7.0Y0lx4OMxSR9b8gTy4Sv5aR4U3A822O' 

def load_data():
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
        response = requests.get(url, headers={'X-Master-Key': MASTER_KEY})
        # JSONBin API'si veriyi 'record' anahtarı içinde gönderir
        return response.json().get('record', {})
    except:
        return {}

def save_data(data):
    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
    headers = {'Content-Type': 'application/json', 'X-Master-Key': MASTER_KEY}
    requests.put(url, json=data, headers=headers)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        if username == "admin" and password == "ily123":
            session['username'] = "admin"
            return redirect(url_for('admin_dashboard'))
        
        students = load_data()
        if username in students and str(students[username].get('password')) == str(password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Hatalı Giriş! <a href='/login'>Geri Dön</a>"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session['username'] == 'admin':
        return redirect(url_for('login'))
    user_data = load_data().get(session['username'])
    return render_template('dashboard.html', user_data=user_data)

@app.route('/admin')
def admin_dashboard():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    return render_template('admin.html', students=load_data())

@app.route('/admin/add', methods=['GET', 'POST'])
def add_student():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    if request.method == 'POST':
        students = load_data()
        students[request.form.get('username').lower()] = {
            'password': request.form.get('password'),
            'name': request.form.get('name')
        }
        save_data(students)
        return redirect(url_for('admin_dashboard'))
    return render_template('add_student.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
