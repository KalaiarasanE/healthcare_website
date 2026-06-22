"""
Authentication routes for user login, signup, and profile management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validation
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return redirect(url_for('auth.signup'))
        
        if not email or '@' not in email:
            flash('Invalid email address', 'error')
            return redirect(url_for('auth.signup'))
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('auth.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.signup'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('auth.signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.signup'))
        
        try:
            # Create new user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {username}")
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Signup error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('auth.signup'))
    
    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Account is disabled', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=bool(remember_me))
            logger.info(f"User logged in: {username}")
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout handler"""
    logger.info(f"User logged out: {current_user.username}")
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        language = request.form.get('language', 'en')
        theme = request.form.get('theme', 'light')
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.language = language
        current_user.theme = theme
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Profile updated for user: {current_user.username}")
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {e}")
        flash('An error occurred while updating profile', 'error')
        return redirect(url_for('auth.profile'))


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('auth.profile'))
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'error')
            return redirect(url_for('auth.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('auth.profile'))
        
        current_user.set_password(new_password)
        db.session.commit()
        logger.info(f"Password changed for user: {current_user.username}")
        flash('Password changed successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {e}")
        flash('An error occurred while changing password', 'error')
        return redirect(url_for('auth.profile'))
