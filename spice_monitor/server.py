import socket
import urllib.parse
import json
import hashlib
import secrets
import os
from database import SpiceDatabase
from datetime import datetime

class UserAuth:
    """Класс для управления пользователями"""
    
    def __init__(self, user_file='data/users.json'):
        self.user_file = user_file
        self.sessions = {}
        self.load_users()
    
    def load_users(self):
        if os.path.exists(self.user_file):
            with open(self.user_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
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
            self.save_users()
    
    def save_users(self):
        with open(self.user_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
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
        self.save_users()
        return True, "Регистрация успешна"
    
    def login(self, username, password):
        if username not in self.users:
            return None, "Неверное имя пользователя"
        
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if self.users[username]['password'] != hashed:
            return None, "Неверный пароль"
        
        token = secrets.token_hex(32)
        self.sessions[token] = username
        return token, "Вход выполнен"
    
    def logout(self, token):
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
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

class HTTPServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.db = SpiceDatabase()
        self.auth = UserAuth()
    
    def get_session_token(self, request_data):
        for line in request_data.split('\n'):
            if line.startswith('Cookie:'):
                cookie = line.split('Cookie:')[1].strip()
                for c in cookie.split(';'):
                    if 'session=' in c:
                        return c.split('session=')[1].strip()
        return None
    
    def handle_request(self, request_data):
        try:
            lines = request_data.split('\n')
            if not lines:
                return self.not_found()
            method, path, _ = lines[0].split(' ')
            
            token = self.get_session_token(request_data)
            is_auth = self.auth.check_auth(token)
            is_admin = self.auth.is_admin(token)
            
            if path in ['/', '/login', '/register'] and not is_auth:
                if path == '/':
                    return self.login_page()
                elif path == '/login':
                    if method == 'POST':
                        return self.do_login(request_data)
                    return self.login_page()
                elif path == '/register':
                    if method == 'POST':
                        return self.do_register(request_data)
                    return self.register_page()
            
            if not is_auth and path not in ['/', '/login', '/register', '/favicon.ico']:
                return self.redirect('/')
            
            if path == '/logout':
                if token:
                    self.auth.logout(token)
                return self.redirect('/')
            
            admin_only_paths = ['/add', '/edit', '/delete', '/monitor']
            if path in admin_only_paths and not is_admin:
                return self.access_denied_page()
            
            if '?' in path:
                path, query = path.split('?', 1)
                params = urllib.parse.parse_qs(query)
            else:
                params = {}
            
            if method == 'GET':
                if path == '/':
                    return self.index_page(token)
                elif path == '/add' and is_admin:
                    return self.add_form_page()
                elif path == '/edit' and is_admin:
                    spice_id = int(params.get('id', [0])[0])
                    return self.edit_form_page(spice_id)
                elif path == '/delete' and is_admin:
                    spice_id = int(params.get('id', [0])[0])
                    return self.delete_spice(spice_id)
                elif path == '/monitor' and is_admin:
                    self.db.update_prices_randomly()
                    return self.redirect_page('/')
                elif path == '/history':
                    spice_id = int(params.get('id', [0])[0])
                    return self.history_page(spice_id)
                elif path == '/analytics':
                    return self.analytics_page()
                elif path == '/export':
                    return self.export_data()
                elif path == '/users' and is_admin:
                    return self.users_page()
                elif path == '/delete_user' and is_admin:
                    username = params.get('username', [''])[0]
                    return self.delete_user(username)
            elif method == 'POST':
                body = request_data.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in request_data else ''
                if path == '/add' and is_admin:
                    return self.add_spice(body)
                elif path == '/edit' and is_admin:
                    spice_id = int(params.get('id', [0])[0])
                    return self.update_spice(spice_id, body)
            
            return self.not_found()
        except Exception as e:
            return self.error_page(str(e))
    
    def access_denied_page(self):
        html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Доступ запрещён</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 50px;
            border-radius: 20px;
            text-align: center;
            max-width: 500px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        .icon { font-size: 80px; margin-bottom: 20px; }
        h1 { color: #e53e3e; margin-bottom: 20px; }
        p { color: #666; margin-bottom: 30px; }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">⛔</div>
        <h1>Доступ запрещён</h1>
        <p>У вас недостаточно прав для выполнения этого действия.<br>Требуются права администратора.</p>
        <a href="/" class="btn">Вернуться на главную</a>
    </div>
</body>
</html>'''
        return self.http_response(403, html)
    
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
        window.onload = function() {
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
            <form method="POST" action="/register" onsubmit="return validateRegister()">
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
    </script>
</body>
</html>'''
        return self.http_response(200, html)
    
    def register_page(self):
        return self.login_page()
    
    def do_login(self, request_data):
        body = request_data.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in request_data else ''
        params = urllib.parse.parse_qs(body)
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        
        token, message = self.auth.login(username, password)
        if token:
            response = "HTTP/1.1 302 Found\r\n"
            response += "Location: /\r\n"
            response += "Set-Cookie: session=" + token + "; Path=/\r\n"
            response += "Content-Length: 0\r\n\r\n"
            return response.encode()
        else:
            return self.redirect_with_error('/', message)
    
    def do_register(self, request_data):
        body = request_data.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in request_data else ''
        params = urllib.parse.parse_qs(body)
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        name = params.get('name', [''])[0]
        
        success, message = self.auth.register(username, password, name)
        if success:
            return self.redirect_with_success('/', message)
        else:
            return self.redirect_with_error('/', message)
    
    def redirect_with_error(self, location, error):
        response = "HTTP/1.1 302 Found\r\n"
        response += "Location: " + location + "?error=" + urllib.parse.quote(error) + "\r\n"
        response += "Content-Length: 0\r\n\r\n"
        return response.encode()
    
    def redirect_with_success(self, location, success):
        response = "HTTP/1.1 302 Found\r\n"
        response += "Location: " + location + "?success=" + urllib.parse.quote(success) + "\r\n"
        response += "Content-Length: 0\r\n\r\n"
        return response.encode()
    
    def index_page(self, token):
        spices = self.db.get_all_spices()
        stats = self.db.get_statistics()
        user = self.auth.get_user(token)
        username = user.get('name', 'Пользователь') if user else 'Гость'
        is_admin = self.auth.is_admin(token)
        
        rows = ''
        for s in spices:
            price_class = ''
            if s['current_price'] > stats.get('avg_price', 0) * 1.2:
                price_class = 'style="color:#e53e3e; font-weight:bold"'
            elif s['current_price'] < stats.get('avg_price', 0) * 0.8:
                price_class = 'style="color:#48bb78; font-weight:bold"'
            
            stock_class = ''
            stock_text = str(s['in_stock']) + ' кг'
            if s['in_stock'] == 0:
                stock_class = 'class="stock-badge stock-out"'
                stock_text = 'НЕТ В НАЛИЧИИ'
            elif s['in_stock'] < 50:
                stock_class = 'class="stock-badge stock-low"'
                stock_text = str(s['in_stock']) + ' кг (МАЛО)'
            else:
                stock_class = 'class="stock-badge stock-normal"'
            
            trend = ''
            if len(s['price_history']) > 1:
                old = s['price_history'][-2]['price']
                if s['current_price'] > old:
                    trend = '📈 +' + str(round(s['current_price'] - old, 2))
                elif s['current_price'] < old:
                    trend = '📉 ' + str(round(s['current_price'] - old, 2))
            
            action_buttons = '<a href="/history?id=' + str(s['id']) + '" class="btn-small btn-info">📊 История</a>'
            if is_admin:
                action_buttons += '<a href="/edit?id=' + str(s['id']) + '" class="btn-small btn-warning">✏️</a>'
                action_buttons += '<a href="/delete?id=' + str(s['id']) + '" class="btn-small btn-danger" onclick="return confirm(\'Удалить ' + s['name'] + '?\')">🗑️</a>'
            
            rows += '<tr>'
            rows += '<td style="padding: 15px 18px; border-bottom: 1px solid #f0f0f0;">' + str(s['id']) + '</td>'
            rows += '<td style="padding: 15px 18px; border-bottom: 1px solid #f0f0f0;"><strong>' + s['name'] + '</strong></td>'
            rows += '<td style="padding: 15px 18px; border-bottom: 1px solid #f0f0f0;">' + s['supplier'] + '</td>'
            rows += '<td style="padding: 15px 18px; border-bottom: 1px solid #f0f0f0;" ' + price_class + '>' + str(s['current_price']) + ' ₽<br><small>' + trend + '</small></td>'
            rows += '<td style="padding: 15px 18px; border-bottom: 1px solid #f0f0f0;"><span ' + stock_class + '>' + stock_text + '</span></td>'
            rows += '<td style="padding: 15px 18px; border-bottom: 1px solid #f0f0f0;" class="actions">' + action_buttons + '</td>'
            rows += '</tr>'
        
        admin_buttons = ''
        if is_admin:
            admin_buttons = '''
                <div class="admin-buttons">
                    <a href="/add" class="btn-primary">➕ Добавить специю</a>
                    <a href="/monitor" class="btn-primary">🔄 Мониторинг цен</a>
                    <a href="/users" class="btn-primary">👥 Управление пользователями</a>
                </div>
            '''
        
        role_badge = '<span class="role-badge admin">👑 Администратор</span>' if is_admin else '<span class="role-badge user">👤 Пользователь</span>'
        role_message = '🔑 У вас есть права администратора. Вы можете управлять ассортиментом.' if is_admin else '👁️ Вы в режиме просмотра.'
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpiceDrugs Pro - Мониторинг специй</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: 'Segoe UI', 'Roboto', sans-serif; 
            min-height: 100vh;
            position: relative;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        body::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><circle cx="100" cy="100" r="80" fill="rgba(255,255,255,0.05)"/><circle cx="900" cy="150" r="120" fill="rgba(255,255,255,0.03)"/><circle cx="200" cy="800" r="100" fill="rgba(255,255,255,0.04)"/><circle cx="850" cy="850" r="90" fill="rgba(255,255,255,0.05)"/><circle cx="500" cy="500" r="200" fill="rgba(255,255,255,0.02)"/></svg>');
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
            pointer-events: none;
            z-index: 0;
        }}
        
        body::after {{
            content: "🌶️🍃🌿🌶️🍃🌿🌶️🍃🌿🌶️🍃🌿";
            position: fixed;
            left: 10px;
            top: 50%;
            transform: translateY(-50%) rotate(-90deg);
            font-size: 40px;
            opacity: 0.15;
            white-space: nowrap;
            pointer-events: none;
            z-index: 0;
            animation: floatLeft 10s ease-in-out infinite;
        }}
        
        @keyframes floatLeft {{
            0%, 100% {{ transform: translateY(-50%) rotate(-90deg) translateX(0); }}
            50% {{ transform: translateY(-50%) rotate(-90deg) translateX(10px); }}
        }}
        
        .right-decoration {{
            position: fixed;
            right: 10px;
            top: 50%;
            transform: translateY(-50%) rotate(90deg);
            font-size: 40px;
            opacity: 0.15;
            white-space: nowrap;
            pointer-events: none;
            z-index: 0;
            animation: floatRight 10s ease-in-out infinite;
        }}
        
        @keyframes floatRight {{
            0%, 100% {{ transform: translateY(-50%) rotate(90deg) translateX(0); }}
            50% {{ transform: translateY(-50%) rotate(90deg) translateX(-10px); }}
        }}
        
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            color: #333;
            padding: 0 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid rgba(102,126,234,0.2);
        }}
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            flex-wrap: wrap;
        }}
        .logo {{
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
        }}
        .logo span {{ color: #ffd700; background: none; -webkit-background-clip: unset; background-clip: unset; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .nav-links {{ display: flex; flex-wrap: wrap; align-items: center; gap: 5px; }}
        .nav-links a {{
            color: #333;
            text-decoration: none;
            padding: 8px 18px;
            border-radius: 25px;
            transition: all 0.3s;
            font-weight: 600;
        }}
        .nav-links a:hover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; transform: translateY(-2px); }}
        .user-info {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-left: 15px;
            padding: 8px 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 30px;
            color: white;
            font-weight: 600;
        }}
        .role-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
        .role-badge.admin {{ background: #ffd700; color: #667eea; }}
        .role-badge.user {{ background: rgba(255,255,255,0.3); color: white; }}
        
        .container {{ max-width: 1400px; margin: 30px auto; padding: 0 30px; position: relative; z-index: 1; }}
        
        .welcome {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 25px 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(102,126,234,0.2);
        }}
        .welcome h2 {{ color: #667eea; margin-bottom: 8px; font-size: 24px; font-weight: 700; }}
        .role-info {{ color: #555; font-size: 14px; margin-top: 8px; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, rgba(102,126,234,0.95) 0%, rgba(118,75,162,0.95) 100%);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            transition: all 0.3s;
            border: 1px solid rgba(255,255,255,0.3);
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            color: white;
        }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }}
        .stat-card h4 {{ color: rgba(255,255,255,0.9); font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; font-weight: 700; }}
        .stat-card .value {{ font-size: 32px; font-weight: bold; color: white; }}
        
        .table-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
            box-shadow: 0 5px 25px rgba(0,0,0,0.1);
            border: 1px solid rgba(102,126,234,0.2);
        }}
        table {{ width: 100%; border-collapse: collapse; min-width: 800px; }}
        th {{ padding: 15px 18px; text-align: left; background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; font-size: 14px; border-bottom: 2px solid rgba(102,126,234,0.2); }}
        td {{ padding: 15px 18px; text-align: left; border-bottom: 1px solid #f0f0f0; color: #333; font-weight: 500; }}
        tr:hover {{ background: rgba(102,126,234,0.05); transition: 0.2s; }}
        
        .stock-badge {{ display: inline-block; padding: 5px 14px; border-radius: 25px; font-size: 12px; font-weight: 600; }}
        .stock-normal {{ background: linear-gradient(135deg, #48bb78, #38a169); color: white; }}
        .stock-low {{ background: linear-gradient(135deg, #ed8936, #dd6b20); color: white; }}
        .stock-out {{ background: linear-gradient(135deg, #e53e3e, #c53030); color: white; }}
        
        .btn-primary {{
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
            box-shadow: 0 2px 5px rgba(102,126,234,0.3);
        }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.5); }}
        
        .btn-small {{ padding: 5px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; margin: 0 3px; display: inline-block; transition: all 0.2s; font-weight: 600; }}
        .btn-info {{ background: #4299e1; color: white; }}
        .btn-warning {{ background: #ed8936; color: white; }}
        .btn-danger {{ background: #e53e3e; color: white; }}
        .btn-small:hover {{ transform: translateY(-1px); opacity: 0.9; }}
        
        .actions {{ white-space: nowrap; }}
        
        .footer {{
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
            color: #333;
            text-align: center;
            padding: 25px;
            margin-top: 50px;
            border-top: 1px solid rgba(102,126,234,0.2);
            font-weight: 500;
        }}
        
        .admin-buttons {{
            display: flex;
            gap: 12px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }}
        
        .header-actions {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .header-actions h2 {{ color: #667eea; font-weight: 700; }}
        
        @media (max-width: 768px) {{
            .nav-container {{ flex-direction: column; gap: 10px; }}
            .stats-grid {{ gap: 15px; }}
            th, td {{ padding: 10px 12px; }}
        }}
    </style>
</head>
<body>
    <div class="right-decoration">🌿🍃🌶️🌿🍃🌶️🌿🍃🌶️</div>
    
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/export">📥 Экспорт</a>
                {('<a href="/users">👥 Пользователи</a>' if is_admin else '')}
                <span class="user-info">👋 {username} {role_badge}</span>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="welcome">
            <h2>🍃 Добро пожаловать, {username}!</h2>
            <p>Сегодня {datetime.now().strftime('%d %B %Y года')}</p>
            <div class="role-info">{role_message}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card"><h4>🌶️ Всего позиций</h4><div class="value">{stats.get('total_items', 0)}</div></div>
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{stats.get('avg_price', 0)} ₽</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{stats.get('min_price', 0)} / {stats.get('max_price', 0)} ₽</div></div>
            <div class="stat-card"><h4>📦 Общий запас</h4><div class="value">{stats.get('total_stock', 0)} кг</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{stats.get('total_value', 0)} ₽</div></div>
        </div>
        
        <div class="header-actions">
            <h2>📋 Наш ассортимент специй</h2>
            {admin_buttons}
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Наименование</th>
                        <th>Поставщик</th>
                        <th>Цена</th>
                        <th>Остаток</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
        <p style="font-size: 12px; margin-top: 8px; opacity: 0.8;">© 2024 Все права защищены</p>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def analytics_page(self):
        spices = self.db.get_all_spices()
        stats = self.db.get_statistics()
        
        spice_options = ''
        for s in spices:
            spice_options += f'<option value="{s["id"]}">{s["name"]}</option>'
        
        import json as json_module
        spices_json = []
        for s in spices:
            spices_json.append({
                'id': s['id'],
                'name': s['name'],
                'history': [h['price'] for h in s['price_history']],
                'dates': [h['date'] for h in s['price_history']]
            })
        spices_data = json_module.dumps(spices_json)
        
        spices_table = ''
        for s in spices:
            week_history = self.db.get_price_history_for_period(s['id'], 'week')
            month_history = self.db.get_price_history_for_period(s['id'], 'month')
            year_history = self.db.get_price_history_for_period(s['id'], 'year')
            
            week_change = 0
            week_percent = 0
            if len(week_history[1]) >= 2:
                week_change = week_history[1][-1] - week_history[1][0]
                week_percent = (week_change / week_history[1][0]) * 100 if week_history[1][0] != 0 else 0
            
            month_change = 0
            month_percent = 0
            if len(month_history[1]) >= 2:
                month_change = month_history[1][-1] - month_history[1][0]
                month_percent = (month_change / month_history[1][0]) * 100 if month_history[1][0] != 0 else 0
            
            year_change = 0
            year_percent = 0
            if len(year_history[1]) >= 2:
                year_change = year_history[1][-1] - year_history[1][0]
                year_percent = (year_change / year_history[1][0]) * 100 if year_history[1][0] != 0 else 0
            
            week_color = '#e53e3e' if week_change > 0 else '#48bb78' if week_change < 0 else '#666'
            week_symbol = '▲' if week_change > 0 else '▼' if week_change < 0 else '●'
            month_color = '#e53e3e' if month_change > 0 else '#48bb78' if month_change < 0 else '#666'
            month_symbol = '▲' if month_change > 0 else '▼' if month_change < 0 else '●'
            year_color = '#e53e3e' if year_change > 0 else '#48bb78' if year_change < 0 else '#666'
            year_symbol = '▲' if year_change > 0 else '▼' if year_change < 0 else '●'
            
            spices_table += f'''
            <tr>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;"><strong style="color:#667eea;">{s['name']}</strong></td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;"><span style="color:#667eea; font-weight:bold;">{s['current_price']:.2f} ₽</span></td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0; color: {week_color}; font-weight: bold;">
                    {week_symbol} {abs(week_change):.2f} ₽<br><small>({abs(week_percent):.1f}%)</small>
                </td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0; color: {month_color}; font-weight: bold;">
                    {month_symbol} {abs(month_change):.2f} ₽<br><small>({abs(month_percent):.1f}%)</small>
                </td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0; color: {year_color}; font-weight: bold;">
                    {year_symbol} {abs(year_change):.2f} ₽<br><small>({abs(year_percent):.1f}%)</small>
                </td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;"><canvas id="mini-{s['id']}" width="120" height="30" style="width:120px;height:30px"></canvas></td>
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
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        body::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><circle cx="100" cy="100" r="80" fill="rgba(255,255,255,0.05)"/><circle cx="900" cy="150" r="120" fill="rgba(255,255,255,0.03)"/><circle cx="200" cy="800" r="100" fill="rgba(255,255,255,0.04)"/><circle cx="850" cy="850" r="90" fill="rgba(255,255,255,0.05)"/></svg>');
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
            pointer-events: none;
            z-index: 0;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: relative;
            z-index: 1;
        }}
        .nav-container {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .logo span {{ color: #ffd700; background: none; -webkit-background-clip: unset; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .nav-links a {{ color: #333; text-decoration: none; margin-left: 25px; padding: 8px 16px; border-radius: 25px; transition: 0.3s; font-weight: 600; }}
        .nav-links a:hover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .container {{ max-width: 1400px; margin: 30px auto; padding: 0 30px; position: relative; z-index: 1; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, rgba(102,126,234,0.95) 0%, rgba(118,75,162,0.95) 100%);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            transition: 0.3s;
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-card h4 {{ color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 12px; font-weight: 700; }}
        .stat-card .value {{ font-size: 28px; font-weight: bold; color: white; }}
        
        .tabs {{ display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }}
        .tab-btn {{
            padding: 12px 28px;
            background: rgba(255,255,255,0.95);
            border: none;
            border-radius: 40px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 700;
            transition: 0.3s;
            color: #333;
        }}
        .tab-btn.active {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        
        .tab-pane {{ display: none; }}
        .tab-pane.active {{ display: block; }}
        
        .table-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow-x: auto;
            border: 1px solid rgba(102,126,234,0.2);
        }}
        table {{ width: 100%; border-collapse: collapse; min-width: 800px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
        th {{ background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; }}
        tr:hover {{ background: rgba(102,126,234,0.05); }}
        td {{ color: #333; font-weight: 500; }}
        
        .detail-chart {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(102,126,234,0.2);
        }}
        .selector {{ display: flex; gap: 20px; align-items: flex-end; flex-wrap: wrap; margin-bottom: 30px; }}
        .selector-group {{ flex: 1; min-width: 200px; }}
        .selector-group label {{ display: block; margin-bottom: 8px; font-weight: 700; color: #667eea; }}
        .selector-group select, .selector-group input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            transition: 0.3s;
            font-weight: 500;
        }}
        .selector-group select:focus {{ outline: none; border-color: #667eea; }}
        .btn-submit {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 28px;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            transition: 0.3s;
            font-weight: 700;
        }}
        .btn-submit:hover {{ transform: translateY(-2px); }}
        .period-buttons {{ display: flex; gap: 12px; margin: 20px 0; flex-wrap: wrap; }}
        .period-btn {{
            padding: 8px 22px;
            background: #e0e0e0;
            color: #333;
            border-radius: 30px;
            cursor: pointer;
            transition: 0.3s;
            border: none;
            font-weight: 600;
        }}
        .period-btn.active {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .chart-container {{ text-align: center; margin-top: 20px; }}
        .detail-stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 25px;
        }}
        .detail-stat {{
            background: rgba(102,126,234,0.1);
            padding: 15px;
            border-radius: 15px;
            text-align: center;
        }}
        .detail-stat .label {{ font-size: 12px; color: #666; font-weight: 600; }}
        .detail-stat .number {{ font-size: 20px; font-weight: bold; color: #667eea; }}
        .footer {{
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
            color: #333;
            text-align: center;
            padding: 25px;
            margin-top: 50px;
            font-weight: 500;
        }}
        canvas {{ background: #f8f9ff; border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/export">📥 Экспорт</a>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card"><h4>🌶️ Всего специй</h4><div class="value">{stats.get('total_items', 0)}</div></div>
            <div class="stat-card"><h4>💰 Средняя цена</h4><div class="value">{stats.get('avg_price', 0)} ₽</div></div>
            <div class="stat-card"><h4>📊 Мин / Макс</h4><div class="value">{stats.get('min_price', 0)} / {stats.get('max_price', 0)} ₽</div></div>
            <div class="stat-card"><h4>💎 Общая стоимость</h4><div class="value">{stats.get('total_value', 0)} ₽</div></div>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('all')">📋 Все специи</button>
            <button class="tab-btn" onclick="showTab('detail')">📈 Детальный анализ</button>
        </div>
        
        <div id="tab-all" class="tab-pane active">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th style="padding: 12px 15px;">Специя</th>
                            <th style="padding: 12px 15px;">Цена</th>
                            <th style="padding: 12px 15px;">За неделю</th>
                            <th style="padding: 12px 15px;">За месяц</th>
                            <th style="padding: 12px 15px;">За год</th>
                            <th style="padding: 12px 15px;">Тренд (30 дней)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {spices_table}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="tab-detail" class="tab-pane">
            <div class="detail-chart">
                <h2 style="color: #667eea; margin-bottom: 25px; font-weight: 700;">📈 Детальный график цен</h2>
                <div class="selector">
                    <div class="selector-group">
                        <label>Выберите специю:</label>
                        <select id="detail-spice">{spice_options}</select>
                    </div>
                    <div class="selector-group">
                        <label>&nbsp;</label>
                        <button class="btn-submit" onclick="updateChart()">Показать график</button>
                    </div>
                </div>
                <div class="period-buttons">
                    <button class="period-btn" onclick="setPeriod('week')">📅 Неделя</button>
                    <button class="period-btn active" onclick="setPeriod('month')">📆 Месяц</button>
                    <button class="period-btn" onclick="setPeriod('year')">📊 Год</button>
                </div>
                <div class="chart-container">
                    <canvas id="detail-canvas" width="800" height="400" style="width:100%; max-width:800px; height:auto; background:#f8f9ff; border-radius:15px;"></canvas>
                </div>
                <div class="detail-stats" id="detail-stats"></div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
    </div>
    
    <script>
        const spicesData = {spices_data};
        let currentPeriod = 'month';
        let currentSpice = spicesData[0];
        
        function drawMiniChart(canvasId, values) {{
            const canvas = document.getElementById(canvasId);
            if (!canvas || !values || values.length < 2) return;
            const ctx = canvas.getContext('2d');
            const w = canvas.width, h = canvas.height;
            ctx.clearRect(0, 0, w, h);
            const minVal = Math.min(...values);
            const maxVal = Math.max(...values);
            const range = maxVal - minVal || 1;
            const stepX = w / (values.length - 1);
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2;
            for (let i = 0; i < values.length; i++) {{
                const x = i * stepX;
                const y = h - ((values[i] - minVal) / range) * h;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }}
            ctx.stroke();
        }}
        
        function getHistoryForPeriod(spiceId, period) {{
            const spice = spicesData.find(s => s.id == spiceId);
            if (!spice) return {{ dates: [], prices: [] }};
            const now = new Date();
            let daysBack = period === 'week' ? 7 : (period === 'month' ? 30 : 365);
            const cutoff = new Date();
            cutoff.setDate(now.getDate() - daysBack);
            const filtered = [];
            for (let i = 0; i < spice.dates.length; i++) {{
                const date = new Date(spice.dates[i]);
                if (date >= cutoff) filtered.push({{ date: spice.dates[i], price: spice.history[i] }});
            }}
            return {{ dates: filtered.map(f => f.date), prices: filtered.map(f => f.price) }};
        }}
        
        function drawDetailChart() {{
            const canvas = document.getElementById('detail-canvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const w = canvas.width, h = canvas.height;
            const history = getHistoryForPeriod(currentSpice.id, currentPeriod);
            const prices = history.prices;
            const dates = history.dates;
            if (prices.length < 2) {{
                ctx.fillStyle = '#999';
                ctx.fillText('Недостаточно данных', w/2-50, h/2);
                return;
            }}
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const range = maxPrice - minPrice || 1;
            const avgPrice = prices.reduce((a,b) => a + b, 0) / prices.length;
            const startPrice = prices[0];
            const currentPrice = prices[prices.length-1];
            const change = currentPrice - startPrice;
            const changePercent = (change / startPrice) * 100;
            document.getElementById('detail-stats').innerHTML = `
                <div class="detail-stat"><div class="label">📉 Минимум</div><div class="number">${{minPrice.toFixed(2)}} ₽</div></div>
                <div class="detail-stat"><div class="label">📈 Максимум</div><div class="number">${{maxPrice.toFixed(2)}} ₽</div></div>
                <div class="detail-stat"><div class="label">📊 Средняя</div><div class="number">${{avgPrice.toFixed(2)}} ₽</div></div>
                <div class="detail-stat"><div class="label">🔄 Изменение</div><div class="number" style="color: ${{change > 0 ? '#e53e3e' : change < 0 ? '#48bb78' : '#666'}}">${{change > 0 ? '▲' : change < 0 ? '▼' : '●'}} ${{Math.abs(change).toFixed(2)}} ₽ (${{Math.abs(changePercent).toFixed(1)}}%)</div></div>
            `;
            ctx.clearRect(0, 0, w, h);
            for (let i = 0; i <= 4; i++) {{
                const y = h - (i / 4) * h;
                ctx.beginPath();
                ctx.strokeStyle = '#ddd';
                ctx.moveTo(40, y);
                ctx.lineTo(w - 20, y);
                ctx.stroke();
                ctx.fillStyle = '#999';
                ctx.font = '10px Arial';
                ctx.fillText(`${{(minPrice + (i / 4) * range).toFixed(0)}} ₽`, 5, y + 3);
            }}
            const stepX = (w - 60) / (prices.length - 1);
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2.5;
            for (let i = 0; i < prices.length; i++) {{
                const x = 40 + i * stepX;
                const y = h - ((prices[i] - minPrice) / range) * (h - 40) - 20;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }}
            ctx.stroke();
            ctx.lineTo(40 + (prices.length - 1) * stepX, h - 20);
            ctx.lineTo(40, h - 20);
            ctx.fillStyle = 'rgba(102,126,234,0.1)';
            ctx.fill();
            for (let i = 0; i < prices.length; i++) {{
                const x = 40 + i * stepX;
                const y = h - ((prices[i] - minPrice) / range) * (h - 40) - 20;
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffd700';
                ctx.fill();
                ctx.strokeStyle = '#667eea';
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }}
            const minY = h - ((minPrice - minPrice) / range) * (h - 40) - 20;
            const maxY = h - ((maxPrice - minPrice) / range) * (h - 40) - 20;
            const avgY = h - ((avgPrice - minPrice) / range) * (h - 40) - 20;
            ctx.beginPath(); ctx.strokeStyle = '#48bb78'; ctx.setLineDash([5,5]);
            ctx.moveTo(40, minY); ctx.lineTo(w - 20, minY); ctx.stroke();
            ctx.beginPath(); ctx.strokeStyle = '#e53e3e';
            ctx.moveTo(40, maxY); ctx.lineTo(w - 20, maxY); ctx.stroke();
            ctx.beginPath(); ctx.strokeStyle = '#ffd700';
            ctx.moveTo(40, avgY); ctx.lineTo(w - 20, avgY); ctx.stroke();
            ctx.setLineDash([]);
        }}
        
        function updateChart() {{
            const spiceId = parseInt(document.getElementById('detail-spice').value);
            currentSpice = spicesData.find(s => s.id == spiceId);
            drawDetailChart();
        }}
        
        function setPeriod(period) {{
            currentPeriod = period;
            document.querySelectorAll('#tab-detail .period-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            drawDetailChart();
        }}
        
        function showTab(tab) {{
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            if (tab === 'all') {{
                document.getElementById('tab-all').classList.add('active');
                document.querySelector('.tab-btn:first-child').classList.add('active');
            }} else {{
                document.getElementById('tab-detail').classList.add('active');
                document.querySelector('.tab-btn:last-child').classList.add('active');
                drawDetailChart();
            }}
        }}
        
        window.onload = function() {{
            for (let i = 0; i < spicesData.length; i++) {{
                const values = spicesData[i].history.slice(-30);
                drawMiniChart(`mini-${{spicesData[i].id}}`, values);
            }}
            currentSpice = spicesData[0];
            drawDetailChart();
        }};
    </script>
</body>
</html>'''
        return self.http_response(200, html)
    
    def add_form_page(self):
        html = '''<!DOCTYPE html>
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
        .logo { font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .logo span { color: #ffd700; background: none; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .nav-links a { color: #333; text-decoration: none; margin-left: 25px; padding: 8px 16px; border-radius: 25px; font-weight: 600; }
        .nav-links a:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .form-container { max-width: 600px; margin: 50px auto; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 40px; border-radius: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
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
            <div class="nav-links"><a href="/">🏠 Главная</a><a href="/logout">🚪 Выйти</a></div>
        </div>
    </div>
    <div class="form-container">
        <h2>➕ Добавление новой специи</h2>
        <form method="POST" action="/add">
            <div class="form-group"><label>🌿 Название специи</label><input type="text" name="name" required placeholder="Например: Шафран"></div>
            <div class="form-group"><label>💰 Цена (₽ за кг)</label><input type="number" step="0.01" name="price" required placeholder="0.00"></div>
            <div class="form-group"><label>🏭 Поставщик</label><input type="text" name="supplier" required placeholder="ООО Поставщик"></div>
            <div class="form-group"><label>📦 Количество на складе (кг)</label><input type="number" name="stock" required placeholder="0"></div>
            <button type="submit">💾 Сохранить</button>
        </form>
        <a href="/" class="back">← Вернуться на главную</a>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def edit_form_page(self, spice_id):
        spice = self.db.get_spice_by_id(spice_id)
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
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
        }}
        .nav-container {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .logo span {{ color: #ffd700; background: none; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .nav-links a {{ color: #333; text-decoration: none; margin-left: 25px; padding: 8px 16px; border-radius: 25px; font-weight: 600; }}
        .nav-links a:hover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .form-container {{ max-width: 600px; margin: 50px auto; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 40px; border-radius: 25px; }}
        h2 {{ color: #ed8936; margin-bottom: 30px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 8px; font-weight: 600; color: #333; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 12px; }}
        button {{ background: #ed8936; color: white; padding: 12px 30px; border: none; border-radius: 30px; cursor: pointer; font-size: 16px; font-weight: 600; }}
        .back {{ display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links"><a href="/">🏠 Главная</a><a href="/logout">🚪 Выйти</a></div>
        </div>
    </div>
    <div class="form-container">
        <h2>✏️ Редактирование: {spice['name']}</h2>
        <form method="POST" action="/edit?id={spice_id}">
            <div class="form-group"><label>🌿 Название</label><input type="text" name="name" value="{spice['name']}" required></div>
            <div class="form-group"><label>💰 Цена (₽)</label><input type="number" step="0.01" name="price" value="{spice['current_price']}" required></div>
            <div class="form-group"><label>🏭 Поставщик</label><input type="text" name="supplier" value="{spice['supplier']}" required></div>
            <div class="form-group"><label>📦 Количество (кг)</label><input type="number" name="stock" value="{spice['in_stock']}" required></div>
            <button type="submit">💾 Обновить</button>
        </form>
        <a href="/" class="back">← Назад</a>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def history_page(self, spice_id):
        spice = self.db.get_spice_by_id(spice_id)
        if not spice:
            return self.not_found()
        
        week_history = self.db.get_price_history_for_period(spice_id, 'week')
        month_history = self.db.get_price_history_for_period(spice_id, 'month')
        year_history = self.db.get_price_history_for_period(spice_id, 'year')
        
        week_change = 0
        week_percent = 0
        if len(week_history[1]) >= 2:
            week_change = week_history[1][-1] - week_history[1][0]
            week_percent = (week_change / week_history[1][0]) * 100 if week_history[1][0] != 0 else 0
        
        month_change = 0
        month_percent = 0
        if len(month_history[1]) >= 2:
            month_change = month_history[1][-1] - month_history[1][0]
            month_percent = (month_change / month_history[1][0]) * 100 if month_history[1][0] != 0 else 0
        
        year_change = 0
        year_percent = 0
        if len(year_history[1]) >= 2:
            year_change = year_history[1][-1] - year_history[1][0]
            year_percent = (year_change / year_history[1][0]) * 100 if year_history[1][0] != 0 else 0
        
        prices_trend = [h['price'] for h in spice['price_history'][-30:]]
        trend = "стабильна"
        trend_icon = "➖"
        if len(prices_trend) > 5:
            first_avg = sum(prices_trend[:5]) / 5
            last_avg = sum(prices_trend[-5:]) / 5
            if last_avg > first_avg * 1.05:
                trend = "растёт"
                trend_icon = "📈"
            elif last_avg < first_avg * 0.95:
                trend = "падает"
                trend_icon = "📉"
        
        history_rows = ''
        for record in spice['price_history'][-30:]:
            date_obj = datetime.strptime(record['date'], '%Y-%m-%d')
            date_formatted = date_obj.strftime('%d.%m.%Y')
            history_rows += f'''
            <div class="history-item">
                <div class="history-date">📅 {date_formatted}</div>
                <div class="history-price">{record['price']} ₽</div>
            </div>
            '''
        
        all_prices = [h['price'] for h in spice['price_history']]
        min_price = min(all_prices)
        max_price = max(all_prices)
        avg_price = sum(all_prices) / len(all_prices)
        price_range = max_price - min_price
        
        min_price_date = next((h['date'] for h in spice['price_history'] if h['price'] == min_price), None)
        max_price_date = next((h['date'] for h in spice['price_history'] if h['price'] == max_price), None)
        
        if min_price_date:
            min_price_date = datetime.strptime(min_price_date, '%Y-%m-%d').strftime('%d.%m.%Y')
        if max_price_date:
            max_price_date = datetime.strptime(max_price_date, '%Y-%m-%d').strftime('%d.%m.%Y')
        
        chart_prices = [h['price'] for h in spice['price_history'][-90:]]
        
        import json as json_module
        chart_prices_json = json_module.dumps(chart_prices)
        
        html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>История цен - {spice['name']} | SpiceDrugs Pro</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', 'Roboto', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        body::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><circle cx="100" cy="100" r="80" fill="rgba(255,255,255,0.05)"/><circle cx="900" cy="150" r="120" fill="rgba(255,255,255,0.03)"/><circle cx="200" cy="800" r="100" fill="rgba(255,255,255,0.04)"/><circle cx="850" cy="850" r="90" fill="rgba(255,255,255,0.05)"/></svg>');
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
            pointer-events: none;
            z-index: 0;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: relative;
            z-index: 1;
        }}
        .nav-container {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .logo span {{ color: #ffd700; background: none; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .nav-links a {{ color: #333; text-decoration: none; margin-left: 25px; padding: 8px 18px; border-radius: 25px; transition: all 0.3s; font-weight: 600; }}
        .nav-links a:hover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        
        .container {{ max-width: 1200px; margin: 30px auto; padding: 0 30px; position: relative; z-index: 1; }}
        
        .breadcrumb {{ margin-bottom: 25px; color: #666; }}
        .breadcrumb a {{ color: #667eea; text-decoration: none; font-weight: 600; }}
        
        .spice-header {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 25px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        .spice-name {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .supplier {{ color: #555; margin-bottom: 20px; font-size: 14px; font-weight: 500; }}
        
        .current-price-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 25px;
            color: white;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .current-price-info {{ flex: 1; }}
        .current-price-label {{ font-size: 14px; opacity: 0.9; margin-bottom: 8px; }}
        .current-price-value {{ font-size: 48px; font-weight: bold; }}
        .trend-badge {{ background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 40px; display: inline-block; font-size: 14px; }}
        
        .period-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .period-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
        }}
        .period-card:hover {{ transform: translateY(-5px); background: white; }}
        .period-title {{ font-size: 14px; color: #666; margin-bottom: 10px; font-weight: 600; }}
        .period-change {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
        .period-percent {{ font-size: 12px; }}
        .positive {{ color: #e53e3e; }}
        .negative {{ color: #48bb78; }}
        .neutral {{ color: #666; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-3px); background: white; }}
        .stat-icon {{ font-size: 28px; margin-bottom: 10px; }}
        .stat-label {{ font-size: 12px; color: #666; margin-bottom: 8px; font-weight: 600; }}
        .stat-value {{ font-size: 22px; font-weight: bold; color: #667eea; }}
        .stat-date {{ font-size: 11px; color: #999; margin-top: 5px; }}
        
        .chart-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .chart-title {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        canvas {{
            width: 100%;
            height: auto;
            background: #f8f9ff;
            border-radius: 15px;
        }}
        
        .history-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
        }}
        .history-title {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .history-list {{
            max-height: 400px;
            overflow-y: auto;
            border-radius: 15px;
        }}
        .history-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
            transition: all 0.2s;
        }}
        .history-item:hover {{ background: rgba(102,126,234,0.05); transform: translateX(5px); }}
        .history-date {{ font-weight: 500; color: #333; }}
        .history-price {{ font-size: 18px; font-weight: bold; color: #667eea; }}
        
        .action-buttons {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 12px 28px;
            border-radius: 40px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .btn-secondary {{ background: white; color: #667eea; border: 2px solid #667eea; }}
        .btn:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }}
        
        .footer {{
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(10px);
            color: #333;
            text-align: center;
            padding: 25px;
            margin-top: 50px;
            font-weight: 500;
        }}
        
        @media (max-width: 768px) {{
            .period-stats {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .current-price-value {{ font-size: 32px; }}
        }}
        
        .history-list::-webkit-scrollbar {{ width: 8px; }}
        .history-list::-webkit-scrollbar-track {{ background: #f0f0f0; border-radius: 10px; }}
        .history-list::-webkit-scrollbar-thumb {{ background: #667eea; border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/export">📥 Экспорт</a>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="breadcrumb">
            <a href="/">🏠 Главная</a> / 📊 История цен
        </div>
        
        <div class="spice-header">
            <div class="spice-name">
                🌶️ {spice['name']}
                <span class="trend-badge">{trend_icon} Тренд: {trend}</span>
            </div>
            <div class="supplier">🏭 Поставщик: {spice['supplier']} | 📦 Остаток: {spice['in_stock']} кг</div>
        </div>
        
        <div class="current-price-card">
            <div class="current-price-info">
                <div class="current-price-label">💰 Текущая цена</div>
                <div class="current-price-value">{spice['current_price']} ₽ / кг</div>
            </div>
            <div class="current-price-info">
                <div class="current-price-label">📊 Всего записей в истории</div>
                <div class="current-price-value">{len(spice['price_history'])}</div>
            </div>
        </div>
        
        <div class="period-stats">
            <div class="period-card">
                <div class="period-title">📅 За последнюю неделю</div>
                <div class="period-change {'positive' if week_change > 0 else 'negative' if week_change < 0 else 'neutral'}">
                    {'▲' if week_change > 0 else '▼' if week_change < 0 else '●'} {abs(week_change):.2f} ₽
                </div>
                <div class="period-percent {'positive' if week_percent > 0 else 'negative' if week_percent < 0 else 'neutral'}">
                    {abs(week_percent):.1f}%
                </div>
            </div>
            <div class="period-card">
                <div class="period-title">📆 За последний месяц</div>
                <div class="period-change {'positive' if month_change > 0 else 'negative' if month_change < 0 else 'neutral'}">
                    {'▲' if month_change > 0 else '▼' if month_change < 0 else '●'} {abs(month_change):.2f} ₽
                </div>
                <div class="period-percent {'positive' if month_percent > 0 else 'negative' if month_percent < 0 else 'neutral'}">
                    {abs(month_percent):.1f}%
                </div>
            </div>
            <div class="period-card">
                <div class="period-title">📊 За последний год</div>
                <div class="period-change {'positive' if year_change > 0 else 'negative' if year_change < 0 else 'neutral'}">
                    {'▲' if year_change > 0 else '▼' if year_change < 0 else '●'} {abs(year_change):.2f} ₽
                </div>
                <div class="period-percent {'positive' if year_percent > 0 else 'negative' if year_percent < 0 else 'neutral'}">
                    {abs(year_percent):.1f}%
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">📉</div>
                <div class="stat-label">Минимальная цена за всю историю</div>
                <div class="stat-value">{min_price:.2f} ₽</div>
                <div class="stat-date">{min_price_date if min_price_date else '—'}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-label">Максимальная цена за всю историю</div>
                <div class="stat-value">{max_price:.2f} ₽</div>
                <div class="stat-date">{max_price_date if max_price_date else '—'}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⚖️</div>
                <div class="stat-label">Средняя цена за всю историю</div>
                <div class="stat-value">{avg_price:.2f} ₽</div>
                <div class="stat-date">за {len(spice['price_history'])} дней</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-label">Волатильность</div>
                <div class="stat-value">{(price_range / avg_price * 100):.1f}%</div>
                <div class="stat-date">разброс цены</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">
                <span>📈</span> Динамика изменения цены (последние 90 дней)
            </div>
            <canvas id="priceChart" width="800" height="300" style="width:100%; height:300px;"></canvas>
        </div>
        
        <div class="history-container">
            <div class="history-title">
                <span>📋</span> Полная история изменений (последние 30 записей)
            </div>
            <div class="history-list">
                {history_rows}
            </div>
        </div>
        
        <div class="action-buttons">
            <a href="/" class="btn btn-primary">← Вернуться на главную</a>
            <a href="/analytics" class="btn btn-secondary">📊 Перейти в аналитику</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
    </div>
    
    <script>
        const priceData = {chart_prices_json};
        
        function drawChart() {{
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
            for (let i = 0; i <= 4; i++) {{
                const y = paddingTop + (i / 4) * chartH;
                ctx.beginPath();
                ctx.moveTo(paddingLeft, y);
                ctx.lineTo(w - paddingRight, y);
                ctx.stroke();
                ctx.fillStyle = '#999';
                ctx.font = '10px Arial';
                ctx.fillText(`${{(maxPriceVal - (i / 4) * rangeVal).toFixed(0)}} ₽`, 5, y + 3);
            }}
            
            const stepX = chartW / (priceData.length - 1);
            ctx.beginPath();
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2.5;
            
            for (let i = 0; i < priceData.length; i++) {{
                const x = paddingLeft + i * stepX;
                const y = paddingTop + chartH - ((priceData[i] - minPriceVal) / rangeVal) * chartH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }}
            ctx.stroke();
            
            ctx.lineTo(paddingLeft + (priceData.length - 1) * stepX, paddingTop + chartH);
            ctx.lineTo(paddingLeft, paddingTop + chartH);
            ctx.fillStyle = 'rgba(102,126,234,0.1)';
            ctx.fill();
            
            for (let i = 0; i < priceData.length; i++) {{
                const x = paddingLeft + i * stepX;
                const y = paddingTop + chartH - ((priceData[i] - minPriceVal) / rangeVal) * chartH;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffd700';
                ctx.fill();
                ctx.strokeStyle = '#667eea';
                ctx.lineWidth = 1;
                ctx.stroke();
            }}
            
            const currentY = paddingTop + chartH - ((priceData[priceData.length-1] - minPriceVal) / rangeVal) * chartH;
            ctx.beginPath();
            ctx.strokeStyle = '#ffd700';
            ctx.setLineDash([8, 4]);
            ctx.moveTo(paddingLeft, currentY);
            ctx.lineTo(w - paddingRight, currentY);
            ctx.stroke();
            ctx.setLineDash([]);
        }}
        
        window.onload = function() {{
            drawChart();
            window.addEventListener('resize', function() {{
                setTimeout(drawChart, 200);
            }});
        }};
    </script>
</body>
</html>'''
        return self.http_response(200, html)
    
    def export_data(self):
        spices = self.db.get_all_spices()
        data = {
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_items': len(spices),
            'spices': spices
        }
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += "Content-Disposition: attachment; filename=spices_export.json\r\n"
        response += "Content-Length: " + str(len(json_data.encode())) + "\r\n"
        response += "\r\n"
        response += json_data
        return response.encode()
    
    def users_page(self):
        users = self.auth.users
        rows = ''
        for username, user_data in users.items():
            rows += f'''
            <tr>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;">{username}</td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;">{user_data.get('name', '')}</td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;">{"👑 Администратор" if user_data.get('role') == 'admin' else "👤 Пользователь"}</td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;">{user_data.get('created_at', '')}</td>
                <td style="padding: 12px 15px; border-bottom: 1px solid #f0f0f0;">{"<span class='disabled'>Защищён</span>" if username == 'admin' else f"<a href='/delete_user?username={username}' class='btn-small btn-danger' onclick='return confirm(\"Удалить пользователя {username}?\")'>🗑️ Удалить</a>"}</td>
            </tr>
            '''
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Управление пользователями</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .nav-container {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
        .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ff8c00 0%, #ffa500 50%, #ffb347 100%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .logo span {{ color: #ffd700; background: none; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .nav-links a {{ color: #333; text-decoration: none; margin-left: 25px; padding: 8px 16px; border-radius: 25px; font-weight: 600; transition: 0.3s; }}
        .nav-links a:hover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .container {{ max-width: 1200px; margin: 30px auto; padding: 0 30px; }}
        .table-container {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 20px; overflow-x: auto; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
        th {{ background: rgba(102,126,234,0.1); color: #667eea; font-weight: 700; }}
        tr:hover {{ background: rgba(102,126,234,0.05); }}
        .btn-small {{ padding: 5px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; font-weight: 600; transition: 0.2s; }}
        .btn-danger {{ background: #e53e3e; color: white; }}
        .btn-danger:hover {{ opacity: 0.9; transform: translateY(-1px); }}
        .disabled {{ background: #ccc; padding: 5px 12px; border-radius: 20px; font-size: 12px; }}
        .back {{ display: inline-block; margin-top: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 25px; text-decoration: none; border-radius: 30px; font-weight: 600; transition: 0.3s; }}
        .back:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }}
        h1 {{ color: #667eea; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">🌶️ <span>SpiceDrugs</span> Pro</div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/export">📥 Экспорт</a>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    <div class="container">
        <h1>👥 Управление пользователями</h1>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="padding: 12px 15px;">Логин</th>
                        <th style="padding: 12px 15px;">Имя</th>
                        <th style="padding: 12px 15px;">Роль</th>
                        <th style="padding: 12px 15px;">Дата регистрации</th>
                        <th style="padding: 12px 15px;">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        <a href="/" class="back">← На главную</a>
    </div>
</body>
</html>'''
        return self.http_response(200, html)
    
    def delete_user(self, username):
        if username != 'admin' and username in self.auth.users:
            del self.auth.users[username]
            self.auth.save_users()
        return self.redirect('/users')
    
    def add_spice(self, body):
        params = urllib.parse.parse_qs(body)
        name = params.get('name', [''])[0]
        price = float(params.get('price', ['0'])[0])
        supplier = params.get('supplier', [''])[0]
        stock = int(params.get('stock', ['0'])[0])
        self.db.add_spice(name, price, supplier, stock)
        return self.redirect('/')
    
    def update_spice(self, spice_id, body):
        params = urllib.parse.parse_qs(body)
        name = params.get('name', [''])[0]
        price = float(params.get('price', ['0'])[0])
        supplier = params.get('supplier', [''])[0]
        stock = int(params.get('stock', ['0'])[0])
        self.db.update_spice(spice_id, name, price, supplier, stock)
        return self.redirect('/')
    
    def delete_spice(self, spice_id):
        self.db.delete_spice(spice_id)
        return self.redirect('/')
    
    def redirect(self, location):
        response = "HTTP/1.1 302 Found\r\nLocation: " + location + "\r\nContent-Length: 0\r\n\r\n"
        return response.encode()
    
    def redirect_page(self, location):
        html = '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="1;url=' + location + '"></head><body style="text-align:center;padding:50px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;"><h2>✅ Цены обновлены!</h2><p>Перенаправление...</p></body></html>'
        return self.http_response(200, html)
    
    def http_response(self, code, content):
        response = "HTTP/1.1 " + str(code) + " OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " + str(len(content.encode())) + "\r\n\r\n" + content
        return response.encode()
    
    def not_found(self):
        return self.http_response(404, '<h1>404 - Страница не найдена</h1><a href="/">На главную</a>')
    
    def error_page(self, error):
        return self.http_response(500, '<h1>500 - Ошибка</h1><p>' + error + '</p><a href="/">На главную</a>')
    
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print('🌶️ SpiceDrugs Pro запущен на http://' + self.host + ':' + str(self.port))
        print('👑 Администратор: admin / admin123')
        
        while True:
            client, _ = sock.accept()
            data = client.recv(4096).decode()
            if data:
                client.send(self.handle_request(data))
            client.close()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    HTTPServer(host='0.0.0.0', port=port).run()
