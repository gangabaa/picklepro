# PicklePro - Simple Backend
# Revenue: $9.99/month × 25 subs = $250/mo potential

from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('picklepro.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE,
        name TEXT,
        premium BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Clicks table (track affiliate clicks)
    c.execute('''CREATE TABLE IF NOT EXISTS clicks (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product TEXT,
        clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return jsonify({
        'app': 'PicklePro',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/click', methods=['POST'])
def track_click():
    data = request.json
    product = data.get('product')
    
    # Track click for analytics
    conn = sqlite3.connect('picklepro.db')
    c = conn.cursor()
    c.execute('INSERT INTO clicks (product) VALUES (?)', (product,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'tracked'})

@app.route('/api/premium/buy', methods=['POST'])
def buy_premium():
    data = request.json
    email = data.get('email')
    
    # In production: Stripe integration here
    # stripe.PaymentIntent.create(...)
    
    conn = sqlite3.connect('picklepro.db')
    c = conn.cursor()
    c.execute('UPDATE users SET premium = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    
    return jsonify({
        'status': 'success',
        'premium': True,
        'next_billing': '2026-03-25'
    })

@app.route('/api/earnings')
def earnings():
    conn = sqlite3.connect('picklepro.db')
    c = conn.cursor()
    
    # Count premium users
    c.execute('SELECT COUNT(*) FROM users WHERE premium = 1')
    premium_users = c.fetchone()[0]
    
    # Count clicks
    c.execute('SELECT COUNT(*) FROM clicks')
    total_clicks = c.fetchone()[0]
    
    conn.close()
    
    revenue = premium_users * 9.99
    affiliate_estimate = total_clicks * 0.50  # Rough estimate
    
    return jsonify({
        'premium_users': premium_users,
        'total_clicks': total_clicks,
        'monthly_revenue': round(revenue, 2),
        'affiliate_estimate': round(affiliate_estimate, 2),
        'total_potential': round(revenue + affiliate_estimate, 2)
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
