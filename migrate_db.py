"""
Veritabanı şemasını güncellemek için migration script.
Bu script, User tablosuna is_admin alanı, EmotionStats tablosuna average_intensity alanı ve
TextSuggestionFeedback tablosuna user_id alanı ekler.
"""

import sqlite3
import os

def migrate_database():
    """Veritabanı şemasını günceller."""
    print("Empathix Veritabanı Güncelleme Aracı")
    print("------------------------------------")
    
    db_path = 'empathix.db'
    
    # Veritabanı dosyasının varlığını kontrol et
    if not os.path.exists(db_path):
        print(f"Veritabanı dosyası ({db_path}) bulunamadı!")
        return False
    
    # SQLite bağlantısı oluştur
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # User tablosunda is_admin sütununun varlığını kontrol et
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'is_admin' not in column_names:
        print("'is_admin' sütunu User tablosuna ekleniyor...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
            print("'is_admin' sütunu başarıyla eklendi!")
        except sqlite3.Error as e:
            print(f"Hata: {e}")
            conn.rollback()
            return False
    else:
        print("'is_admin' sütunu zaten mevcut.")
    
    # EmotionStats tablosunda average_intensity sütununun varlığını kontrol et
    cursor.execute("PRAGMA table_info(emotion_stats)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'average_intensity' not in column_names:
        print("'average_intensity' sütunu EmotionStats tablosuna ekleniyor...")
        try:
            cursor.execute("ALTER TABLE emotion_stats ADD COLUMN average_intensity FLOAT DEFAULT 0.0")
            conn.commit()
            print("'average_intensity' sütunu başarıyla eklendi!")
        except sqlite3.Error as e:
            print(f"Hata: {e}")
            conn.rollback()
            return False
    else:
        print("'average_intensity' sütunu zaten mevcut.")
    
    # TextSuggestionFeedback tablosunda user_id sütununun varlığını kontrol et
    cursor.execute("PRAGMA table_info(text_suggestion_feedback)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'user_id' not in column_names:
        print("'user_id' sütunu TextSuggestionFeedback tablosuna ekleniyor...")
        try:
            cursor.execute("ALTER TABLE text_suggestion_feedback ADD COLUMN user_id INTEGER REFERENCES user(id)")
            conn.commit()
            print("'user_id' sütunu başarıyla eklendi!")
        except sqlite3.Error as e:
            print(f"Hata: {e}")
            conn.rollback()
            return False
    else:
        print("'user_id' sütunu zaten mevcut.")
    
    # Bağlantıyı kapat
    conn.close()
    
    print("\nVeritabanı güncelleme işlemi tamamlandı!")
    return True

if __name__ == "__main__":
    migrate_database()
