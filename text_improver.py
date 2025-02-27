"""
Metin önerileri ve düzeltmeleri için modül.
Bu modül, negatif metinleri daha pozitif hale getirme, dilbilgisi düzeltmeleri ve
alternatif ifade önerileri gibi işlevleri sağlar.
"""

import re
import json
import nltk
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from deep_translator import GoogleTranslator
from sentiment_analyzer import EMOTION_KEYWORDS, translate_to_english

# NLTK kaynaklarını kontrol et ve indir
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Negatif ifadelerin pozitif alternatifleri
NEGATIVE_TO_POSITIVE = {
    # İngilizce
    'bad': ['good', 'nice', 'pleasant'],
    'terrible': ['excellent', 'wonderful', 'great'],
    'awful': ['awesome', 'amazing', 'fantastic'],
    'hate': ['like', 'appreciate', 'enjoy'],
    'dislike': ['like', 'enjoy', 'appreciate'],
    'angry': ['calm', 'composed', 'understanding'],
    'sad': ['happy', 'cheerful', 'joyful'],
    'disappointed': ['satisfied', 'pleased', 'content'],
    'worried': ['confident', 'assured', 'optimistic'],
    'annoyed': ['pleased', 'content', 'satisfied'],
    
    # Türkçe
    'kötü': ['iyi', 'güzel', 'hoş'],
    'berbat': ['mükemmel', 'harika', 'muhteşem'],
    'korkunç': ['harika', 'şahane', 'mükemmel'],
    'nefret': ['sevgi', 'beğeni', 'takdir'],
    'sevmiyorum': ['seviyorum', 'beğeniyorum', 'takdir ediyorum'],
    'kızgın': ['sakin', 'anlayışlı', 'huzurlu'],
    'üzgün': ['mutlu', 'neşeli', 'keyifli'],
    'hayal kırıklığı': ['memnuniyet', 'tatmin', 'hoşnutluk'],
    'endişeli': ['kendinden emin', 'iyimser', 'umutlu'],
    'rahatsız': ['memnun', 'hoşnut', 'tatmin']
}

def improve_negative_text(text, lang_code):
    """
    Negatif metni daha pozitif hale getirmek için öneriler sunar.
    
    Args:
        text (str): Orijinal metin
        lang_code (str): Metnin dil kodu
        
    Returns:
        dict: Orijinal metin ve iyileştirilmiş metin içeren sözlük
    """
    # Metni İngilizce'ye çevir (eğer İngilizce değilse)
    if lang_code != 'en':
        en_text = translate_to_english(text, lang_code)
    else:
        en_text = text
    
    # TextBlob ile duygu analizi yap
    analysis = TextBlob(en_text)
    polarity = analysis.sentiment.polarity
    
    # Eğer metin zaten pozitifse, değişiklik yapma
    if polarity >= 0:
        return {
            'original_text': text,
            'improved_text': text,
            'changes_made': False,
            'message': 'Metin zaten pozitif tonda, değişiklik yapılmadı.'
        }
    
    # Metni kelimelere ayır
    words = word_tokenize(en_text.lower())
    
    # Negatif kelimeleri tespit et ve değiştir
    improved_words = words.copy()
    changes = []
    
    for i, word in enumerate(words):
        if word in NEGATIVE_TO_POSITIVE:
            # Rastgele bir pozitif alternatif seç
            positive_alt = NEGATIVE_TO_POSITIVE[word][0]
            improved_words[i] = positive_alt
            changes.append({
                'original': word,
                'improved': positive_alt,
                'position': i
            })
    
    # İyileştirilmiş metni oluştur
    improved_text = ' '.join(improved_words)
    
    # Eğer orijinal dil İngilizce değilse, geri çevir
    if lang_code != 'en':
        try:
            translator = GoogleTranslator(source='en', target=lang_code)
            improved_text = translator.translate(improved_text)
        except Exception as e:
            print(f"Çeviri hatası: {e}")
    
    return {
        'original_text': text,
        'improved_text': improved_text,
        'changes_made': len(changes) > 0,
        'changes': changes,
        'message': f"{len(changes)} adet negatif ifade daha pozitif alternatiflerle değiştirildi."
    }

def correct_grammar(text, lang_code):
    """
    Metindeki dilbilgisi hatalarını düzeltir.
    
    Args:
        text (str): Orijinal metin
        lang_code (str): Metnin dil kodu
        
    Returns:
        dict: Orijinal metin ve düzeltilmiş metin içeren sözlük
    """
    # Şu anda sadece İngilizce için TextBlob dilbilgisi düzeltmesi destekleniyor
    if lang_code == 'en':
        blob = TextBlob(text)
        corrected_text = str(blob.correct())
        
        # Değişiklik olup olmadığını kontrol et
        changes_made = corrected_text != text
        
        return {
            'original_text': text,
            'corrected_text': corrected_text,
            'changes_made': changes_made,
            'message': 'Dilbilgisi hataları düzeltildi.' if changes_made else 'Dilbilgisi hatası bulunamadı.'
        }
    else:
        # Diğer diller için şu anda destek yok
        return {
            'original_text': text,
            'corrected_text': text,
            'changes_made': False,
            'message': f"Dilbilgisi düzeltmesi şu anda {lang_code} dili için desteklenmiyor."
        }

def suggest_alternative_expressions(text, lang_code, sentiment):
    """
    Metindeki ifadeler için alternatif öneriler sunar.
    
    Args:
        text (str): Orijinal metin
        lang_code (str): Metnin dil kodu
        sentiment (str): Metnin duygu tonu (Pozitif, Negatif, Nötr)
        
    Returns:
        dict: Orijinal metin ve alternatif ifadeler içeren sözlük
    """
    # Metni İngilizce'ye çevir (eğer İngilizce değilse)
    if lang_code != 'en':
        en_text = translate_to_english(text, lang_code)
    else:
        en_text = text
    
    # Metni kelimelere ayır
    words = word_tokenize(en_text.lower())
    
    # Yaygın ifadeler ve alternatifleri
    common_expressions = {
        'good': ['great', 'excellent', 'fantastic', 'wonderful'],
        'bad': ['poor', 'terrible', 'awful', 'unpleasant'],
        'happy': ['joyful', 'delighted', 'pleased', 'thrilled'],
        'sad': ['unhappy', 'depressed', 'gloomy', 'melancholy'],
        'big': ['large', 'enormous', 'massive', 'substantial'],
        'small': ['tiny', 'little', 'miniature', 'compact'],
        'important': ['crucial', 'essential', 'vital', 'significant'],
        'difficult': ['challenging', 'demanding', 'tough', 'arduous'],
        'easy': ['simple', 'straightforward', 'effortless', 'uncomplicated'],
        'interesting': ['fascinating', 'intriguing', 'captivating', 'engaging']
    }
    
    # Türkçe ifadeler
    if lang_code == 'tr':
        common_expressions = {
            'iyi': ['harika', 'mükemmel', 'muhteşem', 'hayranlık verici'],
            'kötü': ['berbat', 'korkunç', 'fena', 'hoş olmayan'],
            'mutlu': ['neşeli', 'sevinçli', 'keyifli', 'memnun'],
            'üzgün': ['mutsuz', 'kederli', 'karamsar', 'melankolik'],
            'büyük': ['kocaman', 'devasa', 'muazzam', 'geniş'],
            'küçük': ['minik', 'ufak', 'minyatür', 'kompakt'],
            'önemli': ['hayati', 'kritik', 'elzem', 'mühim'],
            'zor': ['çetin', 'meşakkatli', 'güç', 'zorlu'],
            'kolay': ['basit', 'zahmetsiz', 'çaba gerektirmeyen', 'anlaşılır'],
            'ilginç': ['merak uyandırıcı', 'etkileyici', 'büyüleyici', 'sürükleyici']
        }
    
    # Alternatif ifadeleri bul
    alternatives = []
    
    for i, word in enumerate(words):
        if word in common_expressions:
            alternatives.append({
                'original': word,
                'alternatives': common_expressions[word],
                'position': i
            })
    
    return {
        'original_text': text,
        'alternatives': alternatives,
        'message': f"{len(alternatives)} ifade için alternatif öneriler bulundu."
    }

def get_text_improvements(text, lang_code, sentiment):
    """
    Metin için tüm iyileştirme önerilerini döndürür.
    
    Args:
        text (str): Orijinal metin
        lang_code (str): Metnin dil kodu
        sentiment (str): Metnin duygu tonu (Pozitif, Negatif, Nötr)
        
    Returns:
        dict: Tüm iyileştirme önerilerini içeren sözlük
    """
    # Negatif metni iyileştir
    improved_text = improve_negative_text(text, lang_code)
    
    # Dilbilgisi düzeltmeleri
    grammar_corrections = correct_grammar(text, lang_code)
    
    # Alternatif ifade önerileri
    alternative_expressions = suggest_alternative_expressions(text, lang_code, sentiment)
    
    return {
        'original_text': text,
        'improved_text': improved_text,
        'grammar_corrections': grammar_corrections,
        'alternative_expressions': alternative_expressions
    }
