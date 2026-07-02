from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_123'

BIN_ID = '6a452d96f5f4af5e294e2344'
MASTER_KEY = '$2a$10$Vm/z9QlARXZ/0VCmOwuF7.0Y0lx4OMxSR9b8gTy4Sv5aR4U3A822O'

def load_data():
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
        headers = {'X-Master-Key': MASTER_KEY}
        response = requests.get(url, headers=headers)
        return response.json().get('record', {}) if response.status_code == 200 else {}
    except:
        return {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '1234':
            session['username'] = 'admin'
            return redirect(url_for('admin'))
        students = load_data()
        if username in students and students[username].get('password') == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        hata = "Hatalı giriş!"
    return render_template('login.html', hata=hata)

@app.route('/admin')
def admin():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    return render_template('admin.html', students=load_data())

@app.route('/add_student', methods=['POST'])
def add_student():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    data = load_data()
    data[request.form.get('username')] = {
        "name": request.form.get('name'),
        "password": request.form.get('password'),
        "phone": request.form.get('phone'),
        "balance": request.form.get('balance'),
        "total_lessons": request.form.get('total_lessons')
    }
    requests.put(f'https://api.jsonbin.io/v3/b/{BIN_ID}', 
                 headers={'X-Master-Key': MASTER_KEY, 'Content-Type': 'application/json'}, json=data)
    return redirect(url_for('admin'))

@app.route('/delete_student/<username>')
def delete_student(username):
    if session.get('username') != 'admin': return redirect(url_for('login'))
    data = load_data()
    if username in data:
        del data[username]
        requests.put(f'https://api.jsonbin.io/v3/b/{BIN_ID}', 
                     headers={'X-Master-Key': MASTER_KEY, 'Content-Type': 'application/json'}, json=data)
    return redirect(url_for('admin'))

@app.route('/update_student', methods=['POST'])
def update_student():
    if session.get('username') != 'admin': return redirect(url_for('login'))
    data = load_data()
    username = request.form.get('username')
    if username in data:
        data[username] = {
            "name": request.form.get('name'),
            "password": request.form.get('password'),
            "phone": request.form.get('phone'),
            "balance": request.form.get('balance'),
            "total_lessons": request.form.get('total_lessons')
        }
        requests.put(f'https://api.jsonbin.io/v3/b/{BIN_ID}', 
                     headers={'X-Master-Key': MASTER_KEY, 'Content-Type': 'application/json'}, json=data)
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
