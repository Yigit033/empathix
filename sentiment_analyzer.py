from textblob import TextBlob
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
import re
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# NLTK gerekli kaynakları indir
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Duygu kategorileri için anahtar kelimeler
EMOTION_KEYWORDS = {
    'happiness': [
        'happy', 'joy', 'delighted', 'pleased', 'glad', 'satisfied', 'cheerful', 'content', 'thrilled', 'excited',
        'mutlu', 'sevinç', 'memnun', 'neşeli', 'keyifli', 'tatmin', 'hoşnut', 'heyecanlı'
    ],
    'sadness': [
        'sad', 'unhappy', 'depressed', 'miserable', 'heartbroken', 'gloomy', 'disappointed', 'upset', 'tearful',
        'üzgün', 'mutsuz', 'depresif', 'kederli', 'kalbi kırık', 'karamsar', 'hayal kırıklığı', 'kırgın'
    ],
    'anger': [
        'angry', 'mad', 'furious', 'outraged', 'annoyed', 'irritated', 'frustrated', 'enraged', 'hostile',
        'kızgın', 'öfkeli', 'sinirli', 'hiddetli', 'rahatsız', 'huzursuz', 'hayal kırıklığına uğramış', 'düşmanca'
    ],
    'fear': [
        'afraid', 'scared', 'frightened', 'terrified', 'anxious', 'worried', 'nervous', 'panicked', 'horrified',
        'korkmuş', 'ürkmüş', 'dehşete düşmüş', 'endişeli', 'kaygılı', 'gergin', 'panik', 'dehşet'
    ],
    'surprise': [
        'surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'startled', 'speechless', 'bewildered',
        'şaşırmış', 'hayret', 'şaşkın', 'şok', 'afallama', 'hayrete düşmüş', 'nutku tutulmuş', 'afallamış'
    ]
}

# Desteklenen diller ve kodları
SUPPORTED_LANGUAGES = {
    'en': 'İngilizce',
    'tr': 'Türkçe',
    'es': 'İspanyolca',
    'fr': 'Fransızca',
    'de': 'Almanca',
    'it': 'İtalyanca',
    'pt': 'Portekizce',
    'ru': 'Rusça',
    'ar': 'Arapça',
    'zh-cn': 'Çince (Basitleştirilmiş)',
    'ja': 'Japonca',
    'ko': 'Korece'
}

def detect_language(text):
    """Metnin dilini tespit eder."""
    try:
        lang_code = detect(text)
        # Bazı dil kodlarını düzeltme
        if lang_code == 'zh-cn' or lang_code == 'zh-tw' or lang_code == 'zh':
            lang_code = 'zh-cn'
        
        # Desteklenen diller listesinde varsa o dili döndür, yoksa 'en' (İngilizce) döndür
        if lang_code in SUPPORTED_LANGUAGES:
            return lang_code, SUPPORTED_LANGUAGES[lang_code]
        return 'en', 'İngilizce (Varsayılan)'
    except LangDetectException:
        return 'en', 'İngilizce (Varsayılan)'

def translate_to_english(text, source_lang='auto'):
    """Metni İngilizce'ye çevirir."""
    try:
        if source_lang == 'en':
            return text  # Zaten İngilizce ise çevirme
        
        translator = GoogleTranslator(source=source_lang, target='en')
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        print(f"Çeviri hatası: {e}")
        return text  # Hata durumunda orijinal metni döndür

def clean_text(text):
    """Metni temizler ve analize hazırlar."""
    # URL'leri kaldır
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # HTML etiketlerini kaldır
    text = re.sub(r'<.*?>', '', text)
    # Fazla boşlukları kaldır
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def analyze_detailed_emotions(text, lang_code):
    """
    Metindeki detaylı duygu kategorilerini analiz eder.
    Her bir duygu kategorisi için 0-1 arasında bir skor döndürür.
    """
    # Metni İngilizce'ye çevir (eğer İngilizce değilse)
    if lang_code != 'en':
        en_text = translate_to_english(text, lang_code)
    else:
        en_text = text
    
    # Metni küçük harfe çevir ve kelimelere ayır
    words = word_tokenize(en_text.lower())
    
    # Durdurma kelimelerini kaldır
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    
    # Her duygu kategorisi için skor hesapla
    emotion_scores = {
        'happiness': 0.0,
        'sadness': 0.0,
        'anger': 0.0,
        'fear': 0.0,
        'surprise': 0.0
    }
    
    # Metindeki her kelime için duygu kategorilerini kontrol et
    for word in words:
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if word in keywords:
                emotion_scores[emotion] += 1
    
    # Skorları normalize et (0-1 arasında)
    total_matches = sum(emotion_scores.values())
    if total_matches > 0:
        for emotion in emotion_scores:
            emotion_scores[emotion] = emotion_scores[emotion] / total_matches
    
    # TextBlob polaritesini de hesaba kat
    analysis = TextBlob(en_text)
    polarity = analysis.sentiment.polarity
    
    # Polarite pozitifse mutluluk skorunu artır, negatifse üzüntü ve öfke skorlarını artır
    if polarity > 0:
        emotion_scores['happiness'] = max(emotion_scores['happiness'], abs(polarity))
    else:
        emotion_scores['sadness'] = max(emotion_scores['sadness'], abs(polarity) * 0.7)
        emotion_scores['anger'] = max(emotion_scores['anger'], abs(polarity) * 0.3)
    
    return emotion_scores

def calculate_intensity(emotion_scores, polarity):
    """
    Duygu yoğunluğunu hesaplar.
    1: Hafif, 2: Orta, 3: Yüksek
    """
    # En yüksek duygu skoru
    max_emotion_score = max(emotion_scores.values())
    
    # Polarite mutlak değeri
    abs_polarity = abs(polarity)
    
    # Yoğunluk hesaplama
    if max_emotion_score < 0.3 and abs_polarity < 0.3:
        return 1  # Hafif
    elif max_emotion_score < 0.6 and abs_polarity < 0.6:
        return 2  # Orta
    else:
        return 3  # Yüksek

def highlight_emotional_words(text, lang_code):
    """
    Metindeki duygusal kelimeleri tespit eder ve vurgular.
    Vurgulanan kelimeler ve duygu kategorileri ile birlikte döndürür.
    """
    # Metni İngilizce'ye çevir (eğer İngilizce değilse)
    if lang_code != 'en':
        en_text = translate_to_english(text, lang_code)
    else:
        en_text = text
    
    # Metni kelimelere ayır
    words = word_tokenize(en_text.lower())
    
    # Duygusal kelimeleri tespit et
    emotional_words = []
    for i, word in enumerate(words):
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if word in keywords:
                emotional_words.append({
                    'word': word,
                    'emotion': emotion,
                    'position': i
                })
    
    return {
        'text': text,
        'emotional_words': emotional_words
    }

def analyze_sentiment(text):
    """Metnin duygu analizini yapar ve sonuçları döndürür."""
    # Metni temizle
    cleaned_text = clean_text(text)
    
    # Dil tespiti yap
    lang_code, lang_name = detect_language(cleaned_text)
    
    # Metni İngilizce'ye çevir (eğer İngilizce değilse)
    if lang_code != 'en':
        en_text = translate_to_english(cleaned_text, lang_code)
    else:
        en_text = cleaned_text
    
    # TextBlob ile duygu analizi yap
    analysis = TextBlob(en_text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    # Polariteyi değerlendir
    if polarity > 0.05:
        sentiment = "Pozitif"
    elif polarity < -0.05:
        sentiment = "Negatif"
    else:
        sentiment = "Nötr"
    
    # Güven skorunu hesapla (0-100 arasında)
    confidence = abs(polarity) * 100
    
    # Detaylı duygu kategorilerini analiz et
    emotion_scores = analyze_detailed_emotions(cleaned_text, lang_code)
    
    # Duygu yoğunluğunu hesapla
    intensity = calculate_intensity(emotion_scores, polarity)
    
    # Duygusal kelimeleri vurgula
    highlighted_emotions = highlight_emotional_words(cleaned_text, lang_code)
    
    # Sonuçları döndür
    result = {
        'text': text,
        'cleaned_text': cleaned_text,
        'language_code': lang_code,
        'language_name': lang_name,
        'translated_text': en_text if lang_code != 'en' else None,
        'sentiment': sentiment,
        'polarity': polarity,
        'subjectivity': subjectivity,
        'confidence': round(confidence, 2),
        'emotion_scores': {
            'happiness': round(emotion_scores['happiness'], 2),
            'sadness': round(emotion_scores['sadness'], 2),
            'anger': round(emotion_scores['anger'], 2),
            'fear': round(emotion_scores['fear'], 2),
            'surprise': round(emotion_scores['surprise'], 2)
        },
        'intensity': intensity,
        'highlighted_emotions': highlighted_emotions['emotional_words']
    }
    
    return result
