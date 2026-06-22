"""
Internationalization (i18n) support for multi-language support
"""

import json
import os
from flask import session, request
import logging

logger = logging.getLogger(__name__)

# Define supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'hi': 'हिंदी',
    'zh': '中文'
}

# Translation dictionary - can be expanded
TRANSLATIONS = {
    'en': {
        'home': 'Home',
        'about': 'About',
        'login': 'Login',
        'logout': 'Logout',
        'signup': 'Sign Up',
        'profile': 'Profile',
        'history': 'History',
        'chatbot': 'Chatbot',
        'settings': 'Settings',
        'diabetes_predictor': 'Diabetes Predictor',
        'welcome': 'Welcome',
        'predict': 'Predict',
        'result': 'Result',
        'error': 'Error',
        'success': 'Success',
        'pregnancies': 'Pregnancies',
        'glucose': 'Glucose Level (mg/dL)',
        'blood_pressure': 'Blood Pressure (mmHg)',
        'skin_thickness': 'Skin Thickness (mm)',
        'insulin': 'Insulin Level (IU/mL)',
        'bmi': 'BMI (kg/m²)',
        'dpf': 'Diabetes Pedigree Function',
        'age': 'Age (years)',
        'submit': 'Submit',
        'reset': 'Reset',
        'back': 'Back',
        'positive': 'Positive',
        'negative': 'Negative',
        'confidence': 'Confidence',
        'recommendations': 'Recommendations',
        'export': 'Export',
        'csv': 'CSV',
        'pdf': 'PDF',
        'trends': 'Trends',
        'statistics': 'Statistics',
        'language': 'Language',
        'theme': 'Theme',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode',
    },
    'es': {
        'home': 'Inicio',
        'about': 'Acerca de',
        'login': 'Iniciar sesión',
        'logout': 'Cerrar sesión',
        'signup': 'Registrarse',
        'profile': 'Perfil',
        'history': 'Historial',
        'chatbot': 'Chatbot',
        'settings': 'Configuración',
        'diabetes_predictor': 'Predictor de Diabetes',
        'welcome': 'Bienvenido',
        'predict': 'Predecir',
        'result': 'Resultado',
        'error': 'Error',
        'success': 'Éxito',
        'pregnancies': 'Embarazos',
        'glucose': 'Nivel de Glucosa (mg/dL)',
        'blood_pressure': 'Presión Arterial (mmHg)',
        'skin_thickness': 'Grosor de la Piel (mm)',
        'insulin': 'Nivel de Insulina (IU/mL)',
        'bmi': 'IMC (kg/m²)',
        'dpf': 'Función de Pedigree de Diabetes',
        'age': 'Edad (años)',
        'submit': 'Enviar',
        'reset': 'Restablecer',
        'back': 'Atrás',
        'positive': 'Positivo',
        'negative': 'Negativo',
        'confidence': 'Confianza',
        'recommendations': 'Recomendaciones',
        'export': 'Exportar',
        'csv': 'CSV',
        'pdf': 'PDF',
        'trends': 'Tendencias',
        'statistics': 'Estadísticas',
        'language': 'Idioma',
        'theme': 'Tema',
        'dark_mode': 'Modo Oscuro',
        'light_mode': 'Modo Claro',
    },
    'fr': {
        'home': 'Accueil',
        'about': 'À propos',
        'login': 'Connexion',
        'logout': 'Déconnexion',
        'signup': 'S\'inscrire',
        'profile': 'Profil',
        'history': 'Historique',
        'chatbot': 'Chatbot',
        'settings': 'Paramètres',
        'diabetes_predictor': 'Prédicteur de Diabète',
        'welcome': 'Bienvenue',
        'predict': 'Prédire',
        'result': 'Résultat',
        'error': 'Erreur',
        'success': 'Succès',
        'pregnancies': 'Grossesses',
        'glucose': 'Niveau de Glucose (mg/dL)',
        'blood_pressure': 'Pression Artérielle (mmHg)',
        'skin_thickness': 'Épaisseur de la Peau (mm)',
        'insulin': 'Niveau d\'Insuline (IU/mL)',
        'bmi': 'IMC (kg/m²)',
        'dpf': 'Fonction de Risque Génétique du Diabète',
        'age': 'Âge (ans)',
        'submit': 'Soumettre',
        'reset': 'Réinitialiser',
        'back': 'Retour',
        'positive': 'Positif',
        'negative': 'Négatif',
        'confidence': 'Confiance',
        'recommendations': 'Recommandations',
        'export': 'Exporter',
        'csv': 'CSV',
        'pdf': 'PDF',
        'trends': 'Tendances',
        'statistics': 'Statistiques',
        'language': 'Langue',
        'theme': 'Thème',
        'dark_mode': 'Mode Sombre',
        'light_mode': 'Mode Clair',
    },
    'de': {
        'home': 'Startseite',
        'about': 'Über uns',
        'login': 'Anmelden',
        'logout': 'Abmelden',
        'signup': 'Registrieren',
        'profile': 'Profil',
        'history': 'Verlauf',
        'chatbot': 'Chatbot',
        'settings': 'Einstellungen',
        'diabetes_predictor': 'Diabetes-Prädiktor',
        'welcome': 'Willkommen',
        'predict': 'Vorhersagen',
        'result': 'Ergebnis',
        'error': 'Fehler',
        'success': 'Erfolg',
        'pregnancies': 'Schwangerschaften',
        'glucose': 'Glukosespiegel (mg/dL)',
        'blood_pressure': 'Blutdruck (mmHg)',
        'skin_thickness': 'Hautdicke (mm)',
        'insulin': 'Insulinspiegel (IU/mL)',
        'bmi': 'BMI (kg/m²)',
        'dpf': 'Diabetes-Pedigree-Funktion',
        'age': 'Alter (Jahre)',
        'submit': 'Absenden',
        'reset': 'Zurücksetzen',
        'back': 'Zurück',
        'positive': 'Positiv',
        'negative': 'Negativ',
        'confidence': 'Vertrauen',
        'recommendations': 'Empfehlungen',
        'export': 'Exportieren',
        'csv': 'CSV',
        'pdf': 'PDF',
        'trends': 'Trends',
        'statistics': 'Statistiken',
        'language': 'Sprache',
        'theme': 'Design',
        'dark_mode': 'Dunkler Modus',
        'light_mode': 'Heller Modus',
    },
    'hi': {
        'home': 'होम',
        'about': 'परिचय',
        'login': 'लॉगिन',
        'logout': 'लॉगआउट',
        'signup': 'साइन अप',
        'profile': 'प्रोफाइल',
        'history': 'इतिहास',
        'chatbot': 'चैटबॉट',
        'settings': 'सेटिंग्स',
        'diabetes_predictor': 'मधुमेह भविष्यवक्ता',
        'welcome': 'स्वागत है',
        'predict': 'भविष्यवाणी करें',
        'result': 'परिणाम',
        'error': 'त्रुटि',
        'success': 'सफलता',
        'pregnancies': 'गर्भधारण',
        'glucose': 'ग्लूकोज स्तर (mg/dL)',
        'blood_pressure': 'रक्त दबाव (mmHg)',
        'skin_thickness': 'त्वचा की मोटाई (mm)',
        'insulin': 'इंसुलिन स्तर (IU/mL)',
        'bmi': 'BMI (kg/m²)',
        'dpf': 'मधुमेह वंशावली कार्य',
        'age': 'आयु (वर्ष)',
        'submit': 'जमा करें',
        'reset': 'रीसेट करें',
        'back': 'वापस',
        'positive': 'सकारात्मक',
        'negative': 'नकारात्मक',
        'confidence': 'आत्मविश्वास',
        'recommendations': 'सिफारिशें',
        'export': 'निर्यात',
        'csv': 'CSV',
        'pdf': 'PDF',
        'trends': 'रुझान',
        'statistics': 'आंकड़े',
        'language': 'भाषा',
        'theme': 'थीम',
        'dark_mode': 'डार्क मोड',
        'light_mode': 'लाइट मोड',
    },
    'zh': {
        'home': '主页',
        'about': '关于',
        'login': '登录',
        'logout': '退出',
        'signup': '注册',
        'profile': '个人资料',
        'history': '历史记录',
        'chatbot': '聊天机器人',
        'settings': '设置',
        'diabetes_predictor': '糖尿病预测器',
        'welcome': '欢迎',
        'predict': '预测',
        'result': '结果',
        'error': '错误',
        'success': '成功',
        'pregnancies': '怀孕',
        'glucose': '血糖水平 (mg/dL)',
        'blood_pressure': '血压 (mmHg)',
        'skin_thickness': '皮肤厚度 (mm)',
        'insulin': '胰岛素水平 (IU/mL)',
        'bmi': '身体质量指数 (kg/m²)',
        'dpf': '糖尿病谱系函数',
        'age': '年龄 (岁)',
        'submit': '提交',
        'reset': '重置',
        'back': '返回',
        'positive': '阳性',
        'negative': '阴性',
        'confidence': '置信度',
        'recommendations': '建议',
        'export': '导出',
        'csv': 'CSV',
        'pdf': 'PDF',
        'trends': '趋势',
        'statistics': '统计',
        'language': '语言',
        'theme': '主题',
        'dark_mode': '深色模式',
        'light_mode': '浅色模式',
    }
}


def get_current_language():
    """Get current language from session or user preference"""
    # Check session first
    if 'language' in session:
        return session['language']
    
    # Check user preference if authenticated
    from flask_login import current_user
    if current_user.is_authenticated:
        return current_user.language or 'en'
    
    # Check browser language preference
    best_match = request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys())
    return best_match or 'en'


def translate(key, lang=None):
    """Translate a key to the specified language"""
    if lang is None:
        lang = get_current_language()
    
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))


def set_language(lang):
    """Set the current language in session"""
    if lang in SUPPORTED_LANGUAGES:
        session['language'] = lang
        return True
    return False


def get_language_list():
    """Get list of all supported languages"""
    return SUPPORTED_LANGUAGES
