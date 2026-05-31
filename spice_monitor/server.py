import socket
import urllib.parse
import json
import hashlib
import secrets
import os
from datetime import datetime, timedelta
import random

# ==================== КЛАСС ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ====================
class UserAuth:
    def __init__(self):
        # Храним пользователей в памяти
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
        print("✅ Пользователи загружены")
    
    def login(self, username, password):
        if username not in self.users:
            return None
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if self.users[username]['password'] != hashed:
            return None
        token = secrets.token_hex(32)
        self.sessions[token] = username
        return token
    
    def check_auth(self, token):
        return token in self.sessions
    
    def get_user(self, token):
        if token in self.sessions:
            username = self.sessions[token]
            return self.users.get(username)
        return None
    
    def is_admin(self, token):
        user = self.get_user(token)
        return user and user.get('role') == 'admin'

# ==================== КЛАСС ДЛЯ РАБОТЫ СО СПЕЦИЯМИ ====================
class SpiceDatabase:
    def __init__(self):
        self.spices = self.generate_spices()
    
    def generate_spices(self):
        spices = [
            {'id': 1, 'name': 'Чёрный перец горошком', 'price': 350, 'supplier': 'ООО "Специи Мира"', 'stock': 100, 'trend': 'stable'},
            {'id': 2, 'name': 'Корица цейлонская', 'price': 580, 'supplier': 'ИП "Пряный Двор"', 'stock': 45, 'trend': 'up'},
            {'id': 3, 'name': 'Куркума молотая', 'price': 220, 'supplier': 'ООО "Специи Мира"', 'stock': 150, 'trend': 'down'},
            {'id': 4, 'name': 'Паприка сладкая', 'price': 180, 'supplier': 'ООО "АгроСпеции"', 'stock': 200, 'trend': 'stable'},
            {'id': 5, 'name': 'Имбирь молотый', 'price': 320, 'supplier': 'ИП "Пряный Двор"', 'stock': 80, 'trend': 'up'},
            {'id': 6, 'name': 'Кардамон зелёный', 'price': 1250, 'supplier': 'ООО "Восток-Специи"', 'stock': 25, 'trend': 'up'},
            {'id': 7, 'name': 'Гвоздика', 'price': 450, 'supplier': 'ООО "Специи Мира"', 'stock': 60, 'trend': 'down'},
            {'id': 8, 'name': 'Мускатный орех', 'price': 680, 'supplier': 'ИП "Пряный Двор"', 'stock': 35, 'trend': 'stable'},
            {'id': 9, 'name': 'Кунжут белый', 'price': 150, 'supplier': 'ООО "АгроСпеции"', 'stock': 300, 'trend': 'down'},
            {'id': 10, 'name': 'Зира (кумин)', 'price': 280, 'supplier': 'ООО "Восток-Специи"', 'stock': 90, 'trend': 'stable'},
            {'id': 11, 'name': 'Кориандр молотый', 'price': 190, 'supplier': 'ООО "Специи Мира"', 'stock': 120, 'trend': 'up'},
            {'id': 12, 'name': 'Шафран настоящий', 'price': 3500, 'supplier': 'ИП "Пряный Двор"', 'stock': 5, 'trend': 'up'},
            {'id': 13, 'name': 'Бадьян', 'price': 520, 'supplier': 'ООО "Восток-Специи"', 'stock': 40, 'trend': 'stable'},
            {'id': 14, 'name': 'Асафетида', 'price': 890, 'supplier': 'ООО "Специи Мира"', 'stock': 20, 'trend': 'down'},
            {'id': 15, 'name': 'Фенхель семена', 'price': 240, 'supplier': 'ИП "Пряный Двор"', 'stock': 110, 'trend': 'stable'},
            {'id': 16, 'name': 'Тмин', 'price': 210, 'supplier': 'ООО "АгроСпеции"', 'stock': 95, 'trend': 'up'},
            {'id': 17, 'name': 'Горчица белая', 'price': 120, 'supplier': 'ООО "Специи Мира"', 'stock': 250, 'trend': 'down'},
            {'id': 18, 'name': 'Укроп семена', 'price': 160, 'supplier': 'ИП "Пряный Двор"', 'stock': 180, 'trend': 'stable'},
            {'id': 19, 'name': 'Петрушка сушёная', 'price': 140, 'supplier': 'ООО "АгроСпеции"', 'stock': 200, 'trend': 'stable'},
            {'id': 20, 'name': 'Базилик сушёный', 'price': 170, 'supplier': 'ООО "Специи Мира"', 'stock': 160, 'trend': 'up'},
            {'id': 21, 'name': 'Орегано', 'price': 230, 'supplier': 'ИП "Пряный Двор"', 'stock': 85, 'trend': 'down'},
            {'id': 22, 'name': 'Розмарин', 'price': 290, 'supplier': 'ООО "Восток-Специи"', 'stock': 70, 'trend': 'stable'},
            {'id': 23, 'name': 'Тимьян', 'price': 260, 'supplier': 'ООО "Специи Мира"', 'stock': 75, 'trend': 'up'},
            {'id': 24, 'name': 'Майоран', 'price': 310, 'supplier': 'ИП "Пряный Двор"', 'stock': 55, 'trend': 'down'},
            {'id': 25, 'name': 'Ваниль стручки', 'price': 2800, 'supplier': 'ООО "Восток-Специи"', 'stock': 8, 'trend': 'up'},
            {'id': 26, 'name': 'Перец розовый', 'price': 720, 'supplier': 'ООО "Специи Мира"', 'stock': 30, 'trend': 'stable'},
            {'id': 27, 'name': 'Перец душистый', 'price': 430, 'supplier': 'ИП "Пряный Двор"', 'stock': 65, 'trend': 'down'},
            {'id': 28, 'name': 'Хмели-сунели', 'price': 250, 'supplier': 'ООО "АгроСпеции"', 'stock': 130, 'trend': 'stable'},
            {'id': 29, 'name': 'Аджика сухая', 'price': 200, 'supplier': 'ООО "Специи Мира"', 'stock': 140, 'trend': 'up'},
            {'id': 30, 'name': 'Карри', 'price': 270, 'supplier': 'ИП "Пряный Двор"', 'stock': 120, 'trend': 'stable'},
            {'id': 31, 'name': 'Пажитник', 'price': 340, 'supplier': 'ООО "Восток-Специи"', 'stock': 50, 'trend': 'down'},
            {'id': 32, 'name': 'Чили хлопья', 'price': 310, 'supplier': 'ООО "Специи Мира"', 'stock': 95, 'trend': 'up'},
            {'id': 33, 'name': 'Суммах', 'price': 380, 'supplier': 'ИП "Пряный Двор"', 'stock': 45, 'trend': 'stable'},
            {'id': 34, 'name': 'Чернушка', 'price': 290, 'supplier': 'ООО "АгроСпеции"', 'stock': 60, 'trend': 'down'}
        ]
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
    
    def update_prices(self):
        for spice in self.spices:
            change = random.uniform(-0.1, 0.1)
            new_price = max(10, round(spice['price'] * (1 + change), 2))
            if new_price > spice['price']:
                spice['trend'] = 'up'
            elif new_price < spice['price']:
                spice['trend'] = 'down'
            else:
                spice['trend'] = 'stable'
            spice['price'] = new_price
        return True

# ==================== ОСНОВНОЙ СЕРВЕР ====================
class HTTPServer:
    def __init__(self):
        self.auth = UserAuth()
        self.db = SpiceDatabase()
        print("🚀 Сервер инициализирован")
    
    def get_session_token(self, data):
        for line in data.split('\n'):
            if 'Cookie:' in line:
                try:
                    cookie = line.split('Cookie:')[1].strip()
                    for c in cookie.split(';'):
                        if 'session=' in c:
                            return c.split('session=')[1].strip()
                except:
                    pass
        return None
    
    def handle(self, data):
        try:
            lines = data.split('\n')
            if not lines:
                return self.not_found()
            
            parts = lines[0].split(' ')
            if len(parts) < 2:
                return self.not_found()
            
            method, path = parts[0], parts[1]
            token = self.get_session_token(data)
            is_auth = self.auth.check_auth(token)
            is_admin = self.auth.is_admin(token)
            
            # Разбираем параметры URL
            if '?' in path:
                path, query = path.split('?', 1)
                params = urllib.parse.parse_qs(query)
            else:
                params = {}
            
            # Страница входа
            if path == '/' or path == '/login':
                if is_auth:
                    return self.index_page(token)
                return self.login_page()
            
            if not is_auth:
                return self.redirect('/')
            
            # Выход
            if path == '/logout':
                response = "HTTP/1.1 302 Found\r\n"
                response += "Location: /\r\n"
                response += "Set-Cookie: session=; Path=/; Max-Age=0\r\n"
                response += "Content-Length: 0\r\n\r\n"
                return response.encode()
            
            # Обработка POST запроса на вход
            if path == '/do_login' and method == 'POST':
                body = data.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in data else ''
                params = urllib.parse.parse_qs(body)
                username = params.get('username', [''])[0]
                password = params.get('password', [''])[0]
                
                user_token = self.auth.login(username, password)
                if user_token:
                    response = "HTTP/1.1 302 Found\r\n"
                    response += "Location: /\r\n"
                    response += "Set-Cookie: session=" + user_token + "; Path=/\r\n"
                    response += "Content-Length: 0\r\n\r\n"
                    return response.encode()
                else:
                    return self.redirect_with_error('/', 'Неверный логин или пароль')
            
            # Страницы для авторизованных пользователей
            if method == 'GET':
                if path == '/':
                    return self.index_page(token)
                elif path == '/analytics':
                    return self.analytics_page(token)
                elif path == '/history':
                    spice_id = int(params.get('id', [0])[0])
                    return self.history_page(token, spice_id)
                elif path == '/monitor' and is_admin:
                    self.db.update_prices()
                    return self.redirect('/')
                elif path == '/add' and is_admin:
                    return self.add_form_page(token)
                elif path == '/edit' and is_admin:
                    spice_id = int(params.get('id', [0])[0])
                    return self.edit_form_page(token, spice_id)
                elif path == '/delete' and is_admin:
                    return self.not_found()  # Упрощённо
                elif path == '/users' and is_admin:
                    return self.users_page(token)
            
            # POST запросы
            if method == 'POST':
                body = data.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in data else ''
                if path == '/add' and is_admin:
                    return self.add_spice(body)
                elif path == '/edit' and is_admin:
                    spice_id = int(params.get('id', [0])[0])
                    return self.update_spice(spice_id, body)
            
            return self.not_found()
        except Exception as e:
            print(f"Ошибка: {e}")
            return self.error_page(str(e))
    
    def login_page(self):
        html = '''<!DOCTYPE html>
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
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            width: 400px;
            max-width: 90%;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a472a 0%, #2d5a3b 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .logo-icon { font-size: 50px; margin-bottom: 10px; }
        .form-panel { padding: 40px; }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
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
        }
        .btn-submit:hover { transform: translateY(-2px); }
        .message {
            margin: 20px;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            display: none;
        }
        .message.error { background: #fee; color: #c33; display: block; }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        .info {
            background: #e8f5e9;
            padding: 15px;
            margin-top: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .info p { margin: 5px 0; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="header">
            <div class="logo-icon">🌶️</div>
            <h1>SpiceDrugs Pro</h1>
            <p>Система мониторинга специй</p>
        </div>
        <div class="form-panel">
            <form method="POST" action="/do_login">
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
            <div class="info">
                <p><strong>🔐 Демо-доступ:</strong></p>
                <p>👑 Администратор: <strong>admin</strong> / <strong>admin123</strong></p>
                <p>👤 Пользователь: <strong>user</strong> / <strong>user123</strong></p>
            </div>
        </div>
        <div class="footer">
            <p>© 2024 SpiceDrugs Pro — Система мониторинга специй</p>
        </div>
    </div>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('error')) {
            const msg = document.createElement('div');
            msg.className = 'message error';
            msg.textContent = urlParams.get('error');
            document.querySelector('.form-panel').insertBefore(msg, document.querySelector('form'));
        }
    </script>
</body>
</html>'''
        return self.http_response(200, html)
    
    def index_page(self, token):
        user = self.auth.get_user(token)
        username = user.get('name', 'Пользователь')
        is_admin = self.auth.is_admin(token)
        spices = self.db.get_all()
        stats = self.db.get_statistics()
        
        rows = ''
        for s in spices:
            trend_class = ''
            trend_symbol = ''
            if s['trend'] == 'up':
                trend_class = 'trend-up'
                trend_symbol = '📈'
            elif s['trend'] == 'down':
                trend_class = 'trend-down'
                trend_symbol = '📉'
            else:
                trend_class = 'trend-stable'
                trend_symbol = '➖'
            
            stock_class = ''
            if s['stock'] == 0:
                stock_class = 'stock-out'
            elif s['stock'] < 50:
                stock_class = 'stock-low'
            else:
                stock_class = 'stock-normal'
            
            rows += f'''
            <tr>
                <td>{s['id']}</td>
                <td><strong>{s['name']}</strong></td>
                <td>{s['supplier']}</td>
                <td class="{trend_class}">{s['price']} ₽ {trend_symbol}</td>
                <td><span class="stock-badge {stock_class}">{s['stock']} кг</span></td>
                <td class="actions">
                    <a href="/history?id={s['id']}" class="btn-small btn-info">📊 История</a>
                </td>
            </tr>
            '''
        
        admin_buttons = ''
        if is_admin:
            admin_buttons = f'''
            <div class="admin-buttons">
                <a href="/add" class="btn-primary">➕ Добавить специю</a>
                <a href="/monitor" class="btn-primary">🔄 Мониторинг цен</a>
                <a href="/users" class="btn-primary">👥 Управление пользователями</a>
            </div>
            '''
        
        role_badge = 'admin' if is_admin else 'user'
        role_text = '👑 Администратор' if is_admin else '👤 Пользователь'
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpiceDrugs Pro - Мониторинг специй</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .logo span {{ color: #ffd700; background: none; }}
        .nav-links {{ display: flex; gap: 15px; align-items: center; flex-wrap: wrap; }}
        .nav-links a {{
            color: #333;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 25px;
            transition: all 0.3s;
            font-weight: 600;
        }}
        .nav-links a:hover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .user-info {{
            display: flex;
            align-items: center;
            gap: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 8px 20px;
            border-radius: 30px;
            color: white;
        }}
        .role-badge {{
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }}
        .role-badge.admin {{ background: #ffd700; color: #667eea; }}
        .role-badge.user {{ background: rgba(255,255,255,0.3); color: white; }}
        .logout-btn {{
            background: #e53e3e;
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            text-decoration: none;
        }}
        .container {{ max-width: 1400px; margin: 30px auto; padding: 0 30px; }}
        .welcome {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .welcome h2 {{ color: #667eea; margin-bottom: 10px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        .stat-card h4 {{ color: #667eea; font-size: 12px; margin-bottom: 10px; }}
        .stat-card .value {{ font-size: 28px; font-weight: bold; color: #333; }}
        .table-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; min-width: 700px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: rgba(102,126,234,0.1); color: #667eea; font-weight: 600; }}
        tr:hover {{ background: rgba(102,126,234,0.05); }}
        .trend-up {{ color: #e53e3e; font-weight: bold; }}
        .trend-down {{ color: #48bb78; font-weight: bold; }}
        .trend-stable {{ color: #666; }}
        .stock-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
        .stock-normal {{ background: #48bb78; color: white; }}
        .stock-low {{ background: #ed8936; color: white; }}
        .stock-out {{ background: #e53e3e; color: white; }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            font-weight: 600;
        }}
        .btn-small {{ padding: 5px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; display: inline-block; }}
        .btn-info {{ background: #4299e1; color: white; }}
        .admin-buttons {{ display: flex; gap: 10px; justify-content: flex-end; margin-bottom: 20px; flex-wrap: wrap; }}
        .header-actions {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }}
        .footer {{
            background: rgba(255,255,255,0.9);
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: #666;
        }}
        @media (max-width: 768px) {{
            .nav-container {{ flex-direction: column; gap: 10px; }}
            .stats-grid {{ gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <span class="user-info">
                    👋 {username}
                    <span class="role-badge {role_badge}">{role_text}</span>
                    <a href="/logout" class="logout-btn">🚪 Выйти</a>
                </span>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="welcome">
            <h2>🍃 Добро пожаловать, {username}!</h2>
            <p>Сегодня {datetime.now().strftime('%d.%m.%Y')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card"><h4>🌶️ Всего позиций</h4><div class="value">{stats['total_items']}</div></div>
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{stats['avg_price']} ₽</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{stats['min_price']} / {stats['max_price']} ₽</div></div>
            <div class="stat-card"><h4>📦 Общий запас</h4><div class="value">{stats['total_stock']} кг</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{stats['total_value']} ₽</div></div>
        </div>
        
        <div class="header-actions">
            <h2 style="color: #667eea;">📋 Ассортимент специй</h2>
            {admin_buttons}
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr><th>ID</th><th>Наименование</th><th>Поставщик</th><th>Цена</th><th>Остаток</th><th>Действия</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def analytics_page(self, token):
        is_admin = self.auth.is_admin(token)
        spices = self.db.get_all()
        stats = self.db.get_statistics()
        
        rows = ''
        for s in spices:
            trend_symbol = '📈' if s['trend'] == 'up' else '📉' if s['trend'] == 'down' else '➖'
            trend_color = '#e53e3e' if s['trend'] == 'up' else '#48bb78' if s['trend'] == 'down' else '#666'
            rows += f'''
            <tr>
                <td><strong>{s['name']}</strong></td>
                <td><span style="color:#667eea; font-weight:bold;">{s['price']} ₽</span></td>
                <td style="color: {trend_color};">{trend_symbol} {s['price']} ₽</td>
                <td style="color: {trend_color};">{trend_symbol} {s['price']} ₽</td>
                <td style="color: {trend_color};">{trend_symbol} {s['price']} ₽</td>
                <td><canvas id="mini-{s['id']}" width="100" height="30" style="width:100px;height:30px"></canvas></td>
            </tr>
            '''
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аналитика - SpiceDrugs Pro</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .logo span {{ color: #ffd700; background: none; }}
        .nav-links a {{
            color: #333;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: 600;
        }}
        .nav-links a:hover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .container {{ max-width: 1400px; margin: 30px auto; padding: 0 30px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        .stat-card h4 {{ color: #667eea; font-size: 12px; margin-bottom: 10px; }}
        .stat-card .value {{ font-size: 28px; font-weight: bold; color: #333; }}
        .table-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; min-width: 800px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: rgba(102,126,234,0.1); color: #667eea; font-weight: 600; }}
        tr:hover {{ background: rgba(102,126,234,0.05); }}
        .footer {{
            background: rgba(255,255,255,0.9);
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: #666;
        }}
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
            <div class="stat-card"><h4>🌶️ Всего специй</h4><div class="value">{stats['total_items']}</div></div>
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{stats['avg_price']} ₽</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{stats['min_price']} / {stats['max_price']} ₽</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{stats['total_value']} ₽</div></div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr><th>Специя</th><th>Цена</th><th>Неделя</th><th>Месяц</th><th>Год</th><th>График</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
    </div>
    
    <script>
        function drawMiniChart(id, values) {{
            const canvas = document.getElementById(`mini-${{id}}`);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const w = canvas.width, h = canvas.height;
            ctx.clearRect(0, 0, w, h);
            const prices = [100, 120, 115, 130, 125, 140, 135, 150, 145, 160].map(v => v * (0.5 + Math.random() * 0.5));
            const minVal = Math.min(...prices);
            const maxVal = Math.max(...prices);
            const range = maxVal - minVal || 1;
            const stepX = w / (prices.length - 1);
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 1.5;
            for (let i = 0; i < prices.length; i++) {{
                const x = i * stepX;
                const y = h - ((prices[i] - minVal) / range) * h;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }}
            ctx.stroke();
        }}
        
        window.onload = function() {{
            for (let i = 1; i <= 34; i++) {{
                drawMiniChart(i, []);
            }}
        }};
    </script>
</body>
</html>'''
        return self.http_response(200, html)
    
    def history_page(self, token, spice_id):
        spice = None
        for s in self.db.get_all():
            if s['id'] == spice_id:
                spice = s
                break
        
        if not spice:
            return self.not_found()
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>История цен - {spice['name']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }}
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .logo span {{ color: #ffd700; background: none; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 0 30px; }}
        .card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
        }}
        h1 {{ color: #667eea; margin-bottom: 20px; }}
        .price {{ font-size: 36px; color: #2d5a3b; font-weight: bold; }}
        .back {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
        }}
        .footer {{
            background: rgba(255,255,255,0.9);
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <a href="/logout" style="color:#333; text-decoration:none;">🚪 Выйти</a>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h1>📈 История цен: {spice['name']}</h1>
            <div class="price">💰 Текущая цена: {spice['price']} ₽</div>
            <p style="margin-top: 20px;">Поставщик: {spice['supplier']}</p>
            <p>Остаток на складе: {spice['stock']} кг</p>
        </div>
        
        <div class="card">
            <h2>📊 Динамика изменения цен</h2>
            <canvas id="priceChart" width="700" height="300" style="width:100%; height:auto; background:#f8f9ff; border-radius:10px;"></canvas>
        </div>
        
        <div style="text-align: center;">
            <a href="/" class="back">← Вернуться на главную</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
    </div>
    
    <script>
        const canvas = document.getElementById('priceChart');
        const ctx = canvas.getContext('2d');
        const w = canvas.parentElement.clientWidth;
        const h = 300;
        canvas.width = w;
        canvas.height = h;
        
        const prices = [{spice['price']}, {spice['price'] * 0.95}, {spice['price'] * 0.98}, {spice['price'] * 1.02}, {spice['price'] * 0.97}, {spice['price'] * 1.05}, {spice['price']}];
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const range = maxPrice - minPrice || 1;
        
        const padding = 40;
        const chartW = w - padding * 2;
        const chartH = h - padding * 2;
        const stepX = chartW / (prices.length - 1);
        
        ctx.clearRect(0, 0, w, h);
        
        ctx.beginPath();
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 2;
        for (let i = 0; i < prices.length; i++) {{
            const x = padding + i * stepX;
            const y = padding + chartH - ((prices[i] - minPrice) / range) * chartH;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}
        ctx.stroke();
        
        for (let i = 0; i < prices.length; i++) {{
            const x = padding + i * stepX;
            const y = padding + chartH - ((prices[i] - minPrice) / range) * chartH;
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fillStyle = '#ffd700';
            ctx.fill();
        }}
    </script>
</body>
</html>'''
        return self.http_response(200, html)
    
    def users_page(self, token):
        is_admin = self.auth.is_admin(token)
        if not is_admin:
            return self.redirect('/')
        
        users = self.auth.users
        rows = ''
        for username, user_data in users.items():
            rows += f'''
            <tr>
                <td style="padding: 12px 15px;">{username}</td>
                <td style="padding: 12px 15px;">{user_data['name']}</td>
                <td style="padding: 12px 15px;">{"👑 Администратор" if user_data['role'] == 'admin' else "👤 Пользователь"}</td>
                <td style="padding: 12px 15px;">{user_data['created_at']}</td>
            </tr>
            '''
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Управление пользователями</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }}
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .logo span {{ color: #ffd700; background: none; }}
        .container {{ max-width: 1200px; margin: 30px auto; padding: 0 30px; }}
        .table-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: rgba(102,126,234,0.1); color: #667eea; }}
        h1 {{ color: #667eea; margin-bottom: 20px; }}
        .back {{
            display: inline-block;
            margin-top: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
        }}
        .footer {{
            background: rgba(255,255,255,0.9);
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: #666;
        }}
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
                <tbody>{rows}</tbody>
            </table>
        </div>
        <a href="/" class="back">← На главную</a>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def add_form_page(self, token):
        html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Добавить специю</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .navbar { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 15px 30px; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; }
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo span { color: #ffd700; background: none; }
        .form-container { max-width: 500px; margin: 50px auto; background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; }
        h2 { color: #667eea; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; }
        button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border: none; border-radius: 25px; cursor: pointer; font-size: 16px; }
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
    <div class="form-container">
        <h2>➕ Добавление специи</h2>
        <form method="POST" action="/add">
            <div class="form-group"><label>Название</label><input type="text" name="name" required></div>
            <div class="form-group"><label>Цена (₽)</label><input type="number" step="0.01" name="price" required></div>
            <div class="form-group"><label>Поставщик</label><input type="text" name="supplier" required></div>
            <div class="form-group"><label>Количество (кг)</label><input type="number" name="stock" required></div>
            <button type="submit">💾 Сохранить</button>
        </form>
        <a href="/" class="back">← Назад</a>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def edit_form_page(self, token, spice_id):
        spice = None
        for s in self.db.get_all():
            if s['id'] == spice_id:
                spice = s
                break
        
        if not spice:
            return self.not_found()
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Редактировать - {spice['name']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .navbar {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 15px 30px; }}
        .nav-container {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .logo span {{ color: #ffd700; background: none; }}
        .form-container {{ max-width: 500px; margin: 50px auto; background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; }}
        h2 {{ color: #ed8936; margin-bottom: 30px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 8px; font-weight: 600; }}
        input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; }}
        button {{ background: #ed8936; color: white; padding: 12px 30px; border: none; border-radius: 25px; cursor: pointer; }}
        .back {{ display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }}
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
        <h2>✏️ Редактирование: {spice['name']}</h2>
        <form method="POST" action="/edit?id={spice_id}">
            <div class="form-group"><label>Название</label><input type="text" name="name" value="{spice['name']}" required></div>
            <div class="form-group"><label>Цена (₽)</label><input type="number" step="0.01" name="price" value="{spice['price']}" required></div>
            <div class="form-group"><label>Поставщик</label><input type="text" name="supplier" value="{spice['supplier']}" required></div>
            <div class="form-group"><label>Количество (кг)</label><input type="number" name="stock" value="{spice['stock']}" required></div>
            <button type="submit">💾 Обновить</button>
        </form>
        <a href="/" class="back">← Назад</a>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def add_spice(self, body):
        params = urllib.parse.parse_qs(body)
        new_id = max([s['id'] for s in self.db.get_all()]) + 1
        new_spice = {
            'id': new_id,
            'name': params.get('name', [''])[0],
            'price': float(params.get('price', ['0'])[0]),
            'supplier': params.get('supplier', [''])[0],
            'stock': int(params.get('stock', ['0'])[0]),
            'trend': 'stable'
        }
        self.db.spices.append(new_spice)
        return self.redirect('/')
    
    def update_spice(self, spice_id, body):
        params = urllib.parse.parse_qs(body)
        for s in self.db.get_all():
            if s['id'] == spice_id:
                s['name'] = params.get('name', [''])[0]
                s['price'] = float(params.get('price', ['0'])[0])
                s['supplier'] = params.get('supplier', [''])[0]
                s['stock'] = int(params.get('stock', ['0'])[0])
                break
        return self.redirect('/')
    
    def redirect(self, location):
        response = "HTTP/1.1 302 Found\r\n"
        response += "Location: " + location + "\r\n"
        response += "Content-Length: 0\r\n\r\n"
        return response.encode()
    
    def redirect_with_error(self, location, error):
        response = "HTTP/1.1 302 Found\r\n"
        response += "Location: " + location + "?error=" + urllib.parse.quote(error) + "\r\n"
        response += "Content-Length: 0\r\n\r\n"
        return response.encode()
    
    def http_response(self, code, content):
        response = f"HTTP/1.1 {code} OK\r\n"
        response += "Content-Type: text/html; charset=utf-8\r\n"
        response += f"Content-Length: {len(content.encode())}\r\n"
        response += "\r\n"
        response += content
        return response.encode()
    
    def not_found(self):
        return self.http_response(404, '<h1 style="text-align:center;margin-top:50px;">404 - Страница не найдена</h1><p style="text-align:center;"><a href="/">На главную</a></p>')
    
    def error_page(self, error):
        return self.http_response(500, f'<h1 style="text-align:center;margin-top:50px;">500 - Ошибка</h1><p style="text-align:center;">{error}</p><p style="text-align:center;"><a href="/">На главную</a></p>')
    
    def run(self):
        port = int(os.environ.get('PORT', 8080))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port))
        sock.listen(5)
        print('=' * 50)
        print('🌶️ SpiceDrugs Pro ЗАПУЩЕН!')
        print('=' * 50)
        print(f'🚀 Порт: {port}')
        print('👑 Администратор: admin / admin123')
        print('👤 Пользователь: user / user123')
        print('=' * 50)
        print('🔄 Нажмите Ctrl+C для остановки')
        
        while True:
            client, addr = sock.accept()
            data = client.recv(4096).decode()
            if data:
                response = self.handle(data)
                client.send(response)
            client.close()

if __name__ == '__main__':
    HTTPServer().run()
