#!/usr/bin/env python
"""
Database initialization script
Creates all necessary tables and can seed initial data
"""

import os
import sys
from app import app, db
from models import User, PredictionHistory, ChatMessage
from datetime import datetime

def init_db():
    """Initialize the database"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if tables are empty
        user_count = User.query.count()
        print(f"📊 Current users: {user_count}")
        
        if user_count == 0:
            print("\n💡 Database is empty. Consider adding some test data!")
            print("   Tip: Use the signup page to create a new account")
        
        print("\n✨ Database initialization complete!")

def seed_data():
    """Add sample data (optional)"""
    with app.app_context():
        # Check if sample user already exists
        sample_user = User.query.filter_by(username='demo').first()
        
        if not sample_user:
            print("\nAdding sample user...")
            demo_user = User(
                username='demo',
                email='demo@example.com',
                first_name='Demo',
                last_name='User'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Sample user created (username: demo, password: demo123)")
        else:
            print("\n✓ Sample user already exists")

if __name__ == '__main__':
    try:
        init_db()
        
        # Ask if user wants to seed data
        response = input("\nWould you like to add sample data? (y/n): ").lower().strip()
        if response == 'y':
            seed_data()
        
        print("\n🎉 All done! You can now run the application with: python app.py")
    
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        sys.exit(1)
