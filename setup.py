import subprocess
import sys
import os

def check_python_version():
    """Python sürümünü kontrol et."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Hata: Python {required_version[0]}.{required_version[1]} veya daha yüksek bir sürüm gereklidir.")
        print(f"Mevcut sürüm: {current_version[0]}.{current_version[1]}")
        return False
    return True

def install_requirements():
    """Gerekli paketleri yükle."""
    print("Gerekli paketler yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Paketler başarıyla yüklendi.")
        return True
    except subprocess.CalledProcessError:
        print("Hata: Paketler yüklenirken bir sorun oluştu.")
        return False

def test_model():
    """Duygu analizi modelini test et."""
    print("Duygu analizi modeli test ediliyor...")
    try:
        subprocess.check_call([sys.executable, "test_model.py"])
        return True
    except subprocess.CalledProcessError:
        print("Hata: Model testi başarısız oldu.")
        return False

def main():
    """Ana kurulum işlemi."""
    print("Empathix - Kurulum Başlıyor")
    print("-" * 50)
    
    # Python sürümünü kontrol et
    if not check_python_version():
        return
    
    # Gerekli paketleri yükle
    if not install_requirements():
        return
    
    # Modeli test et
    if not test_model():
        return
    
    print("-" * 50)
    print("Kurulum tamamlandı!")
    print("Uygulamayı başlatmak için 'python app.py' komutunu çalıştırın.")
    print("Tarayıcınızda 'http://localhost:5000' adresine giderek uygulamayı kullanabilirsiniz.")

if __name__ == "__main__":
    main()
