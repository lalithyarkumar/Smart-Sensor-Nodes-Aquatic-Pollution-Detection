from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import joblib
import numpy as np
import pandas as pd
import requests
import telepot
from datetime import datetime
import os
import hashlib
import re

from private_config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    THINGSPEAK_READ_API_KEY,
    SECRET_KEY
)

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Change this to a secure key

# Database setup
DATABASE_PATH = 'database/water_quality.db'

# Create database folder if it doesn't exist
os.makedirs('database', exist_ok=True)

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ph REAL NOT NULL,
            temperature REAL NOT NULL,
            turbidity REAL NOT NULL,
            tds REAL NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Model loading
try:
    model = joblib.load('models/best_water_quality_model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    label_encoder = joblib.load('models/label_encoder.pkl')
    feature_order = joblib.load('models/feature_order.pkl')
    print("Models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    scaler = None
    label_encoder = None
    feature_order = None

# Helper functions
def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def make_prediction(ph, temp, tur, tds):
    """Make prediction using the loaded model"""
    try:
        if model is None or scaler is None or label_encoder is None or feature_order is None:
            return "Model not loaded properly"

        # Create DataFrame
        sample = pd.DataFrame([[ph, temp, tur, tds]], columns=feature_order)
        
        # Scale
        sample_scaled = scaler.transform(sample)
        
        # Predict
        pred_encoded = model.predict(sample_scaled)[0]
        pred_label = label_encoder.inverse_transform([pred_encoded])[0]
        
        return pred_label
    except Exception as e:
        print(f"Prediction error: {e}")
        return None

def send_telegram_alert(ph, temp, tur, tds, result):
    """Send alert via Telegram"""
    try:
        bot = telepot.Bot(TELEGRAM_BOT_TOKEN)
        
        message = f"""🚨 WATER QUALITY ALERT 🚨

                    ⚠️ Poor Water Quality Detected!

                    📊 Readings:
                    • pH: {ph}
                    • Temperature: {temp}°C
                    • Turbidity: {tur} NTU
                    • TDS: {tds} ppm

                    🔴 Result: {result}

                    📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                    Please take immediate action!"""
        
        bot.sendMessage(TELEGRAM_CHAT_ID, message)
        print("Alert sent successfully!")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
            return render_template('register.html')
        
        # Email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Invalid email address!', 'danger')
            return render_template('register.html')

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists!', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Check if email exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('Email already registered!', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to view dashboard.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    )
    predictions = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', predictions=predictions)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        flash('Please login to make predictions.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
    
        # Get data from form
        try:
            ph = float(request.form['ph'])
            temp = float(request.form['temperature'])
            tur = float(request.form['turbidity'])
            tds = float(request.form['tds'])
        except ValueError:
            flash('Please enter valid numeric values!', 'danger')
            return redirect(url_for('predict'))

        # Make prediction
        result = make_prediction(ph, temp, tur, tds)

        if result:
            # Save prediction to database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO predictions (user_id, ph, temperature, turbidity, tds, result) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (session['user_id'], ph, temp, tur, tds, result)
            )
            conn.commit()
            conn.close()

            # Send alert if water quality is poor
            if result.lower() in ['poor', 'unsafe']:
                send_telegram_alert(ph, temp, tur, tds, result)

            return render_template('result.html', 
                                 ph=ph, 
                                 temp=temp, 
                                 tur=tur, 
                                 tds=tds, 
                                 result=result)
    response = requests.get(
    f"https://api.thingspeak.com/channels/3407719/feeds.json?api_key={THINGSPEAK_READ_API_KEY}&results=2"
)

    data = response.json()
    ph = float(data['feeds'][-1]['field1'])
    temp = float(data['feeds'][-1]['field2'])
    tur = float(data['feeds'][-1]['field3'])
    try:
        tds = float(data['feeds'][-1]['field4'])
    except:
        tds=343
    return render_template('predict.html',ph=ph,temp=temp,tur=tur,tds=tds)

@app.route('/delete_prediction/<int:pred_id>')
def delete_prediction(pred_id):
    if 'user_id' not in session:
        flash('Please login to delete predictions.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if prediction belongs to user
    cursor.execute('SELECT user_id FROM predictions WHERE id = ?', (pred_id,))
    pred = cursor.fetchone()
    
    if not pred:
        flash('Prediction not found.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
    
    if pred['user_id'] != session['user_id']:
        flash('You do not have permission to delete this prediction.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Delete prediction
    cursor.execute('DELETE FROM predictions WHERE id = ?', (pred_id,))
    conn.commit()
    conn.close()
    
    flash('Prediction deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/view_prediction/<int:pred_id>')
def view_prediction(pred_id):
    if 'user_id' not in session:
        flash('Please login to view prediction details.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM predictions WHERE id = ?', (pred_id,))
    prediction = cursor.fetchone()
    conn.close()
    
    if not prediction:
        flash('Prediction not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if prediction['user_id'] != session['user_id']:
        flash('You do not have permission to view this prediction.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('result.html', 
                         ph=prediction['ph'], 
                         temp=prediction['temperature'], 
                         tur=prediction['turbidity'], 
                         tds=prediction['tds'], 
                         result=prediction['result'],
                         from_history=True)

if __name__ == '__main__':
    app.run(debug=True)
