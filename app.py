from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from datetime import datetime

from models import db, User, Analysis, LanguageStats, SentimentStats, UserPreference, TextSuggestionFeedback, EmotionStats
from forms import LoginForm, RegistrationForm, AnalysisForm
from sentiment_analyzer import analyze_sentiment, SUPPORTED_LANGUAGES
from stats import get_sentiment_distribution, get_language_distribution, get_time_series_analysis, update_stats
from text_improver import get_text_improvements, improve_negative_text, correct_grammar, suggest_alternative_expressions
from user_preferences import get_or_create_user_preferences, update_user_preferences, record_analysis_feedback
from user_preferences import record_text_suggestion_feedback, get_user_analysis_patterns, get_personalized_recommendations, adapt_analysis_to_preferences
from admin import init_admin

# Flask uygulamasını oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'gelistirilebilir-gizli-anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///empathix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# Veritabanı ve giriş yöneticisini başlat
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bu sayfayı görüntülemek için lütfen giriş yapın.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Veritabanını oluştur
@app.before_first_request
def create_tables():
    db.create_all()
    # Varsayılan duygu istatistiklerini ekle
    if SentimentStats.query.count() == 0:
        db.session.add(SentimentStats(sentiment="Pozitif", count=0))
        db.session.add(SentimentStats(sentiment="Negatif", count=0))
        db.session.add(SentimentStats(sentiment="Nötr", count=0))
        db.session.commit()
    
    # Varsayılan duygu kategorileri istatistiklerini ekle
    if EmotionStats.query.count() == 0:
        db.session.add(EmotionStats(emotion="happiness", count=0))
        db.session.add(EmotionStats(emotion="sadness", count=0))
        db.session.add(EmotionStats(emotion="anger", count=0))
        db.session.add(EmotionStats(emotion="fear", count=0))
        db.session.add(EmotionStats(emotion="surprise", count=0))
        db.session.commit()

@app.route('/')
def index():
    form = AnalysisForm()
    
    # Kullanıcı tercihleri
    user_preferences = None
    if current_user.is_authenticated:
        user_preferences = get_or_create_user_preferences(current_user.id)
    
    return render_template('index.html', form=form, supported_languages=SUPPORTED_LANGUAGES, preferences=user_preferences)

@app.route('/analyze', methods=['POST'])
def analyze():
    form = AnalysisForm()
    result = None
    text_improvements = None
    
    if form.validate_on_submit():
        text = form.text.data
        
        if text.strip():  # Eğer metin boş değilse
            try:
                # Duygu analizi yap
                result = analyze_sentiment(text)
                
                # Analiz edilen metni result sözlüğüne ekle
                result['text'] = text
                
                # Kullanıcı giriş yapmışsa analizi kaydet ve kullanıcı tercihlerine göre uyarla
                if current_user.is_authenticated:
                    # Kullanıcı tercihlerine göre sonuçları uyarla
                    adapted_result = adapt_analysis_to_preferences(result, current_user.id)
                    
                    # Analizi veritabanına kaydet
                    analysis = Analysis(
                        text=text,
                        original_language=result['language_code'],
                        sentiment=result['sentiment'],
                        confidence=result['confidence'],
                        user_id=current_user.id,
                        happiness=result['emotion_scores']['happiness'],
                        sadness=result['emotion_scores']['sadness'],
                        anger=result['emotion_scores']['anger'],
                        fear=result['emotion_scores']['fear'],
                        surprise=result['emotion_scores']['surprise'],
                        intensity=result['intensity']
                    )
                    db.session.add(analysis)
                    
                    # İstatistikleri güncelle
                    update_stats(result)
                    
                    db.session.commit()
                    
                    # Analiz ID'sini result sözlüğüne ekle
                    result['analysis_id'] = analysis.id
                    
                    # Kullanıcı tercihleri
                    user_preferences = get_or_create_user_preferences(current_user.id)
                    
                    # Metin önerileri gösterilecekse
                    if user_preferences.show_text_suggestions:
                        text_improvements = get_text_improvements(text, result['language_code'], result['sentiment'])
                    
                    # Sonuçları kullanıcı tercihlerine göre uyarla
                    result = adapted_result
                    # Analiz ID'sini adapted_result'a da ekle
                    result['analysis_id'] = analysis.id
                
            except Exception as e:
                # Hata durumunda
                result = {
                    'text': text,
                    'sentiment': "Hata",
                    'confidence': 0,
                    'error': str(e)
                }
    
    return render_template('result.html', result=result, form=form, text_improvements=text_improvements)

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Kullanıcı tercihlerini görüntüleme ve güncelleme."""
    user_preferences = get_or_create_user_preferences(current_user.id)
    
    if request.method == 'POST':
        preferences_data = {
            'preferred_language': request.form.get('preferred_language'),
            'show_detailed_emotions': 'show_detailed_emotions' in request.form,
            'show_text_suggestions': 'show_text_suggestions' in request.form,
            'theme': request.form.get('theme')
        }
        
        update_user_preferences(current_user.id, preferences_data)
        flash('Tercihleriniz başarıyla güncellendi.', 'success')
        return redirect(url_for('preferences'))
    
    return render_template('preferences.html', preferences=user_preferences, supported_languages=SUPPORTED_LANGUAGES)

@app.route('/feedback/<int:analysis_id>', methods=['POST'])
@login_required
def submit_feedback(analysis_id):
    """Analiz için geri bildirim gönderme."""
    feedback_value = request.form.get('feedback') == 'true'
    feedback_text = request.form.get('feedback_text')
    
    analysis = record_analysis_feedback(analysis_id, feedback_value, feedback_text)
    
    if analysis:
        flash('Geri bildiriminiz için teşekkürler!', 'success')
    else:
        flash('Geri bildirim kaydedilirken bir hata oluştu.', 'danger')
    
    return redirect(url_for('history'))

@app.route('/text_suggestion_feedback/<int:analysis_id>', methods=['POST'])
@login_required
def submit_text_suggestion_feedback(analysis_id):
    """Metin önerisi için geri bildirim gönderme."""
    original_text = request.form.get('original_text')
    suggested_text = request.form.get('suggested_text')
    is_helpful = request.form.get('is_helpful') == 'true'
    
    feedback = record_text_suggestion_feedback(analysis_id, original_text, suggested_text, is_helpful)
    
    if feedback:
        flash('Öneri geri bildiriminiz için teşekkürler!', 'success')
    else:
        flash('Geri bildirim kaydedilirken bir hata oluştu.', 'danger')
    
    return redirect(url_for('history'))

@app.route('/recommendations')
@login_required
def recommendations():
    """Kullanıcı için kişiselleştirilmiş öneriler."""
    recommendations = get_personalized_recommendations(current_user.id)
    return render_template('recommendations.html', recommendations=recommendations)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Tebrikler, başarıyla kayıt oldunuz! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Geçersiz kullanıcı adı veya şifre', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        flash(f'Hoş geldiniz, {user.username}!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Kullanıcının analizlerini al
    user_analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).limit(5).all()
    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
    
    # İstatistikleri oluştur
    sentiment_chart = get_sentiment_distribution(current_user.id) if total_analyses > 0 else None
    language_chart = get_language_distribution(current_user.id) if total_analyses > 0 else None
    time_series_chart = get_time_series_analysis(days=30, user_id=current_user.id) if total_analyses > 0 else None
    
    return render_template('profile.html', 
                          user=current_user,
                          analyses=user_analyses,
                          total_analyses=total_analyses,
                          sentiment_chart=sentiment_chart,
                          language_chart=language_chart,
                          time_series_chart=time_series_chart)

@app.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(
        Analysis.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('history.html', analyses=analyses)

@app.route('/stats')
@login_required
def stats():
    # Zaman aralığı parametresini al
    time_range = request.args.get('time_range', '30')
    try:
        time_range = int(time_range)
    except ValueError:
        time_range = 30
    
    # Geçerli aralıkları kontrol et
    valid_ranges = [7, 30, 90, 180, 365]
    if time_range not in valid_ranges:
        time_range = 30
    
    # Genel istatistikleri al
    total_analyses = Analysis.query.count()
    total_users = User.query.count()
    
    # Duygu istatistikleri
    sentiment_query = db.session.query(
        SentimentStats.sentiment, 
        SentimentStats.count
    ).order_by(SentimentStats.count.desc())
    
    sentiment_results = sentiment_query.all()
    sentiment_stats = []
    for sentiment, count in sentiment_results:
        percentage = round((count / total_analyses * 100), 1) if total_analyses > 0 else 0
        sentiment_stats.append((sentiment, count, percentage))
    
    # Dil istatistikleri
    language_query = db.session.query(
        LanguageStats.language_code, 
        LanguageStats.language_name, 
        LanguageStats.count
    ).order_by(LanguageStats.count.desc())
    
    language_results = language_query.all()
    language_stats = []
    for code, name, count in language_results:
        percentage = round((count / total_analyses * 100), 1) if total_analyses > 0 else 0
        language_stats.append((name, count, percentage))
    
    # Grafikleri oluştur
    sentiment_chart = get_sentiment_distribution() if total_analyses > 0 else None
    language_chart = get_language_distribution() if total_analyses > 0 else None
    time_series_chart = get_time_series_analysis(days=time_range) if total_analyses > 0 else None
    
    return render_template('stats.html',
                          total_analyses=total_analyses,
                          total_users=total_users,
                          sentiment_stats=sentiment_stats,
                          language_stats=language_stats,
                          sentiment_chart=sentiment_chart,
                          language_chart=language_chart,
                          time_series_chart=time_series_chart,
                          time_range=time_range)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for sentiment analysis."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        result = analyze_sentiment(text)
        
        # Kullanıcı kimliği varsa analizi kaydet
        user_id = data.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                analysis = Analysis(
                    text=text,
                    original_language=result['language_code'],
                    sentiment=result['sentiment'],
                    confidence=result['confidence'],
                    user_id=user.id,
                    happiness=result['emotion_scores']['happiness'],
                    sadness=result['emotion_scores']['sadness'],
                    anger=result['emotion_scores']['anger'],
                    fear=result['emotion_scores']['fear'],
                    surprise=result['emotion_scores']['surprise'],
                    intensity=result['intensity']
                )
                db.session.add(analysis)
                update_stats(result)
                db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/text_improvements', methods=['POST'])
def api_text_improvements():
    """API endpoint for text improvements."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    text = data.get('text')
    lang_code = data.get('language_code', 'en')
    sentiment = data.get('sentiment', 'Nötr')
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        improvements = get_text_improvements(text, lang_code, sentiment)
        return jsonify(improvements)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Navbar'da aktif sayfayı belirlemek için context processor
@app.context_processor
def inject_active_page():
    def is_active_page(endpoint):
        return request.endpoint == endpoint
    return {'is_active_page': is_active_page}

if __name__ == '__main__':
    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all()
    
    # Admin panelini başlat
    from admin import init_admin
    init_admin(app, db)
    
    # Uygulamayı çalıştır
    app.run(debug=True)
