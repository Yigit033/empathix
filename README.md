# Empathix - Çok Dilli Duygu Analizi Platformu

Empathix, metinlerdeki duygusal tonu analiz eden gelişmiş bir yapay zeka uygulamasıdır. Doğal dil işleme teknolojileri kullanarak, metinlerin pozitif, negatif veya nötr olup olmadığını belirler.

## Özellikler

- **Çoklu Dil Desteği**: 12+ dilde duygu analizi yapabilme
- **Gelişmiş Analiz**: TextBlob ve çeşitli NLP teknolojileri kullanarak doğru duygu analizi
- **Kullanıcı Hesapları**: Kayıt olma, giriş yapma ve kişisel analiz geçmişi
- **Detaylı İstatistikler**: Duygu dağılımı, dil dağılımı ve zaman serisi analizleri
- **Modern Arayüz**: Kullanıcı dostu, responsive tasarım
- **API Desteği**: Dış uygulamalar için RESTful API
- **Admin Paneli**: Veritabanı verilerini görüntülemek ve yönetmek için Flask-Admin tabanlı panel
- **Metin İyileştirme**: Negatif metinleri daha yapıcı ifadelere dönüştürme önerileri
- **Kişiselleştirilmiş Öneriler**: Kullanıcı analiz geçmişine dayalı öneriler

## Kurulum

### Gereksinimler

- Python 3.7+
- Flask ve diğer bağımlılıklar

### Adımlar

1. Repoyu klonlayın:
   ```
   git clone https://github.com/Yigit033/empathix.git
   cd empathix
   ```

2. Sanal ortam oluşturun ve aktifleştirin:
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Gerekli paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

4. Veritabanını oluşturun ve güncelleyin:
   ```
   python migrate_db.py
   ```

5. Admin kullanıcısı oluşturun:
   ```
   python create_admin_simple.py
   ```

6. Uygulamayı çalıştırın:
   ```
   python app.py
   ```

7. Tarayıcınızda http://127.0.0.1:5000 adresine gidin.

## Kullanım

1. Ana sayfada metin giriş alanına analiz etmek istediğiniz metni yazın.
2. "Analiz Et" butonuna tıklayın.
3. Sonuçlar sayfasında duygu analizi sonucunu, güven skorunu ve diğer detayları görüntüleyin.
4. Hesap oluşturarak analiz geçmişinizi kaydedebilir ve kişisel istatistiklerinizi görüntüleyebilirsiniz.

### Admin Paneli Kullanımı

1. Admin kullanıcısı ile giriş yapın (varsayılan: kullanıcı adı "admin", şifre "admin123").
2. Sağ üst köşedeki menüde "Admin Paneli" linkine tıklayın veya doğrudan `/admin` adresine gidin.
3. Admin panelinde şunları yapabilirsiniz:
   - Kullanıcıları görüntüleme ve düzenleme
   - Analizleri görüntüleme
   - Dil ve duygu istatistiklerini görüntüleme
   - Kullanıcı tercihlerini yönetme
   - Metin önerisi geri bildirimlerini inceleme

## Desteklenen Diller

- Türkçe
- İngilizce
- İspanyolca
- Fransızca
- Almanca
- İtalyanca
- Portekizce
- Rusça
- Arapça
- Çince (Basitleştirilmiş)
- Japonca
- Korece
- ve daha fazlası...

## Teknolojiler

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Duygu Analizi**: TextBlob, LangDetect, Deep Translator
- **Veritabanı**: SQLite (geliştirme), PostgreSQL (üretim)
- **Grafikler**: Matplotlib

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

Sorularınız veya önerileriniz için [email@example.com](mailto:email@example.com) adresine e-posta gönderebilirsiniz.
