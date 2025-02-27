from app import app

# Railway için port ayarı
import os
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    # Veritabanı tablolarını oluştur
    with app.app_context():
        from models import db
        db.create_all()
        
        # Admin panelini başlat
        from admin import init_admin
        init_admin(app, db)
    
    # Uygulamayı çalıştır
    app.run(host='0.0.0.0', port=port, debug=False)
