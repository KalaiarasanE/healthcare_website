# Importing essential libraries
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_required, current_user
import pickle
import numpy as np
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import models and blueprints
from models import db, User, PredictionHistory
from auth_routes import auth_bp
from history_routes import history_bp
from chatbot_routes import chatbot_bp
from i18n import get_current_language, translate, set_language, get_language_list

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
from config import get_config
config = get_config()

# Create Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load the Random Forest Classifier model
try:
    filename = 'diabetes-prediction-rfc-model.pkl'
    classifier = pickle.load(open(filename, 'rb'))
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    classifier = None

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(history_bp)
app.register_blueprint(chatbot_bp)

# Before request handler for language and theme
@app.before_request
def before_request():
    """Set up language and theme before each request"""
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=24)
    
    # Set language from request or session
    lang = request.args.get('lang')
    if lang:
        set_language(lang)
    
    # Make translate function available in templates
    session['current_language'] = get_current_language()


# Context processor to make functions available in templates
@app.context_processor
def inject_functions():
    return {
        'translate': translate,
        'get_current_language': get_current_language,
        'get_language_list': get_language_list,
        'current_user': current_user
    }


# Health recommendations based on values
def get_health_recommendations(preg, glucose, bp, st, insulin, bmi, dpf, age):
    recommendations = []
    
    if glucose > 140:
        recommendations.append("Reduce sugar and refined carbohydrate intake")
    if bp > 140 or bp < 60:
        recommendations.append("Monitor your blood pressure regularly")
    if bmi > 30:
        recommendations.append("Regular exercise and balanced diet recommended")
    if age > 45:
        recommendations.append("Increase health checkups frequency")
    if insulin > 150:
        recommendations.append("Consult an endocrinologist for insulin management")
    
    if not recommendations:
        recommendations.append("Maintain your healthy lifestyle with regular exercise and balanced diet")
    
    return recommendations


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        if classifier is None:
            return render_template('error.html', error="Model not loaded. Please try again later."), 500
        
        # Get form data
        preg = request.form.get('pregnancies')
        glucose = request.form.get('glucose')
        bp = request.form.get('bloodpressure')
        st = request.form.get('skinthickness')
        insulin = request.form.get('insulin')
        bmi = request.form.get('bmi')
        dpf = request.form.get('dpf')
        age = request.form.get('age')
        
        # Validate inputs
        if not all([preg, glucose, bp, st, insulin, bmi, dpf, age]):
            return render_template('error.html', error="All fields are required."), 400
        
        try:
            preg = int(preg)
            glucose = int(glucose)
            bp = int(bp)
            st = int(st)
            insulin = int(insulin)
            bmi = float(bmi)
            dpf = float(dpf)
            age = int(age)
        except ValueError:
            return render_template('error.html', error="Please enter valid numbers."), 400
        
        # Validate ranges
        if not (0 <= preg <= 20 and 70 <= glucose <= 200 and 40 <= bp <= 180 and 
                0 <= st <= 100 and 0 <= insulin <= 900 and 10 <= bmi <= 60 and 
                0 <= dpf <= 2.5 and 20 <= age <= 100):
            return render_template('error.html', error="Input values are outside acceptable ranges."), 400
        
        # Make prediction
        data = np.array([[preg, glucose, bp, st, insulin, bmi, dpf, age]])
        prediction = classifier.predict(data)[0]
        prediction_prob = classifier.predict_proba(data)[0]
        confidence = max(prediction_prob) * 100
        
        # Get recommendations
        recommendations = get_health_recommendations(preg, glucose, bp, st, insulin, bmi, dpf, age)
        
        logger.info(f"Prediction made - Age: {age}, BMI: {bmi}, Result: {prediction}")
        
        # Save to history if user is authenticated
        if current_user.is_authenticated:
            try:
                prediction_record = PredictionHistory(
                    user_id=current_user.id,
                    pregnancies=preg,
                    glucose=glucose,
                    blood_pressure=bp,
                    skin_thickness=st,
                    insulin=insulin,
                    bmi=bmi,
                    dpf=dpf,
                    age=age,
                    prediction=prediction,
                    confidence=confidence
                )
                db.session.add(prediction_record)
                db.session.commit()
                logger.info(f"Prediction saved to history for user: {current_user.username}")
            except Exception as e:
                logger.error(f"Error saving prediction to history: {e}")
                db.session.rollback()
        
        return render_template('result.html', 
                             prediction=prediction,
                             confidence=confidence,
                             recommendations=recommendations,
                             age=age,
                             bmi=bmi,
                             glucose=glucose)
    
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return render_template('error.html', error="An error occurred during prediction. Please try again."), 500


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    try:
        data = request.get_json()
        
        if classifier is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        required_fields = ['pregnancies', 'glucose', 'bloodpressure', 'skinthickness', 
                          'insulin', 'bmi', 'dpf', 'age']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        values = [float(data[field]) for field in required_fields]
        prediction = classifier.predict([values])[0]
        confidence = float(max(classifier.predict_proba([values])[0])) * 100
        
        # Save to history if user is authenticated
        if current_user.is_authenticated:
            try:
                prediction_record = PredictionHistory(
                    user_id=current_user.id,
                    pregnancies=values[0],
                    glucose=values[1],
                    blood_pressure=values[2],
                    skin_thickness=values[3],
                    insulin=values[4],
                    bmi=values[5],
                    dpf=values[6],
                    age=values[7],
                    prediction=prediction,
                    confidence=confidence
                )
                db.session.add(prediction_record)
                db.session.commit()
            except Exception as e:
                logger.error(f"Error saving API prediction to history: {e}")
                db.session.rollback()
        
        return jsonify({
            'prediction': int(prediction),
            'has_diabetes': bool(prediction),
            'confidence': round(confidence, 2),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"API Error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': classifier is not None})


@app.route('/language/<lang>')
def set_app_language(lang):
    """Set application language"""
    set_language(lang)
    return redirect(request.referrer or url_for('home'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found."), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return render_template('error.html', error="Internal server error. Please try again later."), 500


# Create tables before first request
@app.before_request
def create_tables():
    """Create database tables if they don't exist"""
    # This runs on first request
    if not hasattr(app, 'tables_created'):
        with app.app_context():
            db.create_all()
            app.tables_created = True
        logger.info("Database tables created/verified")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
