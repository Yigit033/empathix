from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')
    preferences = db.relationship('UserPreference', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    original_language = db.Column(db.String(10))
    sentiment = db.Column(db.String(20), nullable=False)  # Genel duygu (Pozitif, Negatif, Nötr)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Detaylı duygu kategorileri
    happiness = db.Column(db.Float, default=0.0)  # Mutluluk skoru
    sadness = db.Column(db.Float, default=0.0)    # Üzüntü skoru
    anger = db.Column(db.Float, default=0.0)      # Öfke skoru
    fear = db.Column(db.Float, default=0.0)       # Korku skoru
    surprise = db.Column(db.Float, default=0.0)   # Şaşkınlık skoru
    
    # Duygu yoğunluğu (1: Hafif, 2: Orta, 3: Yüksek)
    intensity = db.Column(db.Integer, default=1)
    
    # Kullanıcı geri bildirimleri
    user_feedback = db.Column(db.Boolean, default=None)  # True: Doğru analiz, False: Yanlış analiz
    user_feedback_text = db.Column(db.Text)  # Kullanıcının geri bildirim metni
    
    # Metin önerileri ve düzeltmeleri
    improved_text = db.Column(db.Text)  # Düzeltilmiş/iyileştirilmiş metin
    grammar_corrections = db.Column(db.Text)  # Dilbilgisi düzeltmeleri (JSON formatında)
    alternative_expressions = db.Column(db.Text)  # Alternatif ifadeler (JSON formatında)
    
    def __repr__(self):
        return f'<Analysis {self.id}>'
    
    def get_intensity_label(self):
        """Duygu yoğunluğu etiketini döndürür"""
        labels = {1: "Hafif", 2: "Orta", 3: "Yüksek"}
        return labels.get(self.intensity, "Belirsiz")
    
    def get_primary_emotion(self):
        """En baskın duygu kategorisini döndürür"""
        emotions = {
            "Mutluluk": self.happiness,
            "Üzüntü": self.sadness,
            "Öfke": self.anger,
            "Korku": self.fear,
            "Şaşkınlık": self.surprise
        }
        return max(emotions, key=emotions.get)

class LanguageStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_code = db.Column(db.String(10), nullable=False)
    language_name = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<LanguageStats {self.language_name}>'

class SentimentStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentiment = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<SentimentStats {self.sentiment}>'

class EmotionStats(db.Model):
    """Detaylı duygu kategorileri istatistikleri"""
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String(20), nullable=False)  # Mutluluk, Üzüntü, Öfke, Korku, Şaşkınlık
    count = db.Column(db.Integer, default=0)
    average_intensity = db.Column(db.Float, default=0.0)  # Ortalama yoğunluk
    
    def __repr__(self):
        return f'<EmotionStats {self.emotion}>'

class UserPreference(db.Model):
    """Kullanıcı tercihleri"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    preferred_language = db.Column(db.String(10), default='tr')  # Tercih edilen dil
    show_detailed_emotions = db.Column(db.Boolean, default=True)  # Detaylı duygu kategorilerini göster
    show_text_suggestions = db.Column(db.Boolean, default=True)  # Metin önerilerini göster
    theme = db.Column(db.String(20), default='light')  # Tema tercihi (light/dark)
    
    def __repr__(self):
        return f'<UserPreference {self.user_id}>'

class TextSuggestionFeedback(db.Model):
    """Metin önerileri için kullanıcı geri bildirimleri"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))
    original_text = db.Column(db.Text, nullable=False)
    suggested_text = db.Column(db.Text, nullable=False)
    is_helpful = db.Column(db.Boolean)  # Kullanıcı öneriyi faydalı buldu mu?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    analysis = db.relationship('Analysis', backref='suggestion_feedbacks')
    user = db.relationship('User', backref='suggestion_feedbacks')
    
    def __repr__(self):
        return f'<TextSuggestionFeedback {self.id}>'
