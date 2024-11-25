from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://test:sparta@cluster0.kbfqt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


# Halaman Utama: 
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)