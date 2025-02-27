"""
Basit admin kullanıcısı oluşturma scripti
"""
from app import app, db
from models import User

# Admin bilgileri
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"  # Güvenli bir şifre kullanın

def create_admin_user():
    with app.app_context():
        # Kullanıcının zaten var olup olmadığını kontrol et
        existing_user = User.query.filter_by(username=ADMIN_USERNAME).first()
        if existing_user:
            print(f"'{ADMIN_USERNAME}' kullanıcısı zaten mevcut.")
            # Kullanıcıyı admin yap
            if not existing_user.is_admin:
                existing_user.is_admin = True
                db.session.commit()
                print(f"'{ADMIN_USERNAME}' kullanıcısı admin olarak güncellendi.")
            return
        
        # Yeni admin kullanıcısı oluştur
        admin = User(username=ADMIN_USERNAME, email=ADMIN_EMAIL, is_admin=True)
        admin.set_password(ADMIN_PASSWORD)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin kullanıcısı '{ADMIN_USERNAME}' başarıyla oluşturuldu!")
        print(f"Kullanıcı adı: {ADMIN_USERNAME}")
        print(f"Şifre: {ADMIN_PASSWORD}")

if __name__ == "__main__":
    create_admin_user()
