from flask import Flask, render_template_string, request, redirect, session, jsonify
import hashlib
import secrets
import os
from datetime import datetime, timedelta
import random

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
    
    def get_all_users(self):
        return [{'username': u, 'name': data['name'], 'role': data['role'], 'created_at': data['created_at']} 
                for u, data in self.users.items()]
    
    def delete_user(self, username):
        if username == 'admin':
            return False, "Нельзя удалить главного администратора"
        if username in self.users:
            del self.users[username]
            return True, "Пользователь удалён"
        return False, "Пользователь не найден"

# ==================== КЛАСС ДЛЯ РАБОТЫ СО СПЕЦИЯМИ ====================
class SpiceDatabase:
    def __init__(self):
        self.spices = self.generate_spices()
    
    def generate_spices(self):
        spices_data = [
            {'id': 1, 'name': 'Чёрный перец горошком', 'price': 890, 'supplier': 'ООО "Специи Мира"', 'stock': 100, 'rating': 5},
            {'id': 2, 'name': 'Корица цейлонская', 'price': 450, 'supplier': 'ИП "Пряный Двор"', 'stock': 45, 'rating': 4},
            {'id': 3, 'name': 'Куркума молотая', 'price': 320, 'supplier': 'ООО "Специи Мира"', 'stock': 150, 'rating': 5},
            {'id': 4, 'name': 'Паприка сладкая', 'price': 280, 'supplier': 'ООО "АгроСпеции"', 'stock': 200, 'rating': 4},
            {'id': 5, 'name': 'Имбирь молотый', 'price': 550, 'supplier': 'ИП "Пряный Двор"', 'stock': 80, 'rating': 4},
            {'id': 6, 'name': 'Кардамон зелёный', 'price': 3800, 'supplier': 'ООО "Восток-Специи"', 'stock': 25, 'rating': 5},
            {'id': 7, 'name': 'Гвоздика', 'price': 1200, 'supplier': 'ООО "Специи Мира"', 'stock': 60, 'rating': 4},
            {'id': 8, 'name': 'Мускатный орех', 'price': 1500, 'supplier': 'ИП "Пряный Двор"', 'stock': 35, 'rating': 4},
            {'id': 9, 'name': 'Кунжут белый', 'price': 250, 'supplier': 'ООО "АгроСпеции"', 'stock': 300, 'rating': 3},
            {'id': 10, 'name': 'Зира (кумин)', 'price': 420, 'supplier': 'ООО "Восток-Специи"', 'stock': 90, 'rating': 4},
            {'id': 11, 'name': 'Кориандр молотый', 'price': 290, 'supplier': 'ООО "Специи Мира"', 'stock': 120, 'rating': 3},
            {'id': 12, 'name': 'Шафран настоящий', 'price': 15000, 'supplier': 'ИП "Пряный Двор"', 'stock': 5, 'rating': 5},
            {'id': 13, 'name': 'Бадьян', 'price': 780, 'supplier': 'ООО "Восток-Специи"', 'stock': 40, 'rating': 4},
            {'id': 14, 'name': 'Асафетида', 'price': 1250, 'supplier': 'ООО "Специи Мира"', 'stock': 20, 'rating': 3},
            {'id': 15, 'name': 'Фенхель', 'price': 360, 'supplier': 'ИП "Пряный Двор"', 'stock': 110, 'rating': 3},
            {'id': 16, 'name': 'Тмин', 'price': 310, 'supplier': 'ООО "АгроСпеции"', 'stock': 95, 'rating': 4},
            {'id': 17, 'name': 'Горчица белая', 'price': 180, 'supplier': 'ООО "Специи Мира"', 'stock': 250, 'rating': 3},
            {'id': 18, 'name': 'Укроп', 'price': 220, 'supplier': 'ИП "Пряный Двор"', 'stock': 180, 'rating': 4},
            {'id': 19, 'name': 'Петрушка', 'price': 200, 'supplier': 'ООО "АгроСпеции"', 'stock': 200, 'rating': 4},
            {'id': 20, 'name': 'Базилик', 'price': 260, 'supplier': 'ООО "Специи Мира"', 'stock': 160, 'rating': 4},
            {'id': 21, 'name': 'Орегано', 'price': 340, 'supplier': 'ИП "Пряный Двор"', 'stock': 85, 'rating': 3},
            {'id': 22, 'name': 'Розмарин', 'price': 420, 'supplier': 'ООО "Восток-Специи"', 'stock': 70, 'rating': 4},
            {'id': 23, 'name': 'Тимьян', 'price': 380, 'supplier': 'ООО "Специи Мира"', 'stock': 75, 'rating': 3},
            {'id': 24, 'name': 'Майоран', 'price': 460, 'supplier': 'ИП "Пряный Двор"', 'stock': 55, 'rating': 3},
            {'id': 25, 'name': 'Ваниль', 'price': 8500, 'supplier': 'ООО "Восток-Специи"', 'stock': 8, 'rating': 5},
            {'id': 26, 'name': 'Перец розовый', 'price': 1850, 'supplier': 'ООО "Специи Мира"', 'stock': 30, 'rating': 4},
            {'id': 27, 'name': 'Перец душистый', 'price': 1100, 'supplier': 'ИП "Пряный Двор"', 'stock': 65, 'rating': 4},
            {'id': 28, 'name': 'Хмели-сунели', 'price': 370, 'supplier': 'ООО "АгроСпеции"', 'stock': 130, 'rating': 4},
            {'id': 29, 'name': 'Аджика', 'price': 290, 'supplier': 'ООО "Специи Мира"', 'stock': 140, 'rating': 4},
            {'id': 30, 'name': 'Карри', 'price': 390, 'supplier': 'ИП "Пряный Двор"', 'stock': 120, 'rating': 5},
            {'id': 31, 'name': 'Пажитник', 'price': 510, 'supplier': 'ООО "АгроСпеции"', 'stock': 50, 'rating': 3},
            {'id': 32, 'name': 'Чили хлопья', 'price': 470, 'supplier': 'ООО "Специи Мира"', 'stock': 95, 'rating': 4},
            {'id': 33, 'name': 'Суммах', 'price': 580, 'supplier': 'ИП "Пряный Двор"', 'stock': 45, 'rating': 3},
            {'id': 34, 'name': 'Чернушка', 'price': 440, 'supplier': 'ООО "АгроСпеции"', 'stock': 60, 'rating': 3},
            {'id': 35, 'name': 'Анис звёздчатый', 'price': 720, 'supplier': 'ООО "Восток-Специи"', 'stock': 35, 'rating': 4},
            {'id': 36, 'name': 'Барбарис сушёный', 'price': 630, 'supplier': 'ИП "Пряный Двор"', 'stock': 40, 'rating': 3},
            {'id': 37, 'name': 'Калган (корень)', 'price': 840, 'supplier': 'ООО "Специи Мира"', 'stock': 25, 'rating': 3},
            {'id': 38, 'name': 'Можжевельник', 'price': 530, 'supplier': 'ООО "АгроСпеции"', 'stock': 30, 'rating': 3},
            {'id': 39, 'name': 'Мелисса сушёная', 'price': 340, 'supplier': 'ИП "Пряный Двор"', 'stock': 70, 'rating': 3},
            {'id': 40, 'name': 'Мята перечная', 'price': 280, 'supplier': 'ООО "Специи Мира"', 'stock': 110, 'rating': 4},
            {'id': 41, 'name': 'Шалфей', 'price': 420, 'supplier': 'ООО "Восток-Специи"', 'stock': 55, 'rating': 3},
            {'id': 42, 'name': 'Эстрагон', 'price': 390, 'supplier': 'ИП "Пряный Двор"', 'stock': 65, 'rating': 3},
            {'id': 43, 'name': 'Кинза сушёная', 'price': 300, 'supplier': 'ООО "АгроСпеции"', 'stock': 90, 'rating': 4},
            {'id': 44, 'name': 'Лавровый лист', 'price': 140, 'supplier': 'ООО "Специи Мира"', 'stock': 250, 'rating': 5},
            {'id': 45, 'name': 'Майоран садовый', 'price': 450, 'supplier': 'ИП "Пряный Двор"', 'stock': 50, 'rating': 3},
            {'id': 46, 'name': 'Чабер садовый', 'price': 480, 'supplier': 'ООО "Восток-Специи"', 'stock': 45, 'rating': 3},
            {'id': 47, 'name': 'Кресс-салат', 'price': 270, 'supplier': 'ООО "АгроСпеции"', 'stock': 80, 'rating': 3}
        ]
        
        end_date = datetime.now()
        for s in spices_data:
            price_history = []
            current_price = s['price']
            for days_ago in range(365, -1, -1):
                date = (end_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                change = random.uniform(-0.05, 0.05)
                current_price = max(10, round(current_price * (1 + change), 2))
                price_history.append({'date': date, 'price': current_price})
            s['price_history'] = price_history
        return spices_data
    
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
    
    def add_spice(self, name, price, supplier, stock, rating=3):
        new_id = max([s['id'] for s in self.spices]) + 1
        today = datetime.now().strftime('%Y-%m-%d')
        price_history = []
        current_price = float(price)
        for days_ago in range(365, -1, -1):
            date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            price_history.append({'date': date, 'price': current_price})
        self.spices.append({
            'id': new_id,
            'name': name,
            'price': float(price),
            'supplier': supplier,
            'stock': int(stock),
            'rating': int(rating),
            'price_history': price_history
        })
        return True
    
    def update_spice(self, spice_id, name, price, supplier, stock, rating=None):
        spice = self.get_spice_by_id(spice_id)
        if spice:
            spice['name'] = name
            spice['price'] = float(price)
            spice['supplier'] = supplier
            spice['stock'] = int(stock)
            if rating:
                spice['rating'] = int(rating)
            spice['price_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'price': float(price)
            })
            return True
        return False
    
    def delete_spice(self, spice_id):
        self.spices = [s for s in self.spices if s['id'] != spice_id]
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
    
    def get_price_history_for_period(self, spice_id, period):
        spice = self.get_spice_by_id(spice_id)
        if not spice:
            return [], []
        
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=365)
        
        filtered = [h for h in spice['price_history'] 
                   if datetime.strptime(h['date'], '%Y-%m-%d') >= start_date]
        
        dates = [h['date'] for h in filtered]
        prices = [h['price'] for h in filtered]
        return dates, prices

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
                    <input type="text" name="username" required placeholder="Придумайте логин">
                </div>
                <div class="form-group">
                    <label>👨 Ваше имя</label>
                    <input type="text" name="name" required placeholder="Как вас зовут?">
                </div>
                <div class="form-group">
                    <label>🔒 Пароль</label>
                    <input type="password" name="password" required placeholder="Минимум 4 символа">
                </div>
                <div class="form-group">
                    <label>🔒 Подтверждение пароля</label>
                    <input type="password" name="confirm" required placeholder="Повторите пароль">
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
        
        document.querySelector('#panel-register form').onsubmit = function() {
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
        };
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
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, rgba(102,126,234,0.95) 0%, rgba(118,75,162,0.95) 100%);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            transition: all 0.3s;
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
        }
        .stat-card:hover { transform: translateY(-3px); }
        .stat-card h4 { color: rgba(255,255,255,0.9); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: 700; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: white; }
        
        .table-container {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
            box-shadow: 0 5px 25px rgba(0,0,0,0.1);
            border: 1px solid rgba(102,126,234,0.2);
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            min-width: 1000px;
        }
        th { 
            padding: 15px 12px; 
            text-align: left; 
            background: rgba(102,126,234,0.1); 
            color: #667eea; 
            font-weight: 700; 
            font-size: 14px;
            border-bottom: 2px solid rgba(102,126,234,0.2);
        }
        td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #f0f0f0; 
            color: #333; 
            font-weight: 500;
            vertical-align: middle;
        }
        tr:hover { background: rgba(102,126,234,0.05); }
        
        .stars { display: inline-flex; gap: 2px; }
        .star { color: #ddd; font-size: 16px; }
        .star.filled { color: #ffc107; }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 20px;
            border: none;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
        
        .btn-small { 
            padding: 4px 10px; 
            border-radius: 20px; 
            text-decoration: none; 
            font-size: 11px; 
            margin: 0 2px; 
            display: inline-block; 
            transition: all 0.2s; 
            font-weight: 600; 
        }
        .btn-info { background: #4299e1; color: white; }
        .btn-warning { background: #ed8936; color: white; }
        .btn-danger { background: #e53e3e; color: white; }
        .btn-small:hover { transform: translateY(-1px); opacity: 0.9; }
        
        .footer {
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
            color: #333;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-top: 1px solid rgba(102,126,234,0.2);
            font-weight: 500;
        }
        
        .admin-buttons { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; justify-content: flex-end; }
        .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }
        .header-actions h2 { color: #667eea; font-weight: 700; font-size: 22px; }
        
        @media (max-width: 768px) {
            .nav-container { flex-direction: column; gap: 10px; }
            .stats-grid { gap: 10px; }
            th, td { padding: 8px; font-size: 12px; }
            .star { font-size: 12px; }
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
                <a href="/spice-graph">📊 Графики цен</a>
                {% if is_admin %}
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
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{{ stats.avg_price }} ₽/кг</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{{ stats.min_price }} / {{ stats.max_price }} ₽/кг</div></div>
            <div class="stat-card"><h4>📦 Общий запас</h4><div class="value">{{ stats.total_stock }} кг</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{{ stats.total_value }} ₽</div></div>
        </div>
        
        <div class="header-actions">
            <h2>📋 Ассортимент специй</h2>
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
                    <tr>
                        <th>ID</th>
                        <th>Наименование</th>
                        <th>Поставщик</th>
                        <th>Цена (за кг)</th>
                        <th>Цена (за 100 г)</th>
                        <th>Остаток</th>
                        <th>Рейтинг</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for s in spices %}
                    <tr>
                        <td>{{ s.id }}</td>
                        <td><strong>{{ s.name }}</strong></td>
                        <td>{{ s.supplier }}</td>
                        <td>{{ s.price }} ₽</td>
                        <td>{{ "%.2f"|format(s.price / 10) }} ₽</td>
                        <td>{{ s.stock }} кг</td>
                        <td class="stars">
                            {% for i in range(1, 6) %}
                                {% if i <= s.rating %}
                                    <span class="star filled">★</span>
                                {% else %}
                                    <span class="star">★</span>
                                {% endif %}
                            {% endfor %}
                        </td>
                        <td class="actions">
                            <a href="/history/{{ s.id }}" class="btn-small btn-info">📊 История</a>
                            {% if is_admin %}
                            <a href="/edit/{{ s.id }}" class="btn-small btn-warning">✏️</a>
                            <a href="/delete/{{ s.id }}" class="btn-small btn-danger" onclick="return confirm('Удалить {{ s.name }}?')">🗑️</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
        <p style="font-size: 12px; margin-top: 8px;">© 2024 Все права защищены</p>
    </div>
</body>
</html>
'''

SPICE_GRAPH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Графики цен - SpiceDrugs Pro</title>
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
        .nav-links a { color: #333; text-decoration: none; margin-left: 25px; padding: 8px 16px; border-radius: 25px; font-weight: 600; }
        .nav-links a:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 30px; }
        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        .selector {
            display: flex;
            gap: 20px;
            align-items: flex-end;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        .selector-group { flex: 1; min-width: 200px; }
        .selector-group label { display: block; margin-bottom: 8px; font-weight: 700; color: #667eea; }
        .selector-group select, .selector-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 14px;
        }
        .selector-group select:focus { outline: none; border-color: #667eea; }
        .period-buttons {
            display: flex;
            gap: 12px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .period-btn {
            padding: 8px 22px;
            background: #e0e0e0;
            color: #333;
            border-radius: 30px;
            cursor: pointer;
            border: none;
            font-weight: 600;
            transition: all 0.3s;
        }
        .period-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 28px;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 700;
        }
        .chart-container { text-align: center; margin-top: 20px; }
        canvas { max-width: 100%; height: auto; background: #f8f9ff; border-radius: 15px; }
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        .stat-mini {
            background: rgba(102,126,234,0.1);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-mini .label { font-size: 12px; color: #666; }
        .stat-mini .value { font-size: 20px; font-weight: bold; color: #667eea; }
        .back {
            display: inline-block;
            margin-top: 20px;
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
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/spice-graph">📊 Графики цен</a>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h1>📈 Графики цен на специи</h1>
            
            <div class="selector">
                <div class="selector-group">
                    <label>Выберите специю:</label>
                    <select id="spice-select">
                        {% for s in spices %}
                        <option value="{{ s.id }}" {% if s.id == current_spice.id %}selected{% endif %}>{{ s.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="selector-group">
                    <label>&nbsp;</label>
                    <button class="btn-primary" onclick="updateChart()">Показать график</button>
                </div>
            </div>
            
            <div class="period-buttons">
                <button class="period-btn" onclick="setPeriod('week')">📅 Неделя</button>
                <button class="period-btn active" onclick="setPeriod('month')">📆 Месяц</button>
                <button class="period-btn" onclick="setPeriod('year')">📊 Год</button>
            </div>
            
            <div class="chart-container">
                <canvas id="priceChart" width="800" height="400" style="width:100%; max-width:800px; height:auto;"></canvas>
            </div>
            
            <div class="stats-row" id="stats-container"></div>
        </div>
        
        <div style="text-align: center;">
            <a href="/" class="back">← Вернуться на главную</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
    </div>
    
    <script>
        let currentPeriod = 'month';
        let currentSpiceId = {{ current_spice.id }};
        
        async function fetchData(spiceId, period) {
            const response = await fetch(`/api/chart-data/${spiceId}/${period}`);
            return await response.json();
        }
        
        function drawChart(prices, dates, period) {
            const canvas = document.getElementById('priceChart');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const container = canvas.parentElement;
            const w = container.clientWidth;
            const h = 400;
            canvas.width = w;
            canvas.height = h;
            
            if (!prices || prices.length < 2) {
                ctx.fillStyle = '#999';
                ctx.font = '14px Arial';
                ctx.fillText('Недостаточно данных для отображения', w/2-100, h/2);
                return;
            }
            
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const range = maxPrice - minPrice || 1;
            const avgPrice = prices.reduce((a,b) => a + b, 0) / prices.length;
            const startPrice = prices[0];
            const currentPrice = prices[prices.length-1];
            const change = currentPrice - startPrice;
            const changePercent = (change / startPrice) * 100;
            
            document.getElementById('stats-container').innerHTML = `
                <div class="stat-mini"><div class="label">📉 Минимум</div><div class="value">${minPrice.toFixed(2)} ₽</div></div>
                <div class="stat-mini"><div class="label">📈 Максимум</div><div class="value">${maxPrice.toFixed(2)} ₽</div></div>
                <div class="stat-mini"><div class="label">📊 Средняя</div><div class="value">${avgPrice.toFixed(2)} ₽</div></div>
                <div class="stat-mini"><div class="label">🔄 Изменение</div><div class="value" style="color: ${change > 0 ? '#e53e3e' : change < 0 ? '#48bb78' : '#666'}">${change > 0 ? '▲' : change < 0 ? '▼' : '●'} ${Math.abs(change).toFixed(2)} ₽ (${Math.abs(changePercent).toFixed(1)}%)</div></div>
            `;
            
            const paddingLeft = 50;
            const paddingRight = 30;
            const paddingTop = 20;
            const paddingBottom = 40;
            const chartW = w - paddingLeft - paddingRight;
            const chartH = h - paddingTop - paddingBottom;
            
            ctx.clearRect(0, 0, w, h);
            
            for (let i = 0; i <= 4; i++) {
                const y = paddingTop + (i / 4) * chartH;
                ctx.beginPath();
                ctx.strokeStyle = '#e0e0e0';
                ctx.moveTo(paddingLeft, y);
                ctx.lineTo(w - paddingRight, y);
                ctx.stroke();
                ctx.fillStyle = '#999';
                ctx.font = '10px Arial';
                ctx.fillText(`${(maxPrice - (i / 4) * range).toFixed(0)} ₽`, 5, y + 3);
            }
            
            const stepX = chartW / (prices.length - 1);
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2.5;
            
            for (let i = 0; i < prices.length; i++) {
                const x = paddingLeft + i * stepX;
                const y = paddingTop + chartH - ((prices[i] - minPrice) / range) * chartH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            
            ctx.lineTo(paddingLeft + (prices.length - 1) * stepX, paddingTop + chartH);
            ctx.lineTo(paddingLeft, paddingTop + chartH);
            ctx.fillStyle = 'rgba(102,126,234,0.1)';
            ctx.fill();
            
            for (let i = 0; i < prices.length; i++) {
                const x = paddingLeft + i * stepX;
                const y = paddingTop + chartH - ((prices[i] - minPrice) / range) * chartH;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffd700';
                ctx.fill();
            }
            
            const currentY = paddingTop + chartH - ((currentPrice - minPrice) / range) * chartH;
            ctx.beginPath();
            ctx.strokeStyle = '#ffd700';
            ctx.setLineDash([8, 4]);
            ctx.moveTo(paddingLeft, currentY);
            ctx.lineTo(w - paddingRight, currentY);
            ctx.stroke();
            ctx.setLineDash([]);
        }
        
        async function updateChart() {
            const spiceId = document.getElementById('spice-select').value;
            currentSpiceId = spiceId;
            const data = await fetchData(spiceId, currentPeriod);
            drawChart(data.prices, data.dates, currentPeriod);
        }
        
        async function setPeriod(period) {
            currentPeriod = period;
            document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            const data = await fetchData(currentSpiceId, period);
            drawChart(data.prices, data.dates, period);
        }
        
        window.onload = async function() {
            const data = await fetchData(currentSpiceId, currentPeriod);
            drawChart(data.prices, data.dates, currentPeriod);
            window.addEventListener('resize', () => setTimeout(updateChart, 200));
        };
    </script>
</body>
</html>
'''

HISTORY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>История цен - {{ spice.name }}</title>
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
        .nav-container { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .container { max-width: 800px; margin: 30px auto; padding: 0 30px; }
        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        .price { font-size: 32px; color: #2d5a3b; font-weight: bold; }
        .price-100g { font-size: 16px; color: #888; margin-top: 5px; }
        .stars { display: inline-flex; gap: 3px; margin-left: 10px; }
        .star { color: #ddd; font-size: 20px; }
        .star.filled { color: #ffc107; }
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
        canvas { width: 100%; height: auto; background: #f8f9ff; border-radius: 15px; }
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
            <h1>📈 История цен: {{ spice.name }}
                <span class="stars">
                    {% for i in range(1, 6) %}
                        {% if i <= spice.rating %}
                            <span class="star filled">★</span>
                        {% else %}
                            <span class="star">★</span>
                        {% endif %}
                    {% endfor %}
                </span>
            </h1>
            <div class="price">💰 Цена за кг: {{ spice.price }} ₽</div>
            <div class="price-100g">📊 Цена за 100 г: {{ "%.2f"|format(spice.price / 10) }} ₽</div>
            <p style="margin-top: 20px;">🏭 Поставщик: {{ spice.supplier }}</p>
            <p>📦 Остаток: {{ spice.stock }} кг</p>
        </div>
        
        <div class="card">
            <h2>📊 Динамика цены (90 дней)</h2>
            <canvas id="priceChart" width="700" height="300"></canvas>
        </div>
        
        <div style="text-align: center;">
            <a href="/" class="back">← На главную</a>
            <a href="/spice-graph" class="back" style="background: #4299e1;">📊 Все графики</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
    </div>
    
    <script>
        const prices = {{ prices | tojson }};
        const canvas = document.getElementById('priceChart');
        const ctx = canvas.getContext('2d');
        const container = canvas.parentElement;
        const w = container.clientWidth;
        const h = 300;
        canvas.width = w;
        canvas.height = h;
        
        if (prices && prices.length > 1) {
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const range = maxPrice - minPrice || 1;
            const padding = 40;
            const chartW = w - padding * 2;
            const chartH = h - padding * 2;
            const stepX = chartW / (prices.length - 1);
            
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2;
            for (let i = 0; i < prices.length; i++) {
                const x = padding + i * stepX;
                const y = padding + chartH - ((prices[i] - minPrice) / range) * chartH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            
            for (let i = 0; i < prices.length; i++) {
                const x = padding + i * stepX;
                const y = padding + chartH - ((prices[i] - minPrice) / range) * chartH;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffd700';
                ctx.fill();
            }
        }
    </script>
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
        table { width: 100%; border-collapse: collapse; min-width: 900px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }
        th { background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; }
        tr:hover { background: rgba(102,126,234,0.05); }
        .stock-status { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .stock-low { background: #e53e3e; color: white; }
        .stock-medium { background: #ed8936; color: white; }
        .stock-high { background: #48bb78; color: white; }
        .stars { display: inline-flex; gap: 2px; }
        .star { color: #ddd; font-size: 14px; }
        .star.filled { color: #ffc107; }
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
                <a href="/spice-graph">📊 Графики</a>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card"><h4>🌶️ Всего специй</h4><div class="value">{{ stats.total_items }}</div></div>
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{{ stats.avg_price }} ₽/кг</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{{ stats.min_price }} / {{ stats.max_price }} ₽/кг</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{{ stats.total_value }} ₽</div></div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Специя</th>
                        <th>Поставщик</th>
                        <th>Цена (за кг)</th>
                        <th>Цена (за 100 г)</th>
                        <th>Остаток</th>
                        <th>Статус</th>
                        <th>Рейтинг</th>
                    </tr>
                </thead>
                <tbody>
                    {% for s in spices %}
                    <tr>
                        <td><strong>{{ s.name }}</strong></td>
                        <td>{{ s.supplier }}</td>
                        <td>{{ s.price }} ₽</td>
                        <td>{{ "%.2f"|format(s.price / 10) }} ₽</td>
                        <td>{{ s.stock }} кг</td>
                        <td>
                            {% if s.stock < 30 %}
                                <span class="stock-status stock-low">⚠️ МАЛО</span>
                            {% elif s.stock > 150 %}
                                <span class="stock-status stock-high">✓ В ИЗБЫТКЕ</span>
                            {% else %}
                                <span class="stock-status stock-medium">➖ НОРМА</span>
                            {% endif %}
                        </td>
                        <td class="stars">
                            {% for i in range(1, 6) %}
                                {% if i <= s.rating %}
                                    <span class="star filled">★</span>
                                {% else %}
                                    <span class="star">★</span>
                                {% endif %}
                            {% endfor %}
                            ({{ s.rating }}/5)
                        </td>
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
        input, select { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 12px; transition: 0.3s; }
        input:focus, select:focus { outline: none; border-color: #667eea; }
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
            <div class="form-group"><label>⭐ Рейтинг (1-5)</label><input type="number" name="rating" min="1" max="5" value="3" required></div>
            <button type="submit">💾 Сохранить</button>
        </form>
        <a href="/" class="back">← Вернуться на главную</a>
    </div>
</body>
</html>
'''

EDIT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Редактировать - {{ spice.name }}</title>
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
        h2 { color: #ed8936; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 12px; }
        button { background: #ed8936; color: white; padding: 12px 30px; border: none; border-radius: 30px; cursor: pointer; font-size: 16px; font-weight: 600; }
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
        <h2>✏️ Редактирование: {{ spice.name }}</h2>
        <form method="POST">
            <div class="form-group"><label>🌿 Название</label><input type="text" name="name" value="{{ spice.name }}" required></div>
            <div class="form-group"><label>💰 Цена (₽ за кг)</label><input type="number" step="0.01" name="price" value="{{ spice.price }}" required></div>
            <div class="form-group"><label>🏭 Поставщик</label><input type="text" name="supplier" value="{{ spice.supplier }}" required></div>
            <div class="form-group"><label>📦 Количество (кг)</label><input type="number" name="stock" value="{{ spice.stock }}" required></div>
            <div class="form-group"><label>⭐ Рейтинг (1-5)</label><input type="number" name="rating" min="1" max="5" value="{{ spice.rating }}" required></div>
            <button type="submit">💾 Сохранить изменения</button>
        </form>
        <a href="/" class="back">← Назад</a>
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
        table { width: 100%; border-collapse: collapse; min-width: 700px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }
        th { background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; }
        tr:hover { background: rgba(102,126,234,0.05); }
        .btn-small { padding: 5px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; font-weight: 600; }
        .btn-danger { background: #e53e3e; color: white; }
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
                <thead>
                    <tr>
                        <th>Логин</th>
                        <th>Имя</th>
                        <th>Роль</th>
                        <th>Дата регистрации</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u in users %}
                    <tr>
                        <td>{{ u.username }}</td>
                        <td>{{ u.name }}</td>
                        <td>{{ u.role }}</td>
                        <td>{{ u.created_at }}</td>
                        <td>
                            {% if u.username != 'admin' %}
                            <a href="/delete_user/{{ u.username }}" class="btn-small btn-danger" onclick="return confirm('Удалить пользователя {{ u.username }}?')">🗑️ Удалить</a>
                            {% else %}
                            <span style="color:#999;">Защищён</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            <tr>
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

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login_page')
    
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

@app.route('/login_page')
def login_page():
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if auth.check_password(username, password):
        session['username'] = username
        return redirect('/')
    else:
        return redirect('/login_page?error=Неверный+логин+или+пароль')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    
    success, message = auth.register(username, password, name)
    if success:
        return redirect('/login_page?success=' + message)
    else:
        return redirect('/login_page?error=' + message)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login_page')

@app.route('/analytics')
def analytics():
    if 'username' not in session:
        return redirect('/login_page')
    
    stats = db.get_statistics()
    spices = db.get_all()
    return render_template_string(ANALYTICS_TEMPLATE, stats=stats, spices=spices)

@app.route('/spice-graph')
def spice_graph():
    if 'username' not in session:
        return redirect('/login_page')
    
    spices = db.get_all()
    current_spice = spices[0] if spices else None
    return render_template_string(SPICE_GRAPH_TEMPLATE, spices=spices, current_spice=current_spice)

@app.route('/api/chart-data/<int:spice_id>/<period>')
def chart_data(spice_id, period):
    dates, prices = db.get_price_history_for_period(spice_id, period)
    return {'dates': dates, 'prices': prices}

@app.route('/history/<int:spice_id>')
def history(spice_id):
    if 'username' not in session:
        return redirect('/login_page')
    
    spice = db.get_spice_by_id(spice_id)
    if not spice:
        return redirect('/')
    
    prices = [h['price'] for h in spice['price_history'][-90:]]
    return render_template_string(HISTORY_TEMPLATE, spice=spice, prices=prices)

@app.route('/add', methods=['GET', 'POST'])
def add_spice():
    if 'username' not in session:
        return redirect('/login_page')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        supplier = request.form.get('supplier')
        stock = int(request.form.get('stock'))
        rating = int(request.form.get('rating', 3))
        
        db.add_spice(name, price, supplier, stock, rating)
        return redirect('/')
    
    return render_template_string(ADD_TEMPLATE)

@app.route('/edit/<int:spice_id>', methods=['GET', 'POST'])
def edit_spice(spice_id):
    if 'username' not in session:
        return redirect('/login_page')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    spice = db.get_spice_by_id(spice_id)
    if not spice:
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        supplier = request.form.get('supplier')
        stock = int(request.form.get('stock'))
        rating = int(request.form.get('rating', 3))
        
        db.update_spice(spice_id, name, price, supplier, stock, rating)
        return redirect('/')
    
    return render_template_string(EDIT_TEMPLATE, spice=spice)

@app.route('/delete/<int:spice_id>')
def delete_spice(spice_id):
    if 'username' not in session:
        return redirect('/login_page')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    db.delete_spice(spice_id)
    return redirect('/')

@app.route('/users')
def users_list():
    if 'username' not in session:
        return redirect('/login_page')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    users = auth.get_all_users()
    return render_template_string(USERS_TEMPLATE, users=users)

@app.route('/delete_user/<username>')
def delete_user(username):
    if 'username' not in session:
        return redirect('/login_page')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    auth.delete_user(username)
    return redirect('/users')

@app.route('/monitor')
def monitor_prices():
    if 'username' not in session:
        return redirect('/login_page')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    db.update_prices()
    return redirect('/')

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)