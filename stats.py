import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışması için
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from models import Analysis, LanguageStats, SentimentStats, EmotionStats, db
from datetime import datetime, timedelta

def get_sentiment_distribution(user_id=None):
    """
    Duygu analizi dağılımını gösteren pasta grafik oluşturur.
    
    Args:
        user_id (int, optional): Belirli bir kullanıcı için istatistik oluşturmak için kullanıcı ID'si.
        
    Returns:
        str: Base64 kodlanmış grafik görüntüsü.
    """
    try:
        # Veritabanı sorgusunu hazırla
        from models import Analysis, db
        
        if user_id:
            # Belirli bir kullanıcı için duygu dağılımı
            query = db.session.query(
                Analysis.sentiment, 
                db.func.count(Analysis.id).label('count')
            ).filter(Analysis.user_id == user_id)
        else:
            # Tüm kullanıcılar için duygu dağılımı
            query = db.session.query(
                Analysis.sentiment, 
                db.func.count(Analysis.id).label('count')
            )
        
        # Sorguyu grupla ve sonuçları al
        results = query.group_by(Analysis.sentiment).all()
        
        # Veri yoksa boş grafik döndür
        if not results:
            return None
        
        # Verileri hazırla
        labels = [r[0] for r in results]
        sizes = [r[1] for r in results]
        
        # Renkleri belirle
        colors = []
        for label in labels:
            if label == 'Pozitif':
                colors.append('#4CAF50')  # Yeşil
            elif label == 'Negatif':
                colors.append('#F44336')  # Kırmızı
            else:
                colors.append('#FFC107')  # Sarı
        
        # Grafik oluştur
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                shadow=True, startangle=140, textprops={'fontsize': 12})
        plt.axis('equal')  # Dairesel görünüm için
        plt.title('Duygu Analizi Dağılımı', fontsize=16, pad=20)
        
        # Grafik görüntüsünü belleğe kaydet
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Base64 kodla
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()
        
        return img_str
        
    except Exception as e:
        print(f"Grafik oluşturma hatası: {e}")
        return None

def get_language_distribution(user_id=None):
    """
    Dil dağılımını gösteren pasta grafik oluşturur.
    
    Args:
        user_id (int, optional): Belirli bir kullanıcı için istatistik oluşturmak için kullanıcı ID'si.
        
    Returns:
        str: Base64 kodlanmış grafik görüntüsü.
    """
    try:
        # Veritabanı sorgusunu hazırla
        from models import Analysis, db
        
        if user_id:
            # Belirli bir kullanıcı için dil dağılımı
            query = db.session.query(
                Analysis.original_language, 
                db.func.count(Analysis.id).label('count')
            ).filter(Analysis.user_id == user_id)
        else:
            # Tüm kullanıcılar için dil dağılımı
            query = db.session.query(
                Analysis.original_language, 
                db.func.count(Analysis.id).label('count')
            )
        
        # Sorguyu grupla ve sonuçları al
        results = query.group_by(Analysis.original_language).all()
        
        # Veri yoksa boş grafik döndür
        if not results:
            return None
        
        # Verileri hazırla
        languages = [r[0] for r in results]
        counts = [r[1] for r in results]
        
        # Dil kodlarını okunabilir isimlere dönüştür
        language_names = []
        for lang in languages:
            if lang == 'en':
                language_names.append('İngilizce')
            elif lang == 'tr':
                language_names.append('Türkçe')
            elif lang == 'es':
                language_names.append('İspanyolca')
            elif lang == 'fr':
                language_names.append('Fransızca')
            elif lang == 'de':
                language_names.append('Almanca')
            else:
                language_names.append(lang)
        
        # Grafik oluştur
        plt.figure(figsize=(8, 6))
        
        # Renk paleti oluştur
        cmap = plt.cm.get_cmap('tab10')
        colors = [cmap(i) for i in np.linspace(0, 1, len(languages))]
        
        plt.pie(counts, labels=language_names, colors=colors, autopct='%1.1f%%', 
                shadow=True, startangle=90, textprops={'fontsize': 12})
        plt.axis('equal')
        plt.title('Dil Dağılımı', fontsize=16, pad=20)
        
        # Grafik görüntüsünü belleğe kaydet
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Base64 kodla
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()
        
        return img_str
        
    except Exception as e:
        print(f"Grafik oluşturma hatası: {e}")
        return None

def get_time_series_analysis(days=30, user_id=None):
    """
    Belirli bir zaman aralığında yapılan analizlerin zaman serisi grafiğini oluşturur.
    
    Args:
        days (int): Kaç günlük veri gösterileceği.
        user_id (int, optional): Belirli bir kullanıcı için istatistik oluşturmak için kullanıcı ID'si.
        
    Returns:
        str: Base64 kodlanmış grafik görüntüsü.
    """
    try:
        # Veritabanı sorgusunu hazırla
        from models import Analysis, db
        
        # Tarih aralığını belirle
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Sorguyu oluştur
        if user_id:
            analyses = Analysis.query.filter(
                Analysis.created_at.between(start_date, end_date),
                Analysis.user_id == user_id
            ).all()
        else:
            analyses = Analysis.query.filter(
                Analysis.created_at.between(start_date, end_date)
            ).all()
        
        # Veri yoksa boş grafik döndür
        if not analyses:
            return None
        
        # Verileri pandas DataFrame'e dönüştür
        data = []
        for analysis in analyses:
            data.append({
                'date': analysis.created_at.date(),
                'sentiment': analysis.sentiment
            })
        
        df = pd.DataFrame(data)
        
        # Tarihe göre grupla ve duygu sayılarını hesapla
        grouped = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
        
        # Eksik tarihleri doldur
        date_range = pd.date_range(start=start_date.date(), end=end_date.date())
        grouped = grouped.reindex(date_range, fill_value=0)
        
        # Duygu kategorilerini kontrol et ve eksik olanları ekle
        for sentiment in ['Pozitif', 'Negatif', 'Nötr']:
            if sentiment not in grouped.columns:
                grouped[sentiment] = 0
        
        # Grafik oluştur
        plt.figure(figsize=(10, 6))
        
        # Çizgi grafiği çiz
        plt.plot(grouped.index, grouped['Pozitif'], 'g-', label='Pozitif', linewidth=2)
        plt.plot(grouped.index, grouped['Negatif'], 'r-', label='Negatif', linewidth=2)
        plt.plot(grouped.index, grouped['Nötr'], 'y-', label='Nötr', linewidth=2)
        
        # Grafik ayarları
        plt.title(f'Son {days} Gün İçindeki Analiz Dağılımı', fontsize=16)
        plt.xlabel('Tarih', fontsize=12)
        plt.ylabel('Analiz Sayısı', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # X ekseni tarih formatını ayarla
        plt.gcf().autofmt_xdate()
        
        # Grafik görüntüsünü belleğe kaydet
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Base64 kodla
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()
        
        return img_str
        
    except Exception as e:
        print(f"Grafik oluşturma hatası: {e}")
        return None

def update_stats(analysis_result):
    """
    Analiz sonucuna göre istatistikleri günceller.
    
    Args:
        analysis_result (dict): Analiz sonucu
    """
    # Dil istatistiklerini güncelle
    lang_code = analysis_result['language_code']
    lang_name = analysis_result['language_name']
    
    lang_stat = LanguageStats.query.filter_by(language_code=lang_code).first()
    if lang_stat:
        lang_stat.count += 1
    else:
        lang_stat = LanguageStats(language_code=lang_code, language_name=lang_name, count=1)
        db.session.add(lang_stat)
    
    # Duygu istatistiklerini güncelle
    sentiment = analysis_result['sentiment']
    sentiment_stat = SentimentStats.query.filter_by(sentiment=sentiment).first()
    if sentiment_stat:
        sentiment_stat.count += 1
    else:
        sentiment_stat = SentimentStats(sentiment=sentiment, count=1)
        db.session.add(sentiment_stat)
    
    # Duygu kategorileri istatistiklerini güncelle
    if 'emotion_scores' in analysis_result:
        # En yüksek skora sahip duygu kategorisini bul
        emotion_scores = analysis_result['emotion_scores']
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # İstatistikleri güncelle
        emotion_stat = EmotionStats.query.filter_by(emotion=primary_emotion).first()
        if emotion_stat:
            emotion_stat.count += 1
        else:
            emotion_stat = EmotionStats(emotion=primary_emotion, count=1)
            db.session.add(emotion_stat)
    
    db.session.commit()
