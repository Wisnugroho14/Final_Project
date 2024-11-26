from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://test:sparta@cluster0.kbfqt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


# Halaman Utama: 
@app.route('/')
def index():
    return render_template('index.html')

# Halaman About:
@app.route('/about')
def about():
    return render_template('about.html')

# Halaman Form:
@app.route('/form')
def form():
    return render_template('form.html')

# Halaman Contact:    
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Halaman Login: 
@app.route('/login')
def login():
    return render_template('login.html')

# Halaman Register: 
@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)