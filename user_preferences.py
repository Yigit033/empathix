"""
Kullanıcı tercihleri ve kişiselleştirilmiş öğrenme için modül.
Bu modül, kullanıcı geri bildirimleri ile analiz kalitesini artırma, 
kullanıcı tercihlerine göre özelleştirilmiş sonuçlar ve 
kullanıcı davranışlarına göre öneriler sunma işlevlerini sağlar.
"""

from models import db, User, Analysis, UserPreference, TextSuggestionFeedback
from sqlalchemy import func, desc
import json

def get_or_create_user_preferences(user_id):
    """
    Kullanıcı tercihlerini getirir, yoksa oluşturur.
    
    Args:
        user_id (int): Kullanıcı ID'si
        
    Returns:
        UserPreference: Kullanıcı tercihleri nesnesi
    """
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreference(user_id=user_id)
        db.session.add(preferences)
        db.session.commit()
    
    return preferences

def update_user_preferences(user_id, preferences_data):
    """
    Kullanıcı tercihlerini günceller.
    
    Args:
        user_id (int): Kullanıcı ID'si
        preferences_data (dict): Güncellenecek tercihler
        
    Returns:
        UserPreference: Güncellenmiş kullanıcı tercihleri nesnesi
    """
    preferences = get_or_create_user_preferences(user_id)
    
    # Tercihleri güncelle
    if 'preferred_language' in preferences_data:
        preferences.preferred_language = preferences_data['preferred_language']
    
    if 'show_detailed_emotions' in preferences_data:
        preferences.show_detailed_emotions = preferences_data['show_detailed_emotions']
    
    if 'show_text_suggestions' in preferences_data:
        preferences.show_text_suggestions = preferences_data['show_text_suggestions']
    
    if 'theme' in preferences_data:
        preferences.theme = preferences_data['theme']
    
    db.session.commit()
    return preferences

def record_analysis_feedback(analysis_id, feedback_value, feedback_text=None):
    """
    Analiz için kullanıcı geri bildirimini kaydeder.
    
    Args:
        analysis_id (int): Analiz ID'si
        feedback_value (bool): True: Doğru analiz, False: Yanlış analiz
        feedback_text (str, optional): Kullanıcının geri bildirim metni
        
    Returns:
        Analysis: Güncellenmiş analiz nesnesi
    """
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        return None
    
    analysis.user_feedback = feedback_value
    
    if feedback_text:
        analysis.user_feedback_text = feedback_text
    
    db.session.commit()
    return analysis

def record_text_suggestion_feedback(analysis_id, original_text, suggested_text, is_helpful):
    """
    Metin önerisi için kullanıcı geri bildirimini kaydeder.
    
    Args:
        analysis_id (int): Analiz ID'si
        original_text (str): Orijinal metin
        suggested_text (str): Önerilen metin
        is_helpful (bool): Kullanıcı öneriyi faydalı buldu mu?
        
    Returns:
        TextSuggestionFeedback: Kaydedilen geri bildirim nesnesi
    """
    feedback = TextSuggestionFeedback(
        analysis_id=analysis_id,
        original_text=original_text,
        suggested_text=suggested_text,
        is_helpful=is_helpful
    )
    
    db.session.add(feedback)
    db.session.commit()
    return feedback

def get_user_analysis_patterns(user_id):
    """
    Kullanıcının analiz kalıplarını ve eğilimlerini getirir.
    
    Args:
        user_id (int): Kullanıcı ID'si
        
    Returns:
        dict: Kullanıcının analiz kalıpları ve eğilimleri
    """
    # Kullanıcının en sık kullandığı dilleri getir
    top_languages = db.session.query(
        Analysis.original_language,
        func.count(Analysis.id).label('count')
    ).filter_by(user_id=user_id).group_by(
        Analysis.original_language
    ).order_by(desc('count')).limit(3).all()
    
    # Kullanıcının en sık aldığı duygu sonuçlarını getir
    top_sentiments = db.session.query(
        Analysis.sentiment,
        func.count(Analysis.id).label('count')
    ).filter_by(user_id=user_id).group_by(
        Analysis.sentiment
    ).order_by(desc('count')).limit(3).all()
    
    # Kullanıcının en sık aldığı detaylı duygu kategorilerini getir
    analyses = Analysis.query.filter_by(user_id=user_id).all()
    emotion_counts = {
        'happiness': 0,
        'sadness': 0,
        'anger': 0,
        'fear': 0,
        'surprise': 0
    }
    
    for analysis in analyses:
        if analysis.happiness > 0.5:
            emotion_counts['happiness'] += 1
        if analysis.sadness > 0.5:
            emotion_counts['sadness'] += 1
        if analysis.anger > 0.5:
            emotion_counts['anger'] += 1
        if analysis.fear > 0.5:
            emotion_counts['fear'] += 1
        if analysis.surprise > 0.5:
            emotion_counts['surprise'] += 1
    
    top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        'top_languages': [(lang, count) for lang, count in top_languages],
        'top_sentiments': [(sentiment, count) for sentiment, count in top_sentiments],
        'top_emotions': top_emotions
    }

def get_personalized_recommendations(user_id):
    """
    Kullanıcı için kişiselleştirilmiş öneriler sunar.
    
    Args:
        user_id (int): Kullanıcı ID'si
        
    Returns:
        dict: Kişiselleştirilmiş öneriler
    """
    # Kullanıcının analiz kalıplarını getir
    patterns = get_user_analysis_patterns(user_id)
    
    recommendations = []
    
    # Dil kullanımına göre öneriler
    if patterns['top_languages']:
        top_language = patterns['top_languages'][0][0]
        recommendations.append({
            'type': 'language',
            'message': f"En çok {top_language} dilinde analiz yapıyorsunuz. Bu dilde daha doğru sonuçlar için tercihlerde bu dili varsayılan olarak ayarlayabilirsiniz."
        })
    
    # Duygu durumuna göre öneriler
    if patterns['top_sentiments']:
        top_sentiment = patterns['top_sentiments'][0][0]
        if top_sentiment == 'Negatif':
            recommendations.append({
                'type': 'sentiment',
                'message': "Analizlerinizde genellikle negatif sonuçlar görünüyor. Metin önerileri özelliğini kullanarak daha pozitif ifadeler için öneriler alabilirsiniz."
            })
        elif top_sentiment == 'Pozitif':
            recommendations.append({
                'type': 'sentiment',
                'message': "Analizlerinizde genellikle pozitif sonuçlar görünüyor. Bu olumlu yaklaşımınızı sürdürmenizi öneririz!"
            })
    
    # Detaylı duygu kategorilerine göre öneriler
    if patterns['top_emotions']:
        top_emotion = patterns['top_emotions'][0][0]
        if top_emotion == 'anger':
            recommendations.append({
                'type': 'emotion',
                'message': "Metinlerinizde öfke duygusu öne çıkıyor. Daha sakin ifadeler kullanmayı deneyebilirsiniz."
            })
        elif top_emotion == 'fear':
            recommendations.append({
                'type': 'emotion',
                'message': "Metinlerinizde korku duygusu öne çıkıyor. Daha güvenli ve olumlu ifadeler kullanmayı deneyebilirsiniz."
            })
        elif top_emotion == 'sadness':
            recommendations.append({
                'type': 'emotion',
                'message': "Metinlerinizde üzüntü duygusu öne çıkıyor. Daha neşeli ve olumlu ifadeler kullanmayı deneyebilirsiniz."
            })
    
    # Kullanıcının analiz sayısına göre öneriler
    analysis_count = Analysis.query.filter_by(user_id=user_id).count()
    if analysis_count < 5:
        recommendations.append({
            'type': 'usage',
            'message': "Daha doğru kişiselleştirilmiş öneriler için daha fazla analiz yapmanızı öneririz."
        })
    elif analysis_count > 20:
        recommendations.append({
            'type': 'usage',
            'message': "Düzenli olarak analiz yapıyorsunuz! İstatistikler sayfasından duygu ve dil dağılımlarınızı inceleyebilirsiniz."
        })
    
    return {
        'recommendations': recommendations,
        'analysis_count': analysis_count,
        'patterns': patterns
    }

def adapt_analysis_to_preferences(analysis_result, user_id):
    """
    Analiz sonucunu kullanıcı tercihlerine göre uyarlar.
    
    Args:
        analysis_result (dict): Analiz sonucu
        user_id (int): Kullanıcı ID'si
        
    Returns:
        dict: Kullanıcı tercihlerine göre uyarlanmış analiz sonucu
    """
    preferences = get_or_create_user_preferences(user_id)
    adapted_result = analysis_result.copy()
    
    # Önemli alanları koru
    important_fields = ['text', 'analysis_id']
    for field in important_fields:
        if field in analysis_result:
            adapted_result[field] = analysis_result[field]
    
    # Detaylı duygu kategorilerini gösterme tercihi
    if not preferences.show_detailed_emotions:
        if 'emotion_scores' in adapted_result:
            del adapted_result['emotion_scores']
        if 'highlighted_emotions' in adapted_result:
            del adapted_result['highlighted_emotions']
    
    # Tercih edilen dile göre uyarlama
    if preferences.preferred_language != 'tr' and preferences.preferred_language != analysis_result.get('language_code'):
        # Burada tercih edilen dile çeviri yapılabilir
        # Şu an için bu özellik eklenmedi
        pass
    
    return adapted_result
