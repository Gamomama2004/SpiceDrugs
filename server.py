from flask import Flask, render_template_string, request, redirect, session
import hashlib
import secrets
import os
from datetime import datetime, timedelta
import random
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ==================== КЛАСС ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ====================
class UserAuth:
    def __init__(self):
        self.users = {
            'admin': {
                'password': hashlib.sha256('admin123'.encode()).hexdigest(),
                'name': 'Администратор',
                'role': 'admin',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'user': {
                'password': hashlib.sha256('user123'.encode()).hexdigest(),
                'name': 'Менеджер',
                'role': 'user',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        self.sessions = {}
    
    def get_user(self, username):
        return self.users.get(username)
    
    def register(self, username, password, name):
        if username in self.users:
            return False, "Пользователь уже существует"
        if len(password) < 4:
            return False, "Пароль должен быть минимум 4 символа"
        
        self.users[username] = {
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'name': name,
            'role': 'user',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return True, "Регистрация успешна"
    
    def check_password(self, username, password):
        if username not in self.users:
            return False
        return self.users[username]['password'] == hashlib.sha256(password.encode()).hexdigest()
    
    def is_admin(self, username):
        if username not in self.users:
            return False
        return self.users[username].get('role') == 'admin'

# ==================== КЛАСС ДЛЯ РАБОТЫ СО СПЕЦИЯМИ ====================
class SpiceDatabase:
    def __init__(self):
        self.spices = self.generate_spices()
    
    def generate_spices(self):
        spices = []
        base_spices = [
            {'id': 1, 'name': 'Чёрный перец горошком', 'price': 350, 'supplier': 'ООО "Специи Мира"', 'stock': 100},
            {'id': 2, 'name': 'Корица цейлонская', 'price': 580, 'supplier': 'ИП "Пряный Двор"', 'stock': 45},
            {'id': 3, 'name': 'Куркума молотая', 'price': 220, 'supplier': 'ООО "Специи Мира"', 'stock': 150},
            {'id': 4, 'name': 'Паприка сладкая', 'price': 180, 'supplier': 'ООО "АгроСпеции"', 'stock': 200},
            {'id': 5, 'name': 'Имбирь молотый', 'price': 320, 'supplier': 'ИП "Пряный Двор"', 'stock': 80},
            {'id': 6, 'name': 'Кардамон зелёный', 'price': 1250, 'supplier': 'ООО "Восток-Специи"', 'stock': 25},
            {'id': 7, 'name': 'Гвоздика', 'price': 450, 'supplier': 'ООО "Специи Мира"', 'stock': 60},
            {'id': 8, 'name': 'Мускатный орех', 'price': 680, 'supplier': 'ИП "Пряный Двор"', 'stock': 35},
            {'id': 9, 'name': 'Кунжут белый', 'price': 150, 'supplier': 'ООО "АгроСпеции"', 'stock': 300},
            {'id': 10, 'name': 'Зира (кумин)', 'price': 280, 'supplier': 'ООО "Восток-Специи"', 'stock': 90},
            {'id': 11, 'name': 'Кориандр молотый', 'price': 190, 'supplier': 'ООО "Специи Мира"', 'stock': 120},
            {'id': 12, 'name': 'Шафран настоящий', 'price': 3500, 'supplier': 'ИП "Пряный Двор"', 'stock': 5},
            {'id': 13, 'name': 'Бадьян', 'price': 520, 'supplier': 'ООО "Восток-Специи"', 'stock': 40},
            {'id': 14, 'name': 'Асафетида', 'price': 890, 'supplier': 'ООО "Специи Мира"', 'stock': 20},
            {'id': 15, 'name': 'Фенхель', 'price': 240, 'supplier': 'ИП "Пряный Двор"', 'stock': 110},
            {'id': 16, 'name': 'Тмин', 'price': 210, 'supplier': 'ООО "АгроСпеции"', 'stock': 95},
            {'id': 17, 'name': 'Горчица белая', 'price': 120, 'supplier': 'ООО "Специи Мира"', 'stock': 250},
            {'id': 18, 'name': 'Укроп', 'price': 160, 'supplier': 'ИП "Пряный Двор"', 'stock': 180},
            {'id': 19, 'name': 'Петрушка', 'price': 140, 'supplier': 'ООО "АгроСпеции"', 'stock': 200},
            {'id': 20, 'name': 'Базилик', 'price': 170, 'supplier': 'ООО "Специи Мира"', 'stock': 160},
            {'id': 21, 'name': 'Орегано', 'price': 230, 'supplier': 'ИП "Пряный Двор"', 'stock': 85},
            {'id': 22, 'name': 'Розмарин', 'price': 290, 'supplier': 'ООО "Восток-Специи"', 'stock': 70},
            {'id': 23, 'name': 'Тимьян', 'price': 260, 'supplier': 'ООО "Специи Мира"', 'stock': 75},
            {'id': 24, 'name': 'Майоран', 'price': 310, 'supplier': 'ИП "Пряный Двор"', 'stock': 55},
            {'id': 25, 'name': 'Ваниль', 'price': 2800, 'supplier': 'ООО "Восток-Специи"', 'stock': 8},
            {'id': 26, 'name': 'Перец розовый', 'price': 720, 'supplier': 'ООО "Специи Мира"', 'stock': 30},
            {'id': 27, 'name': 'Перец душистый', 'price': 430, 'supplier': 'ИП "Пряный Двор"', 'stock': 65},
            {'id': 28, 'name': 'Хмели-сунели', 'price': 250, 'supplier': 'ООО "АгроСпеции"', 'stock': 130},
            {'id': 29, 'name': 'Аджика', 'price': 200, 'supplier': 'ООО "Специи Мира"', 'stock': 140},
            {'id': 30, 'name': 'Карри', 'price': 270, 'supplier': 'ИП "Пряный Двор"', 'stock': 120}
        ]
        
        end_date = datetime.now()
        for s in base_spices:
            # Генерируем историю цен для графика
            price_history = []
            current_price = s['price']
            for days_ago in range(90, -1, -1):
                date = (end_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                change = random.uniform(-0.05, 0.05)
                current_price = max(10, round(current_price * (1 + change), 2))
                price_history.append({'date': date, 'price': current_price})
            s['price_history'] = price_history
            spices.append(s)
        return spices
    
    def get_all(self):
        return self.spices
    
    def get_spice_by_id(self, spice_id):
        for s in self.spices:
            if s['id'] == spice_id:
                return s
        return None
    
    def get_statistics(self):
        prices = [s['price'] for s in self.spices]
        total_value = sum(s['price'] * s['stock'] for s in self.spices)
        return {
            'total_items': len(self.spices),
            'avg_price': round(sum(prices) / len(prices), 2),
            'min_price': min(prices),
            'max_price': max(prices),
            'total_stock': sum(s['stock'] for s in self.spices),
            'total_value': round(total_value, 2)
        }
    
    def add_spice(self, name, price, supplier, stock):
        new_id = max([s['id'] for s in self.spices]) + 1
        today = datetime.now().strftime('%Y-%m-%d')
        self.spices.append({
            'id': new_id,
            'name': name,
            'price': float(price),
            'supplier': supplier,
            'stock': int(stock),
            'price_history': [{'date': today, 'price': float(price)}]
        })
        return True
    
    def update_prices(self):
        for s in self.spices:
            change = random.uniform(-0.1, 0.1)
            new_price = round(max(10, s['price'] * (1 + change)), 2)
            s['price'] = new_price
            s['price_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'price': new_price
            })
        return True

# ==================== HTML ШАБЛОНЫ ====================

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход - SpiceDrugs Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }
        body::before {
            content: "🌶️🍃🌿🌶️🍃🌿🌶️🍃🌿";
            position: absolute;
            font-size: 200px;
            opacity: 0.05;
            white-space: nowrap;
            animation: slide 60s linear infinite;
            pointer-events: none;
        }
        @keyframes slide {
            0% { transform: translateX(-50%); }
            100% { transform: translateX(0%); }
        }
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            width: 450px;
            max-width: 90%;
            overflow: hidden;
            position: relative;
            z-index: 1;
        }
        .header {
            background: linear-gradient(135deg, #1a472a 0%, #2d5a3b 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .logo-icon { font-size: 60px; margin-bottom: 10px; }
        .tabs {
            display: flex;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            background: #f8f9fa;
            border: none;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .tab.active {
            background: white;
            color: #2d5a3b;
            border-bottom: 3px solid #2d5a3b;
        }
        .form-panel { padding: 40px; display: none; }
        .form-panel.active { display: block; }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #2d5a3b;
        }
        .btn-submit {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-submit:hover { transform: translateY(-2px); }
        .message { margin: 20px; padding: 10px; border-radius: 8px; text-align: center; display: none; }
        .message.error { background: #fee; color: #c33; display: block; }
        .message.success { background: #efe; color: #3a7; display: block; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.form-panel').forEach(p => p.classList.remove('active'));
            document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
            document.getElementById(`panel-${tabName}`).classList.add('active');
        }
    </script>
</head>
<body>
    <div class="login-container">
        <div class="header">
            <div class="logo-icon">🌶️</div>
            <h1>SpiceDrugs Pro</h1>
            <p>Профессиональная система мониторинга специй</p>
        </div>
        <div class="tabs">
            <button class="tab active" data-tab="login" onclick="showTab('login')">🔐 Вход</button>
            <button class="tab" data-tab="register" onclick="showTab('register')">📝 Регистрация</button>
        </div>
        <div id="message" class="message"></div>
        <div id="panel-login" class="form-panel active">
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>👤 Имя пользователя</label>
                    <input type="text" name="username" required placeholder="Введите логин">
                </div>
                <div class="form-group">
                    <label>🔒 Пароль</label>
                    <input type="password" name="password" required placeholder="Введите пароль">
                </div>
                <button type="submit" class="btn-submit">Войти в систему</button>
            </form>
        </div>
        <div id="panel-register" class="form-panel">
            <form method="POST" action="/register">
                <div class="form-group">
                    <label>👤 Имя пользователя</label>
                    <input type="text" name="username" id="reg-username" required placeholder="Придумайте логин">
                </div>
                <div class="form-group">
                    <label>👨 Ваше имя</label>
                    <input type="text" name="name" id="reg-name" required placeholder="Как вас зовут?">
                </div>
                <div class="form-group">
                    <label>🔒 Пароль</label>
                    <input type="password" name="password" id="reg-password" required placeholder="Минимум 4 символа">
                </div>
                <div class="form-group">
                    <label>🔒 Подтверждение пароля</label>
                    <input type="password" name="confirm" id="reg-confirm" required placeholder="Повторите пароль">
                </div>
                <button type="submit" class="btn-submit">Зарегистрироваться</button>
            </form>
        </div>
        <div class="footer">
            <p>© 2024 SpiceDrugs Pro — Система мониторинга специй</p>
        </div>
    </div>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('error')) {
            const msg = document.getElementById('message');
            msg.textContent = urlParams.get('error');
            msg.className = 'message error';
        }
        if (urlParams.get('success')) {
            const msg = document.getElementById('message');
            msg.textContent = urlParams.get('success');
            msg.className = 'message success';
        }
        
        function validateRegister() {
            var pass = document.getElementById('reg-password').value;
            var confirm = document.getElementById('reg-confirm').value;
            if (pass !== confirm) {
                alert('Пароли не совпадают!');
                return false;
            }
            if (pass.length < 4) {
                alert('Пароль должен быть минимум 4 символа!');
                return false;
            }
            return true;
        }
        document.querySelector('#panel-register form').onsubmit = validateRegister;
    </script>
</body>
</html>
'''

MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpiceDrugs Pro - Мониторинг специй</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', 'Roboto', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            color: #333;
            padding: 0 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            flex-wrap: wrap;
        }
        .logo {
            font-size: 26px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
            background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .logo span { color: #ffd700; background: none; }
        .nav-links { display: flex; flex-wrap: wrap; align-items: center; gap: 5px; }
        .nav-links a {
            color: #333;
            text-decoration: none;
            padding: 8px 18px;
            border-radius: 25px;
            transition: all 0.3s;
            font-weight: 600;
        }
        .nav-links a:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; transform: translateY(-2px); }
        .user-info {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-left: 15px;
            padding: 8px 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 30px;
            color: white;
            font-weight: 600;
        }
        .role-badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }
        .role-badge.admin { background: #ffd700; color: #667eea; }
        .role-badge.user { background: rgba(255,255,255,0.3); color: white; }
        
        .container { max-width: 1400px; margin: 30px auto; padding: 0 30px; }
        
        .welcome {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 25px 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(102,126,234,0.2);
        }
        .welcome h2 { color: #667eea; margin-bottom: 8px; font-size: 24px; font-weight: 700; }
        .role-info { color: #555; font-size: 14px; margin-top: 8px; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, rgba(102,126,234,0.95) 0%, rgba(118,75,162,0.95) 100%);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            transition: all 0.3s;
            border: 1px solid rgba(255,255,255,0.3);
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            color: white;
        }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }
        .stat-card h4 { color: rgba(255,255,255,0.9); font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; font-weight: 700; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: white; }
        
        .table-container {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 5px 25px rgba(0,0,0,0.1);
            border: 1px solid rgba(102,126,234,0.2);
        }
        table { width: 100%; border-collapse: collapse; min-width: 700px; }
        th, td { padding: 15px 18px; text-align: left; border-bottom: 1px solid #f0f0f0; }
        th { background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; font-size: 14px; }
        tr:hover { background: rgba(102,126,234,0.05); transition: 0.2s; }
        td { color: #333; font-weight: 500; }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 24px;
            border: none;
            border-radius: 30px;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            cursor: pointer;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
        
        .btn-small { padding: 5px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; margin: 0 3px; display: inline-block; transition: all 0.2s; font-weight: 600; }
        .btn-info { background: #4299e1; color: white; }
        .btn-warning { background: #ed8936; color: white; }
        .btn-danger { background: #e53e3e; color: white; }
        .btn-small:hover { transform: translateY(-1px); opacity: 0.9; }
        
        .actions { white-space: nowrap; }
        
        .footer {
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
            color: #333;
            text-align: center;
            padding: 25px;
            margin-top: 50px;
            border-top: 1px solid rgba(102,126,234,0.2);
            font-weight: 500;
        }
        
        .admin-buttons { display: flex; gap: 12px; margin-bottom: 25px; flex-wrap: wrap; justify-content: flex-end; }
        .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }
        .header-actions h2 { color: #667eea; font-weight: 700; }
        
        @media (max-width: 768px) {
            .nav-container { flex-direction: column; gap: 10px; }
            .stats-grid { gap: 15px; }
            th, td { padding: 10px 12px; }
        }
        
        .price-up { color: #e53e3e; }
        .price-down { color: #48bb78; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                {% if is_admin %}
                <a href="/add">➕ Добавить специю</a>
                <a href="/users">👥 Пользователи</a>
                {% endif %}
                <div class="user-info">
                    👋 {{ username }}
                    <span class="role-badge {{ 'admin' if is_admin else 'user' }}">{{ role_text }}</span>
                    <a href="/logout" style="color:white; text-decoration:none;">🚪 Выйти</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="welcome">
            <h2>🍃 Добро пожаловать, {{ username }}!</h2>
            <p>Сегодня {{ date }}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card"><h4>🌶️ Всего позиций</h4><div class="value">{{ stats.total_items }}</div></div>
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{{ stats.avg_price }} ₽</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{{ stats.min_price }} / {{ stats.max_price }} ₽</div></div>
            <div class="stat-card"><h4>📦 Общий запас</h4><div class="value">{{ stats.total_stock }} кг</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{{ stats.total_value }} ₽</div></div>
        </div>
        
        <div class="header-actions">
            <h2>📋 Наш ассортимент специй</h2>
            {% if is_admin %}
            <div class="admin-buttons">
                <a href="/add" class="btn-primary">➕ Добавить специю</a>
                <a href="/monitor" class="btn-primary">🔄 Мониторинг цен</a>
            </div>
            {% endif %}
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr><th>ID</th><th>Наименование</th><th>Поставщик</th><th>Цена</th><th>Остаток</th><th>Действия</th></tr>
                </thead>
                <tbody>
                    {% for s in spices %}
                    <tr>
                        <td>{{ s.id }}</td>
                        <td><strong>{{ s.name }}</strong></td>
                        <td>{{ s.supplier }}</td>
                        <td>{{ s.price }} ₽</td>
                        <td>{{ s.stock }} кг</td>
                        <td class="actions">
                            <a href="/history/{{ s.id }}" class="btn-small btn-info">📊 История</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
        <p style="font-size: 12px; margin-top: 8px; opacity: 0.8;">© 2024 Все права защищены</p>
    </div>
</body>
</html>
'''

HISTORY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>История цен - {{ spice.name }} | SpiceDrugs Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }
        .nav-container { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 30px; }
        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        .price { font-size: 36px; color: #2d5a3b; font-weight: bold; }
        canvas {
            width: 100%;
            height: auto;
            background: #f8f9ff;
            border-radius: 15px;
        }
        .back {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
        }
        .footer {
            background: rgba(255,255,255,0.9);
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <a href="/" style="color:#333; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h1>📈 История цен: {{ spice.name }}</h1>
            <div class="price">💰 Текущая цена: {{ spice.price }} ₽</div>
            <p style="margin-top: 20px;">🏭 Поставщик: {{ spice.supplier }}</p>
            <p>📦 Остаток на складе: {{ spice.stock }} кг</p>
        </div>
        
        <div class="card">
            <h2>📊 Динамика изменения цены (последние 90 дней)</h2>
            <canvas id="priceChart" width="800" height="300" style="width:100%; height:300px;"></canvas>
        </div>
        
        <div style="text-align: center;">
            <a href="/" class="back">← Вернуться на главную</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
    </div>
    
    <script>
        const priceData = {{ prices | tojson }};
        
        function drawChart() {
            const canvas = document.getElementById('priceChart');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const container = canvas.parentElement;
            const w = container.clientWidth;
            const h = 300;
            canvas.width = w;
            canvas.height = h;
            
            if (!priceData || priceData.length < 2) return;
            
            const minPriceVal = Math.min(...priceData);
            const maxPriceVal = Math.max(...priceData);
            const rangeVal = maxPriceVal - minPriceVal || 1;
            
            const paddingLeft = 50;
            const paddingRight = 30;
            const paddingTop = 20;
            const paddingBottom = 40;
            const chartW = w - paddingLeft - paddingRight;
            const chartH = h - paddingTop - paddingBottom;
            
            ctx.clearRect(0, 0, w, h);
            
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 0.5;
            for (let i = 0; i <= 4; i++) {
                const y = paddingTop + (i / 4) * chartH;
                ctx.beginPath();
                ctx.moveTo(paddingLeft, y);
                ctx.lineTo(w - paddingRight, y);
                ctx.stroke();
                ctx.fillStyle = '#999';
                ctx.font = '10px Arial';
                ctx.fillText(`${(maxPriceVal - (i / 4) * rangeVal).toFixed(0)} ₽`, 5, y + 3);
            }
            
            const stepX = chartW / (priceData.length - 1);
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2.5;
            
            for (let i = 0; i < priceData.length; i++) {
                const x = paddingLeft + i * stepX;
                const y = paddingTop + chartH - ((priceData[i] - minPriceVal) / rangeVal) * chartH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            
            ctx.lineTo(paddingLeft + (priceData.length - 1) * stepX, paddingTop + chartH);
            ctx.lineTo(paddingLeft, paddingTop + chartH);
            ctx.fillStyle = 'rgba(102,126,234,0.1)';
            ctx.fill();
            
            for (let i = 0; i < priceData.length; i++) {
                const x = paddingLeft + i * stepX;
                const y = paddingTop + chartH - ((priceData[i] - minPriceVal) / rangeVal) * chartH;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffd700';
                ctx.fill();
                ctx.strokeStyle = '#667eea';
                ctx.lineWidth = 1;
                ctx.stroke();
            }
            
            const currentY = paddingTop + chartH - ((priceData[priceData.length-1] - minPriceVal) / rangeVal) * chartH;
            ctx.beginPath();
            ctx.strokeStyle = '#ffd700';
            ctx.setLineDash([8, 4]);
            ctx.moveTo(paddingLeft, currentY);
            ctx.lineTo(w - paddingRight, currentY);
            ctx.stroke();
            ctx.setLineDash([]);
        }
        
        window.onload = function() {
            drawChart();
            window.addEventListener('resize', function() {
                setTimeout(drawChart, 200);
            });
        };
    </script>
</body>
</html>
'''

ANALYTICS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аналитика - SpiceDrugs Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }
        .nav-container { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .nav-links a { color: #333; text-decoration: none; margin-left: 25px; padding: 8px 16px; border-radius: 25px; font-weight: 600; }
        .nav-links a:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 1400px; margin: 30px auto; padding: 0 30px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, rgba(102,126,234,0.95) 0%, rgba(118,75,162,0.95) 100%);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
        }
        .stat-card h4 { color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 12px; }
        .stat-card .value { font-size: 28px; font-weight: bold; }
        .table-container {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
        }
        table { width: 100%; border-collapse: collapse; min-width: 800px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }
        th { background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; }
        tr:hover { background: rgba(102,126,234,0.05); }
        td { color: #333; font-weight: 500; }
        .footer {
            background: rgba(255,255,255,0.9);
            text-align: center;
            padding: 25px;
            margin-top: 50px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card"><h4>🌶️ Всего специй</h4><div class="value">{{ stats.total_items }}</div></div>
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{{ stats.avg_price }} ₽</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{{ stats.min_price }} / {{ stats.max_price }} ₽</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{{ stats.total_value }} ₽</div></div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr><th>Специя</th><th>Поставщик</th><th>Цена</th><th>Остаток</th></tr>
                </thead>
                <tbody>
                    {% for s in spices %}
                    <tr>
                        <td><strong>{{ s.name }}</strong></td>
                        <td>{{ s.supplier }}</td>
                        <td>{{ s.price }} ₽</td>
                        <td>{{ s.stock }} кг</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
    </div>
</body>
</html>
'''

ADD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Добавить специю</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }
        .nav-container { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .form-container { max-width: 600px; margin: 50px auto; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 40px; border-radius: 25px; }
        h2 { color: #667eea; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 12px; transition: 0.3s; }
        input:focus { outline: none; border-color: #667eea; }
        button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border: none; border-radius: 30px; cursor: pointer; font-size: 16px; transition: 0.3s; font-weight: 600; }
        button:hover { transform: translateY(-2px); }
        .back { display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <a href="/" style="color:#333; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    <div class="form-container">
        <h2>➕ Добавление новой специи</h2>
        <form method="POST">
            <div class="form-group"><label>🌿 Название специи</label><input type="text" name="name" required placeholder="Например: Шафран"></div>
            <div class="form-group"><label>💰 Цена (₽ за кг)</label><input type="number" step="0.01" name="price" required placeholder="0.00"></div>
            <div class="form-group"><label>🏭 Поставщик</label><input type="text" name="supplier" required placeholder="ООО Поставщик"></div>
            <div class="form-group"><label>📦 Количество на складе (кг)</label><input type="number" name="stock" required placeholder="0"></div>
            <button type="submit">💾 Сохранить</button>
        </form>
        <a href="/" class="back">← Вернуться на главную</a>
    </div>
</body>
</html>
'''

USERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Управление пользователями</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }
        .nav-container { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 30px; }
        .table-container {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }
        th { background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; }
        tr:hover { background: rgba(102,126,234,0.05); }
        .back {
            display: inline-block;
            margin-top: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 30px;
        }
        h1 { color: #667eea; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <a href="/" style="color:#333; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    <div class="container">
        <h1>👥 Управление пользователями</h1>
        <div class="table-container">
            <table>
                <thead><tr><th>Логин</th><th>Имя</th><th>Роль</th><th>Дата регистрации</th></tr></thead>
                <tbody>
                    {% for u in users %}
                    <tr>
                        <td>{{ u.username }}</td>
                        <td>{{ u.name }}</td>
                        <td>{{ u.role }}</td>
                        <td>{{ u.created_at }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <a href="/" class="back">← На главную</a>
    </div>
</body>
</html>
'''

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
auth = UserAuth()
db = SpiceDatabase()

# ==================== МАРШРУТЫ ====================

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        username = session['username']
        user = auth.get_user(username)
        is_admin = auth.is_admin(username)
        
        stats = db.get_statistics()
        spices = db.get_all()
        
        role_text = '👑 Администратор' if is_admin else '👤 Пользователь'
        
        return render_template_string(MAIN_TEMPLATE, 
                                      username=user.get('name', username),
                                      role_text=role_text,
                                      is_admin=is_admin,
                                      stats=stats,
                                      spices=spices,
                                      date=datetime.now().strftime('%d.%m.%Y'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if auth.check_password(username, password):
            session['username'] = username
            return redirect('/')
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Неверный логин или пароль')
    
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if auth.check_password(username, password):
        session['username'] = username
        return redirect('/')
    else:
        return redirect('/?error=Неверный+логин+или+пароль')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    
    success, message = auth.register(username, password, name)
    if success:
        return redirect('/?success=' + message)
    else:
        return redirect('/?error=' + message)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/analytics')
def analytics():
    if 'username' not in session:
        return redirect('/')
    
    stats = db.get_statistics()
    spices = db.get_all()
    return render_template_string(ANALYTICS_TEMPLATE, stats=stats, spices=spices)

@app.route('/history/<int:spice_id>')
def history(spice_id):
    if 'username' not in session:
        return redirect('/')
    
    spice = db.get_spice_by_id(spice_id)
    if not spice:
        return redirect('/')
    
    prices = [h['price'] for h in spice.get('price_history', [spice['price']])[-90:]]
    return render_template_string(HISTORY_TEMPLATE, spice=spice, prices=prices)

@app.route('/add', methods=['GET', 'POST'])
def add_spice():
    if 'username' not in session:
        return redirect('/')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        supplier = request.form.get('supplier')
        stock = int(request.form.get('stock'))
        
        db.add_spice(name, price, supplier, stock)
        return redirect('/')
    
    return render_template_string(ADD_TEMPLATE)

@app.route('/users')
def users_list():
    if 'username' not in session:
        return redirect('/')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    users_list = [{'username': u, 'name': data['name'], 'role': data['role'], 'created_at': data['created_at']} 
                  for u, data in auth.users.items()]
    
    return render_template_string(USERS_TEMPLATE, users=users_list)

@app.route('/monitor')
def monitor_prices():
    if 'username' not in session:
        return redirect('/')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    db.update_prices()
    return redirect('/')

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)