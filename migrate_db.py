"""
Empathix Veritabanı Güncelleme Aracı

Bu script, veritabanı şemasını güncellemek için kullanılır.
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text

def is_postgres_db():
    """PostgreSQL veritabanı kullanılıp kullanılmadığını kontrol eder."""
    db_url = os.environ.get('DATABASE_URL')
    return db_url and ('postgresql' in db_url or 'postgres' in db_url)

def get_db_connection():
    """Veritabanı bağlantısı oluşturur."""
    if is_postgres_db():
        # PostgreSQL bağlantısı
        db_url = os.environ.get('DATABASE_URL')
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        # SQLAlchemy ile bağlantı kur
        engine = create_engine(db_url)
        return engine.connect()
    else:
        # SQLite bağlantısı
        conn = sqlite3.connect('empathix.db')
        return conn

def add_column_if_not_exists(table_name, column_name, column_type):
    """
    Belirtilen tabloya, belirtilen sütunu ekler (eğer yoksa).
    
    Args:
        table_name (str): Tablo adı
        column_name (str): Eklenecek sütun adı
        column_type (str): Sütun tipi (SQLite veya PostgreSQL için)
    """
    try:
        if is_postgres_db():
            # PostgreSQL için
            conn = get_db_connection()
            
            # Sütunun var olup olmadığını kontrol et
            check_query = text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = '{column_name}'
            """)
            
            result = conn.execute(check_query).fetchone()
            
            if not result:
                # Sütun yoksa ekle
                alter_query = text(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN {column_name} {column_type}
                """)
                
                conn.execute(alter_query)
                conn.commit()
                print(f"'{column_name}' sütunu başarıyla eklendi!")
            else:
                print(f"'{column_name}' sütunu zaten var.")
            
            conn.close()
        else:
            # SQLite için
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Sütunun var olup olmadığını kontrol et
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            
            if column_name not in columns:
                # Sütun yoksa ekle
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                conn.commit()
                print(f"'{column_name}' sütunu başarıyla eklendi!")
            else:
                print(f"'{column_name}' sütunu zaten var.")
            
            conn.close()
            
    except Exception as e:
        print(f"Hata: {e}")
        return False
    
    return True

def update_database():
    """Veritabanı şemasını günceller."""
    print("Empathix Veritabanı Güncelleme Aracı")
    print("------------------------------------")
    
    # User tablosuna is_admin sütunu ekle
    print("'is_admin' sütunu User tablosuna ekleniyor...")
    column_type = "BOOLEAN DEFAULT FALSE" if is_postgres_db() else "BOOLEAN DEFAULT 0"
    add_column_if_not_exists("user", "is_admin", column_type)
    
    # EmotionStats tablosuna average_intensity sütunu ekle
    print("'average_intensity' sütunu EmotionStats tablosuna ekleniyor...")
    column_type = "FLOAT DEFAULT 0.0" if is_postgres_db() else "FLOAT DEFAULT 0.0"
    add_column_if_not_exists("emotion_stats", "average_intensity", column_type)
    
    # TextSuggestionFeedback tablosuna user_id sütunu ekle
    print("'user_id' sütunu TextSuggestionFeedback tablosuna ekleniyor...")
    column_type = "INTEGER" if is_postgres_db() else "INTEGER"
    add_column_if_not_exists("text_suggestion_feedback", "user_id", column_type)
    
    print("\nVeritabanı güncelleme işlemi tamamlandı!")

if __name__ == "__main__":
    update_database()
