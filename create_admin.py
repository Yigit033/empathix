"""
Admin kullanıcısı oluşturmak için komut satırı aracı.
"""

import sys
import os
from getpass import getpass
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

def create_admin():
    """Admin kullanıcısı oluşturur."""
    print("Empathix Admin Kullanıcısı Oluşturma Aracı")
    print("------------------------------------------")
    
    # Flask uygulamasını oluştur
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///empathix.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Veritabanı bağlantısını oluştur
    db = SQLAlchemy(app)
    
    # User modelini dinamik olarak oluştur
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(64), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(128))
        is_admin = db.Column(db.Boolean, default=False)
        
        def set_password(self, password):
            self.password_hash = generate_password_hash(password)
    
    # Kullanıcı bilgilerini al
    username = input("Kullanıcı adı: ")
    email = input("E-posta: ")
    password = getpass("Şifre: ")
    confirm_password = getpass("Şifreyi tekrar girin: ")
    
    # Şifreleri kontrol et
    if password != confirm_password:
        print("Şifreler eşleşmiyor!")
        return False
    
    # Kullanıcı adı ve e-posta kontrolü
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"'{username}' kullanıcı adı zaten kullanılıyor!")
            return False
        
        if User.query.filter_by(email=email).first():
            print(f"'{email}' e-posta adresi zaten kullanılıyor!")
            return False
        
        # Admin kullanıcısını oluştur
        admin = User(username=username, email=email, is_admin=True)
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"\nAdmin kullanıcısı '{username}' başarıyla oluşturuldu!")
        return True

if __name__ == "__main__":
    create_admin()
