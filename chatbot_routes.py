"""
Chatbot routes for diabetes Q&A support
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from models import db, ChatMessage
from datetime import datetime
import logging
import os
import json

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')
logger = logging.getLogger(__name__)

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI, APIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Chatbot will use fallback responses.")


# Pre-defined Q&A knowledge base for fallback responses
DIABETES_FAQ = {
    'what is diabetes': 'Diabetes is a chronic metabolic disorder characterized by elevated blood glucose levels. There are three main types: Type 1 (autoimmune), Type 2 (lifestyle-related), and gestational (during pregnancy).',
    'symptoms of diabetes': 'Common symptoms include increased thirst, frequent urination, fatigue, blurred vision, slow-healing wounds, and tingling in extremities. If you experience these symptoms, consult a healthcare provider.',
    'how to prevent diabetes': 'Prevention strategies include maintaining a healthy weight, regular exercise (150 min/week), balanced diet rich in fiber, limiting sugar intake, managing stress, and regular health checkups.',
    'blood glucose levels': 'Normal fasting glucose is 70-100 mg/dL. Prediabetes is 100-125 mg/dL. Diabetes is 126 mg/dL or higher. Consult your doctor about your specific targets.',
    'bmi meaning': 'BMI (Body Mass Index) is calculated as weight(kg) / height(m²). Ranges: Underweight <18.5, Normal 18.5-24.9, Overweight 25-29.9, Obese >30. It helps assess weight-related health risks.',
    'insulin function': 'Insulin is a hormone produced by the pancreas that helps cells absorb glucose from the blood. It maintains blood sugar balance. In diabetes, insulin production or function is impaired.',
    'exercise benefits': 'Regular exercise improves insulin sensitivity, helps maintain healthy weight, reduces blood pressure, and improves overall cardiovascular health. Aim for 150 minutes of moderate activity weekly.',
    'diet for diabetes': 'Focus on whole grains, lean proteins, vegetables, fruits, and healthy fats. Limit processed foods, sugary drinks, and refined carbohydrates. Portion control and meal timing are important.',
    'stress management': 'High stress increases blood glucose levels. Practice relaxation techniques, meditation, yoga, or regular exercise. Adequate sleep (7-9 hours) is also crucial.',
    'monitoring blood sugar': 'Regular blood glucose monitoring helps track your condition. Work with your doctor to set personal targets and establish a monitoring schedule suitable for your situation.',
}


def get_openai_client():
    """Get OpenAI client if available"""
    if not OPENAI_AVAILABLE:
        return None
    
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        logger.warning("OPENAI_API_KEY environment variable not set")
        return None
    
    return OpenAI(api_key=api_key)


def find_best_faq_response(question):
    """Find best matching FAQ response for a question"""
    question_lower = question.lower().strip('?').lower()
    
    best_match = None
    best_score = 0
    
    for faq_question, answer in DIABETES_FAQ.items():
        # Simple keyword matching
        score = sum(1 for word in faq_question.split() if word in question_lower.split())
        if score > best_score:
            best_score = score
            best_match = answer
    
    if best_score > 0:
        return best_match
    
    # Default response if no match found
    return "I'm not sure about that question. Could you rephrase it? I can help with questions about diabetes symptoms, prevention, diet, exercise, blood glucose monitoring, and management."


def get_chatbot_response(question):
    """Get response from OpenAI or fallback to FAQ"""
    client = get_openai_client()
    
    if client:
        try:
            system_prompt = """You are a helpful diabetes health assistant. You provide accurate, supportive 
            information about diabetes prevention, management, and healthy lifestyle. Always remind users to consult 
            with healthcare professionals for personalized advice. Keep responses concise (2-3 sentences) and friendly.
            Focus on: symptoms, prevention, diet, exercise, blood glucose monitoring, and general wellness."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to FAQ
            return find_best_faq_response(question)
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return find_best_faq_response(question)
    
    else:
        # Use FAQ fallback if OpenAI not available
        return find_best_faq_response(question)


@chatbot_bp.route('/')
def chatbot():
    """Chatbot page"""
    if current_user.is_authenticated:
        recent_messages = ChatMessage.query.filter_by(user_id=current_user.id)\
            .order_by(ChatMessage.created_at.desc()).limit(10).all()
        return render_template('chatbot/index.html', recent_messages=reversed(recent_messages))
    else:
        return render_template('chatbot/index.html', recent_messages=[])


@chatbot_bp.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chatbot interaction"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if len(message) > 1000:
            return jsonify({'error': 'Message too long'}), 400
        
        # Get response
        response_text = get_chatbot_response(message)
        
        # Store in database if user is authenticated
        if current_user.is_authenticated:
            try:
                chat_msg = ChatMessage(
                    user_id=current_user.id,
                    message=message,
                    response=response_text
                )
                db.session.add(chat_msg)
                db.session.commit()
            except Exception as e:
                logger.error(f"Error saving chat message: {e}")
                # Continue anyway, just don't save
        
        return jsonify({
            'response': response_text,
            'timestamp': datetime.now().isoformat(),
            'authenticated': current_user.is_authenticated
        })
    
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500


@chatbot_bp.route('/history')
@login_required
def chat_history():
    """View chat history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = ChatMessage.query.filter_by(user_id=current_user.id)\
        .order_by(ChatMessage.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    messages = pagination.items
    
    return render_template('chatbot/history.html', messages=messages, pagination=pagination)


@chatbot_bp.route('/api/faq')
def get_faq():
    """API endpoint to get FAQ items"""
    faq_list = []
    for question, answer in DIABETES_FAQ.items():
        faq_list.append({
            'question': question.title(),
            'answer': answer
        })
    
    return jsonify(faq_list)
