"""
Admin paneli için Flask-Admin yapılandırması.
Bu modül, veritabanı tablolarını görüntülemek için bir admin paneli sağlar.
"""

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
import os

# Güvenli ModelView sınıfı - Sadece admin kullanıcıların erişimine izin verir
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Bu sayfaya erişim izniniz yok. Lütfen admin olarak giriş yapın.', 'danger')
        return redirect(url_for('login'))

# Güvenli AdminIndexView sınıfı
class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return super(SecureAdminIndexView, self).index()

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Bu sayfaya erişim izniniz yok. Lütfen admin olarak giriş yapın.', 'danger')
        return redirect(url_for('login'))

# Railway ortamında olup olmadığımızı kontrol et
IS_PRODUCTION = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'

# Admin panelini oluştur
admin = Admin(name='Empathix Admin', template_mode='bootstrap4', index_view=SecureAdminIndexView())

# Kullanıcı model view'ını özelleştir
class UserModelView(SecureModelView):
    column_exclude_list = ['password_hash']  # Şifre hash'ini gösterme
    column_searchable_list = ['username', 'email']
    column_filters = ['is_admin', 'created_at']
    column_editable_list = ['username', 'email', 'is_admin']
    form_excluded_columns = ['password_hash', 'analyses', 'preferences', 'suggestion_feedbacks']
    can_create = True
    can_edit = True
    can_delete = True

# Analiz model view'ını özelleştir
class AnalysisModelView(SecureModelView):
    column_searchable_list = ['text', 'sentiment']
    column_filters = ['sentiment', 'original_language', 'created_at', 'user_id']
    column_editable_list = ['sentiment', 'confidence']
    form_excluded_columns = ['user', 'suggestion_feedbacks']
    can_create = True
    can_edit = True
    can_delete = True

# Kullanıcı Tercihleri model view'ını özelleştir
class UserPreferenceModelView(SecureModelView):
    column_filters = ['user_id', 'preferred_language', 'theme']
    column_editable_list = ['preferred_language', 'theme', 'show_detailed_emotions', 'show_text_suggestions']
    form_excluded_columns = ['user']
    can_create = True
    can_edit = True
    can_delete = True

# Dil İstatistikleri model view'ını özelleştir
class LanguageStatsModelView(SecureModelView):
    column_filters = ['language_code', 'language_name']
    column_editable_list = ['count']
    can_create = True
    can_edit = True
    can_delete = True

# Duygu İstatistikleri model view'ını özelleştir
class SentimentStatsModelView(SecureModelView):
    column_filters = ['sentiment']
    column_editable_list = ['count']
    can_create = True
    can_edit = True
    can_delete = True

# Duygu Kategorileri İstatistikleri model view'ını özelleştir
class EmotionStatsModelView(SecureModelView):
    column_filters = ['emotion']
    column_editable_list = ['count', 'average_intensity']
    can_create = True
    can_edit = True
    can_delete = True

# Metin Önerisi Geri Bildirimleri model view'ını özelleştir
class TextSuggestionFeedbackModelView(SecureModelView):
    column_filters = ['user_id', 'is_helpful', 'created_at']
    column_editable_list = ['is_helpful']
    form_excluded_columns = ['user', 'analysis']
    can_create = True
    can_edit = True
    can_delete = True

def init_admin(app, db):
    """
    Admin panelini uygulama ve veritabanı ile başlatır.
    
    Args:
        app: Flask uygulaması
        db: SQLAlchemy veritabanı nesnesi
    """
    # Railway'de çalışırken admin panelini devre dışı bırak
    if IS_PRODUCTION:
        return
        
    # Modelleri içeri aktar
    from models import User, Analysis, LanguageStats, SentimentStats, UserPreference, TextSuggestionFeedback, EmotionStats
    admin.init_app(app)
    
    # Model view'ları ekle
    admin.add_view(UserModelView(User, db.session, name='Kullanıcılar'))
    admin.add_view(AnalysisModelView(Analysis, db.session, name='Analizler'))
    admin.add_view(UserPreferenceModelView(UserPreference, db.session, name='Kullanıcı Tercihleri'))
    admin.add_view(LanguageStatsModelView(LanguageStats, db.session, name='Dil İstatistikleri'))
    admin.add_view(SentimentStatsModelView(SentimentStats, db.session, name='Duygu İstatistikleri'))
    admin.add_view(EmotionStatsModelView(EmotionStats, db.session, name='Duygu Kategorileri'))
    admin.add_view(TextSuggestionFeedbackModelView(TextSuggestionFeedback, db.session, name='Metin Önerisi Geri Bildirimleri'))
