from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_123'  # Bunu kendine göre değiştirebilirsin

# JSONBin Ayarları
BIN_ID = '6a452d96f5f4af5e294e2344'
MASTER_KEY = '$2a$10$Vm/z9QlARXZ/0VCmOwuF7.0Y0lx4OMxSR9b8gTy4Sv5aR4U3A822O'

def load_data():
    """JSONBin'den öğrenci verilerini çeker."""
    try:
        url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
        headers = {'X-Master-Key': MASTER_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # API'den gelen veriyi 'record' anahtarı üzerinden alıyoruz
            return response.json().get('record', {})
        return {}
    except Exception as e:
        print(f"Veri yüklenirken hata oluştu: {e}")
        return {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Admin kontrolü
        if username == 'admin' and password == '1234':
            session['username'] = 'admin'
            return redirect(url_for('admin'))
        
        # Öğrenci kontrolü
        students = load_data()
        if username in students and students[username].get('password') == password:
            session['username'] = username
            return "Hoş geldin öğrenci!" # Burayı kendi sayfana yönlendirebilirsin
        
        hata = "Geçersiz kullanıcı adı veya şifre!"
        
    return render_template('login.html', hata=hata)

@app.route('/admin')
def admin():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    students = load_data()
    return render_template('admin.html', students=students)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
