from flask import Flask, render_template_string, request, redirect, make_response, session
import hashlib
import secrets
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Секретный ключ для сессий

# ==================== КЛАСС ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ====================
class UserAuth:
    def __init__(self):
        # Храним пользователей в словаре (можно заменить на БД позже)
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
        
        for s in base_spices:
            spices.append(s)
        return spices
    
    def get_all(self):
        return self.spices
    
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
        self.spices.append({
            'id': new_id,
            'name': name,
            'price': float(price),
            'supplier': supplier,
            'stock': int(stock)
        })
        return True
    
    def update_spice(self, spice_id, name, price, supplier, stock):
        for s in self.spices:
            if s['id'] == spice_id:
                s['name'] = name
                s['price'] = float(price)
                s['supplier'] = supplier
                s['stock'] = int(stock)
                return True
        return False
    
    def delete_spice(self, spice_id):
        self.spices = [s for s in self.spices if s['id'] != spice_id]
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 20px;
            width: 380px;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        h1 { color: #667eea; margin-bottom: 10px; }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
        }
        input:focus { outline: none; border-color: #667eea; }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
        }
        .error { color: #e53e3e; margin-bottom: 15px; }
        .info {
            margin-top: 20px;
            padding: 15px;
            background: #e8f5e9;
            border-radius: 10px;
            font-size: 12px;
        }
        .logo-icon { font-size: 50px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo-icon">🌶️</div>
        <h1>SpiceDrugs Pro</h1>
        <p style="color:#666; margin-bottom:20px;">Система мониторинга специй</p>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <input type="text" name="username" placeholder="👤 Имя пользователя" required>
            <input type="password" name="password" placeholder="🔒 Пароль" required>
            <button type="submit">Войти в систему</button>
        </form>
        
        <div class="info">
            <strong>🔐 Демо-доступ:</strong><br>
            👑 Администратор: <strong>admin</strong> / <strong>admin123</strong><br>
            👤 Пользователь: <strong>user</strong> / <strong>user123</strong>
        </div>
    </div>
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
        }
        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .nav-links { display: flex; gap: 15px; align-items: center; }
        .nav-links a {
            color: #333;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: 600;
        }
        .nav-links a:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 8px 20px;
            border-radius: 30px;
            color: white;
        }
        .role-badge { padding: 3px 10px; border-radius: 20px; font-size: 11px; background: #ffd700; color: #667eea; }
        .logout-btn { background: #e53e3e; padding: 6px 15px; border-radius: 20px; color: white; text-decoration: none; }
        .container { max-width: 1400px; margin: 30px auto; padding: 0 30px; }
        .welcome {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px;
        }
        .welcome h2 { color: #667eea; margin-bottom: 10px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-card h4 { color: #667eea; font-size: 12px; margin-bottom: 10px; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: #333; }
        .table-container {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
        }
        table { width: 100%; border-collapse: collapse; min-width: 700px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: rgba(102,126,234,0.1); color: #667eea; }
        tr:hover { background: rgba(102,126,234,0.05); }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
        }
        .btn-small { padding: 5px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; }
        .btn-info { background: #4299e1; color: white; }
        .btn-warning { background: #ed8936; color: white; }
        .btn-danger { background: #e53e3e; color: white; }
        .admin-buttons { display: flex; gap: 10px; justify-content: flex-end; margin-bottom: 20px; }
        .footer {
            background: rgba(255,255,255,0.9);
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: #666;
        }
        @media (max-width: 768px) {
            .nav-container { flex-direction: column; gap: 10px; }
            .stats-grid { gap: 10px; }
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
                {% if is_admin %}
                <a href="/add">➕ Добавить</a>
                <a href="/users">👥 Пользователи</a>
                {% endif %}
                <div class="user-info">
                    👋 {{ username }}
                    <span class="role-badge">{{ role_text }}</span>
                    <a href="/logout" class="logout-btn">Выйти</a>
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
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="color: #667eea;">📋 Ассортимент специй</h2>
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
                    <tr><th>ID</th><th>Наименование</th><th>Поставщик</th><th>Цена</th><th>Остаток</th></tr>
                </thead>
                <tbody>
                    {% for s in spices %}
                    <tr>
                        <td>{{ s.id }}</td>
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

ANALYTICS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Аналитика - SpiceDrugs Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }
        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .nav-links a { color: #333; text-decoration: none; padding: 8px 16px; border-radius: 25px; }
        .container { max-width: 1400px; margin: 30px auto; padding: 0 30px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-card h4 { color: #667eea; font-size: 12px; margin-bottom: 10px; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: #333; }
        .table-container {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
        }
        table { width: 100%; border-collapse: collapse; min-width: 600px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: rgba(102,126,234,0.1); color: #667eea; }
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
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
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
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
        }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .container { max-width: 600px; margin: 50px auto; padding: 0 30px; }
        .form-box {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 40px;
            border-radius: 20px;
        }
        h2 { color: #667eea; margin-bottom: 30px; }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
        }
        .back { display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }
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
        <div class="form-box">
            <h2>➕ Добавление новой специи</h2>
            <form method="POST">
                <input type="text" name="name" placeholder="Название специи" required>
                <input type="number" step="0.01" name="price" placeholder="Цена (₽ за кг)" required>
                <input type="text" name="supplier" placeholder="Поставщик" required>
                <input type="number" name="stock" placeholder="Количество (кг)" required>
                <button type="submit">💾 Сохранить</button>
            </form>
            <a href="/" class="back">← Вернуться на главную</a>
        </div>
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
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
        }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 30px; }
        .table-box {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
            padding: 20px;
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: rgba(102,126,234,0.1); color: #667eea; }
        .back {
            display: inline-block;
            margin-top: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
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
        <h1>👥 Управление пользователями</h1>
        <div class="table-box">
            <table>
                <thead>
                    <tr><th>Логин</th><th>Имя</th><th>Роль</th><th>Дата регистрации</th></tr>
                </thead>
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
    
    import random
    for s in db.spices:
        change = random.uniform(-0.1, 0.1)
        s['price'] = round(max(10, s['price'] * (1 + change)), 2)
    
    return redirect('/')

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)