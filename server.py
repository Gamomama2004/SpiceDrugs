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
        return [{'username': u, 'name': data['name'], 'role': '👑 Администратор' if data['role'] == 'admin' else '👤 Пользователь', 'created_at': data['created_at']} 
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
        self.rating_history = {}
        for s in self.spices:
            self.rating_history[s['id']] = []
            # Генерируем от 10 до 25 оценок для каждой специи
            num_ratings = random.randint(10, 25)
            users_list = ['Анна', 'Иван', 'Мария', 'Пётр', 'Елена', 'Дмитрий', 'Ольга', 'Сергей', 'Татьяна', 'Алексей', 'Екатерина', 'Владимир', 'Наталья', 'Михаил', 'Юлия']
            comments_list = [
                'Отличная специя!', 'Хорошее качество', 'Нормально', 'Достойно', 'Рекомендую', 
                'Вкусно!', 'Супер!', 'Классная специя', 'Лучшая в своём роде', 'Буду брать ещё',
                'Хороший аромат', 'Качество отличное', 'Цена соответствует качеству', 'Очень доволен',
                'Неплохо, но дороговато', 'Хорошая специя, советую', 'Прекрасный вкус', 'Топ!'
            ]
            rating_weights = [1, 1, 2, 3, 5]  # 5 звезд чаще
            for _ in range(num_ratings):
                rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
                self.rating_history[s['id']].append({
                    'user': random.choice(users_list),
                    'rating': rating,
                    'comment': random.choice(comments_list),
                    'date': (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d %H:%M:%S')
                })
            self.update_average_rating(s['id'])
    
    def generate_spices(self):
        spices_data = [
            {'id': 1, 'name': 'Чёрный перец горошком', 'price': 890, 'supplier': 'ООО "Специи Мира"', 'stock': 100},
            {'id': 2, 'name': 'Корица цейлонская', 'price': 450, 'supplier': 'ИП "Пряный Двор"', 'stock': 45},
            {'id': 3, 'name': 'Куркума молотая', 'price': 320, 'supplier': 'ООО "Специи Мира"', 'stock': 150},
            {'id': 4, 'name': 'Паприка сладкая', 'price': 280, 'supplier': 'ООО "АгроСпеции"', 'stock': 200},
            {'id': 5, 'name': 'Имбирь молотый', 'price': 550, 'supplier': 'ИП "Пряный Двор"', 'stock': 80},
            {'id': 6, 'name': 'Кардамон зелёный', 'price': 3800, 'supplier': 'ООО "Восток-Специи"', 'stock': 25},
            {'id': 7, 'name': 'Гвоздика', 'price': 1200, 'supplier': 'ООО "Специи Мира"', 'stock': 60},
            {'id': 8, 'name': 'Мускатный орех', 'price': 1500, 'supplier': 'ИП "Пряный Двор"', 'stock': 35},
            {'id': 9, 'name': 'Кунжут белый', 'price': 250, 'supplier': 'ООО "АгроСпеции"', 'stock': 300},
            {'id': 10, 'name': 'Зира (кумин)', 'price': 420, 'supplier': 'ООО "Восток-Специи"', 'stock': 90},
            {'id': 11, 'name': 'Кориандр молотый', 'price': 290, 'supplier': 'ООО "Специи Мира"', 'stock': 120},
            {'id': 12, 'name': 'Шафран настоящий', 'price': 15000, 'supplier': 'ИП "Пряный Двор"', 'stock': 5},
            {'id': 13, 'name': 'Бадьян', 'price': 780, 'supplier': 'ООО "Восток-Специи"', 'stock': 40},
            {'id': 14, 'name': 'Асафетида', 'price': 1250, 'supplier': 'ООО "Специи Мира"', 'stock': 20},
            {'id': 15, 'name': 'Фенхель', 'price': 360, 'supplier': 'ИП "Пряный Двор"', 'stock': 110},
            {'id': 16, 'name': 'Тмин', 'price': 310, 'supplier': 'ООО "АгроСпеции"', 'stock': 95},
            {'id': 17, 'name': 'Горчица белая', 'price': 180, 'supplier': 'ООО "Специи Мира"', 'stock': 250},
            {'id': 18, 'name': 'Укроп', 'price': 220, 'supplier': 'ИП "Пряный Двор"', 'stock': 180},
            {'id': 19, 'name': 'Петрушка', 'price': 200, 'supplier': 'ООО "АгроСпеции"', 'stock': 200},
            {'id': 20, 'name': 'Базилик', 'price': 260, 'supplier': 'ООО "Специи Мира"', 'stock': 160},
            {'id': 21, 'name': 'Орегано', 'price': 340, 'supplier': 'ИП "Пряный Двор"', 'stock': 85},
            {'id': 22, 'name': 'Розмарин', 'price': 420, 'supplier': 'ООО "Восток-Специи"', 'stock': 70},
            {'id': 23, 'name': 'Тимьян', 'price': 380, 'supplier': 'ООО "Специи Мира"', 'stock': 75},
            {'id': 24, 'name': 'Майоран', 'price': 460, 'supplier': 'ИП "Пряный Двор"', 'stock': 55},
            {'id': 25, 'name': 'Ваниль', 'price': 8500, 'supplier': 'ООО "Восток-Специи"', 'stock': 8},
            {'id': 26, 'name': 'Перец розовый', 'price': 1850, 'supplier': 'ООО "Специи Мира"', 'stock': 30},
            {'id': 27, 'name': 'Перец душистый', 'price': 1100, 'supplier': 'ИП "Пряный Двор"', 'stock': 65},
            {'id': 28, 'name': 'Хмели-сунели', 'price': 370, 'supplier': 'ООО "АгроСпеции"', 'stock': 130},
            {'id': 29, 'name': 'Аджика', 'price': 290, 'supplier': 'ООО "Специи Мира"', 'stock': 140},
            {'id': 30, 'name': 'Карри', 'price': 390, 'supplier': 'ИП "Пряный Двор"', 'stock': 120},
            {'id': 31, 'name': 'Пажитник', 'price': 510, 'supplier': 'ООО "АгроСпеции"', 'stock': 50},
            {'id': 32, 'name': 'Чили хлопья', 'price': 470, 'supplier': 'ООО "Специи Мира"', 'stock': 95},
            {'id': 33, 'name': 'Суммах', 'price': 580, 'supplier': 'ИП "Пряный Двор"', 'stock': 45},
            {'id': 34, 'name': 'Чернушка', 'price': 440, 'supplier': 'ООО "АгроСпеции"', 'stock': 60},
            {'id': 35, 'name': 'Анис звёздчатый', 'price': 720, 'supplier': 'ООО "Восток-Специи"', 'stock': 35},
            {'id': 36, 'name': 'Барбарис сушёный', 'price': 630, 'supplier': 'ИП "Пряный Двор"', 'stock': 40},
            {'id': 37, 'name': 'Калган (корень)', 'price': 840, 'supplier': 'ООО "Специи Мира"', 'stock': 25},
            {'id': 38, 'name': 'Можжевельник', 'price': 530, 'supplier': 'ООО "АгроСпеции"', 'stock': 30},
            {'id': 39, 'name': 'Мелисса сушёная', 'price': 340, 'supplier': 'ИП "Пряный Двор"', 'stock': 70},
            {'id': 40, 'name': 'Мята перечная', 'price': 280, 'supplier': 'ООО "Специи Мира"', 'stock': 110},
            {'id': 41, 'name': 'Шалфей', 'price': 420, 'supplier': 'ООО "Восток-Специи"', 'stock': 55},
            {'id': 42, 'name': 'Эстрагон', 'price': 390, 'supplier': 'ИП "Пряный Двор"', 'stock': 65},
            {'id': 43, 'name': 'Кинза сушёная', 'price': 300, 'supplier': 'ООО "АгроСпеции"', 'stock': 90},
            {'id': 44, 'name': 'Лавровый лист', 'price': 140, 'supplier': 'ООО "Специи Мира"', 'stock': 250},
            {'id': 45, 'name': 'Майоран садовый', 'price': 450, 'supplier': 'ИП "Пряный Двор"', 'stock': 50},
            {'id': 46, 'name': 'Чабер садовый', 'price': 480, 'supplier': 'ООО "Восток-Специи"', 'stock': 45},
            {'id': 47, 'name': 'Кресс-салат', 'price': 270, 'supplier': 'ООО "АгроСпеции"', 'stock': 80}
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
            s['rating'] = round(random.uniform(3.5, 4.9), 1)
        return spices_data
    
    def update_average_rating(self, spice_id):
        if spice_id in self.rating_history and self.rating_history[spice_id]:
            ratings = [r['rating'] for r in self.rating_history[spice_id]]
            avg = sum(ratings) / len(ratings)
            for s in self.spices:
                if s['id'] == spice_id:
                    s['rating'] = round(avg, 1)
                    break
    
    def add_rating(self, spice_id, username, rating, comment=''):
        spice = self.get_spice_by_id(spice_id)
        if not spice:
            return False
        rating = int(rating)
        if rating < 1 or rating > 5:
            return False
        if spice_id not in self.rating_history:
            self.rating_history[spice_id] = []
        self.rating_history[spice_id].append({
            'user': username,
            'rating': rating,
            'comment': comment,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.update_average_rating(spice_id)
        return True
    
    def delete_rating(self, spice_id, rating_index):
        if spice_id in self.rating_history and rating_index < len(self.rating_history[spice_id]):
            del self.rating_history[spice_id][rating_index]
            self.update_average_rating(spice_id)
            return True
        return False
    
    def get_rating_history(self, spice_id):
        if spice_id in self.rating_history:
            return self.rating_history[spice_id]
        return []
    
    def get_rating_stats(self, spice_id):
        spice = self.get_spice_by_id(spice_id)
        if not spice:
            return {'avg': 0, 'count': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        
        ratings = self.get_rating_history(spice_id)
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in ratings:
            counts[r['rating']] += 1
        
        return {
            'avg': spice['rating'],
            'count': len(ratings),
            '1': counts[1],
            '2': counts[2],
            '3': counts[3],
            '4': counts[4],
            '5': counts[5]
        }
    
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
            'rating': 4.0,
            'price_history': price_history
        })
        self.rating_history[new_id] = []
        return True
    
    def update_spice(self, spice_id, name, price, supplier, stock):
        spice = self.get_spice_by_id(spice_id)
        if spice:
            spice['name'] = name
            spice['price'] = float(price)
            spice['supplier'] = supplier
            spice['stock'] = int(stock)
            spice['price_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'price': float(price)
            })
            return True
        return False
    
    def delete_spice(self, spice_id):
        self.spices = [s for s in self.spices if s['id'] != spice_id]
        if spice_id in self.rating_history:
            del self.rating_history[spice_id]
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

# ==================== БАЗОВЫЕ СТИЛИ ДЛЯ ВСЕХ СТРАНИЦ ====================
BASE_STYLES = '''
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        min-height: 100vh;
    }
    .navbar {
        background: #1a1a1a;
        padding: 15px 30px;
        border-bottom: 2px solid #ff8c00;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
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
        flex-wrap: wrap;
    }
    .logo {
        font-size: 24px;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .logo-icon { font-size: 28px; }
    .logo-text { background: linear-gradient(135deg, #ff8c00 0%, #ffa500 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
    .nav-links { display: flex; flex-wrap: wrap; align-items: center; gap: 5px; }
    .nav-links a {
        color: #fff;
        text-decoration: none;
        padding: 8px 18px;
        border-radius: 25px;
        transition: all 0.3s;
        font-weight: 600;
    }
    .nav-links a:hover { background: #ff8c00; color: #1a1a1a; transform: translateY(-2px); }
    .user-info {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-left: 15px;
        padding: 8px 18px;
        background: #333;
        border-radius: 30px;
        color: white;
        font-weight: 600;
    }
    .role-badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    .role-badge.admin { background: #ff8c00; color: #1a1a1a; }
    .role-badge.user { background: #555; color: white; }
    .container { max-width: 1400px; margin: 30px auto; padding: 0 30px; }
    .footer {
        background: #1a1a1a;
        text-align: center;
        padding: 20px;
        margin-top: 40px;
        border-top: 1px solid #ff8c00;
        color: #888;
        font-size: 12px;
    }
    .btn-primary {
        background: #333;
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
        font-size: 13px;
        font-weight: 600;
        transition: all 0.3s;
        border: 1px solid #444;
    }
    .btn-primary:hover { background: #ff8c00; color: #1a1a1a; transform: translateY(-2px); }
    .btn-secondary {
        background: #333;
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
        font-size: 13px;
        font-weight: 600;
        transition: all 0.3s;
        border: 1px solid #ff8c00;
    }
    .btn-secondary:hover { background: #ff8c00; color: #1a1a1a; transform: translateY(-2px); }
    .btn-small {
        padding: 4px 10px;
        border-radius: 20px;
        text-decoration: none;
        font-size: 11px;
        margin: 0 2px;
        display: inline-block;
        transition: all 0.2s;
        font-weight: 600;
        background: #333;
        color: white;
        border: 1px solid #444;
    }
    .btn-small:hover { background: #ff8c00; color: #1a1a1a; transform: translateY(-1px); }
    .btn-info { background: #333; border-color: #4299e1; color: white; }
    .btn-info:hover { background: #4299e1; color: white; }
    .btn-warning { background: #333; border-color: #ed8936; color: white; }
    .btn-warning:hover { background: #ed8936; color: white; }
    .btn-danger { background: #333; border-color: #e53e3e; color: white; }
    .btn-danger:hover { background: #e53e3e; color: white; }
    .back-button {
        text-align: center;
        margin-top: 30px;
    }
    .card {
        background: #2d2d2d;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        border: 1px solid #444;
    }
    h1, h2, h3 { color: #ff8c00; margin-bottom: 20px; }
    p { color: #ccc; }
</style>
'''

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
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: #2d2d2d;
            border-radius: 20px;
            width: 420px;
            max-width: 90%;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            border: 1px solid #444;
        }
        .header {
            background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-bottom: 3px solid #ff8c00;
        }
        .header h1 { 
            font-size: 32px; 
            margin-bottom: 10px;
            background: linear-gradient(135deg, #ff8c00 0%, #ffa500 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .logo-icon { font-size: 60px; margin-bottom: 10px; }
        .tabs {
            display: flex;
            border-bottom: 2px solid #444;
        }
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            background: #1a1a1a;
            border: none;
            font-size: 16px;
            font-weight: 600;
            color: #ccc;
        }
        .tab.active {
            background: #2d2d2d;
            color: #ff8c00;
            border-bottom: 3px solid #ff8c00;
        }
        .form-panel { padding: 40px; display: none; }
        .form-panel.active { display: block; }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #ccc; }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #444;
            border-radius: 10px;
            background: #1a1a1a;
            color: #fff;
        }
        .form-group input:focus { outline: none; border-color: #ff8c00; }
        .btn-submit {
            width: 100%;
            padding: 12px;
            background: #333;
            color: white;
            border: 1px solid #ff8c00;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-submit:hover { background: #ff8c00; color: #1a1a1a; }
        .message { margin: 20px; padding: 10px; border-radius: 8px; text-align: center; display: none; }
        .message.error { background: #e53e3e; color: white; display: block; }
        .message.success { background: #48bb78; color: white; display: block; }
        .footer { background: #1a1a1a; padding: 20px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #444; }
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
            <p>© 2026 SpiceDrugs Pro — Система мониторинга специй</p>
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
    ''' + BASE_STYLES + '''
    <style>
        .welcome {
            background: #2d2d2d;
            padding: 25px 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #ff8c00;
            border: 1px solid #444;
        }
        .welcome h2 { color: #ff8c00; margin-bottom: 8px; font-size: 24px; font-weight: 700; }
        .welcome p { color: #ccc; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 15px;
            transition: all 0.3s;
            border: 1px solid #444;
            text-align: center;
        }
        .stat-card:hover { transform: translateY(-3px); border-color: #ff8c00; }
        .stat-card h4 { color: #ff8c00; font-size: 12px; text-transform: uppercase; margin-bottom: 10px; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: white; }
        .table-container {
            background: #2d2d2d;
            border-radius: 20px;
            overflow-x: auto;
            border: 1px solid #444;
        }
        table { width: 100%; border-collapse: collapse; min-width: 800px; }
        th { 
            padding: 15px 12px; 
            text-align: left; 
            background: #1a1a1a; 
            color: #ff8c00; 
            font-weight: 700; 
            border-bottom: 2px solid #ff8c00;
        }
        td { padding: 14px 12px; text-align: left; border-bottom: 1px solid #444; color: #fff; vertical-align: middle; }
        tr:hover td { background: #3d3d3d; }
        .admin-buttons { display: flex; gap: 10px; margin-bottom: 20px; justify-content: flex-end; flex-wrap: wrap; }
        .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }
        .header-actions h2 { color: #ff8c00; font-weight: 700; font-size: 22px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/spice-graph">📊 Графики цен</a>
                <a href="/ratings">⭐ Рейтинг специй</a>
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
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for s in spices %}
                    <tr>
                        <td>{{ s.id }}</td>
                        <td><strong style="color:#fff;">{{ s.name }}</strong></td>
                        <td>{{ s.supplier }}</td>
                        <td>{{ s.price }} ₽</td>
                        <td>{{ "%.2f"|format(s.price / 10) }} ₽</td>
                        <td>{{ s.stock }} кг</td>
                        <td class="actions">
                            <a href="/history/{{ s.id }}" class="btn-small btn-info">📊 История</a>
                            <a href="/rate/{{ s.id }}" class="btn-small btn-warning">⭐ Оценить</a>
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
        
        <div class="back-button">
            <a href="/" class="btn-primary">🏠 Вернуться на главную</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Профессиональная система мониторинга рынка специй</p>
        <p style="font-size: 12px; margin-top: 8px;">© 2026 Все права защищены</p>
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
    ''' + BASE_STYLES + '''
    <style>
        .selector {
            display: flex;
            gap: 20px;
            align-items: flex-end;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        .selector-group { flex: 1; min-width: 200px; }
        .selector-group label { display: block; margin-bottom: 8px; font-weight: 700; color: #ff8c00; }
        .selector-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #444;
            border-radius: 12px;
            background: #1a1a1a;
            color: #fff;
            font-size: 14px;
        }
        .period-buttons { display: flex; gap: 12px; margin: 20px 0; flex-wrap: wrap; }
        .period-btn {
            padding: 8px 22px;
            background: #333;
            color: #ccc;
            border-radius: 30px;
            cursor: pointer;
            border: 1px solid #444;
            font-weight: 600;
            transition: all 0.3s;
        }
        .period-btn.active {
            background: #ff8c00;
            color: #1a1a1a;
            border-color: #ff8c00;
        }
        .chart-container { text-align: center; margin-top: 20px; }
        canvas { max-width: 100%; height: auto; background: #1a1a1a; border-radius: 15px; }
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        .stat-mini {
            background: #1a1a1a;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #444;
        }
        .stat-mini .label { font-size: 12px; color: #888; }
        .stat-mini .value { font-size: 20px; font-weight: bold; color: #ff8c00; }
        
        .btn-submit-chart {
            background: linear-gradient(135deg, #333 0%, #2d2d2d 100%);
            border: 2px solid #ff8c00;
            color: white;
            padding: 14px 32px;
            border-radius: 40px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            transition: all 0.3s;
            width: 100%;
            text-align: center;
            letter-spacing: 1px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .btn-submit-chart:hover {
            background: linear-gradient(135deg, #ff8c00 0%, #ffa500 100%);
            color: #1a1a1a;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(255,140,0,0.3);
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
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
                    <button class="btn-submit-chart" onclick="updateChart()">📊 Показать график</button>
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
        <div class="back-button">
            <a href="/" class="btn-primary">🏠 Вернуться на главную</a>
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
            const w = canvas.clientWidth;
            const h = 400;
            canvas.width = w;
            canvas.height = h;
            
            if (!prices || prices.length < 2) {
                ctx.fillStyle = '#888';
                ctx.fillText('Недостаточно данных', w/2-50, h/2);
                return;
            }
            
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const range = maxPrice - minPrice || 1;
            const avgPrice = prices.reduce((a,b) => a + b, 0) / prices.length;
            const currentPrice = prices[prices.length-1];
            
            document.getElementById('stats-container').innerHTML = `
                <div class="stat-mini"><div class="label">📉 Минимум</div><div class="value">${minPrice.toFixed(2)} ₽</div></div>
                <div class="stat-mini"><div class="label">📈 Максимум</div><div class="value">${maxPrice.toFixed(2)} ₽</div></div>
                <div class="stat-mini"><div class="label">📊 Средняя</div><div class="value">${avgPrice.toFixed(2)} ₽</div></div>
                <div class="stat-mini"><div class="label">💰 Текущая</div><div class="value">${currentPrice.toFixed(2)} ₽</div></div>
            `;
            
            const paddingLeft = 60;
            const paddingRight = 40;
            const paddingTop = 30;
            const paddingBottom = 50;
            const chartW = w - paddingLeft - paddingRight;
            const chartH = h - paddingTop - paddingBottom;
            
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, w, h);
            
            for (let i = 0; i <= 4; i++) {
                const y = paddingTop + (i / 4) * chartH;
                ctx.beginPath();
                ctx.strokeStyle = '#444';
                ctx.moveTo(paddingLeft, y);
                ctx.lineTo(w - paddingRight, y);
                ctx.stroke();
                ctx.fillStyle = '#888';
                ctx.fillText(`${(maxPrice - (i / 4) * range).toFixed(0)} ₽`, 5, y + 3);
            }
            
            if (dates && dates.length > 0) {
                const stepX = chartW / (prices.length - 1);
                for (let i = 0; i < Math.min(5, dates.length); i++) {
                    const idx = Math.floor(i * (dates.length - 1) / 4);
                    const x = paddingLeft + idx * stepX;
                    const date = new Date(dates[idx]);
                    ctx.fillStyle = '#888';
                    ctx.fillText(`${date.getDate()}.${date.getMonth()+1}`, x - 15, h - paddingBottom + 15);
                }
            }
            
            const stepX = chartW / (prices.length - 1);
            ctx.beginPath();
            ctx.strokeStyle = '#ff8c00';
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
            ctx.fillStyle = 'rgba(255,140,0,0.15)';
            ctx.fill();
            
            for (let i = 0; i < prices.length; i++) {
                const x = paddingLeft + i * stepX;
                const y = paddingTop + chartH - ((prices[i] - minPrice) / range) * chartH;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffa500';
                ctx.fill();
            }
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
        
        window.onload = function() {
            updateChart();
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
    ''' + BASE_STYLES + '''
    <style>
        .price { font-size: 32px; color: #ffa500; font-weight: bold; }
        .price-100g { font-size: 16px; color: #888; margin-top: 5px; }
        canvas { width: 100%; height: auto; background: #1a1a1a; border-radius: 15px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <a href="/" style="color:#fff; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h1>📈 История цен: {{ spice.name }}</h1>
            <div class="price">💰 Цена за кг: {{ spice.price }} ₽</div>
            <div class="price-100g">📊 Цена за 100 г: {{ "%.2f"|format(spice.price / 10) }} ₽</div>
            <p style="margin-top: 20px; color:#fff;">🏭 Поставщик: {{ spice.supplier }}</p>
            <p style="color:#fff;">📦 Остаток: {{ spice.stock }} кг</p>
        </div>
        
        <div class="card">
            <h2>📊 Динамика цены (90 дней)</h2>
            <canvas id="priceChart" width="800" height="350"></canvas>
        </div>
        
        <div class="back-button">
            <a href="/" class="btn-primary">🏠 Вернуться на главную</a>
            <a href="/spice-graph" class="btn-primary" style="background:#333; border-color:#4299e1; margin-left: 15px;">📊 Все графики</a>
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
        const h = 350;
        canvas.width = w;
        canvas.height = h;
        
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, w, h);
        
        if (prices && prices.length > 1) {
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const range = maxPrice - minPrice || 1;
            const padding = 60;
            const chartW = w - padding * 2;
            const chartH = h - 80;
            const stepX = chartW / (prices.length - 1);
            
            for (let i = 0; i <= 4; i++) {
                const y = 40 + (i / 4) * chartH;
                ctx.beginPath();
                ctx.strokeStyle = '#444';
                ctx.moveTo(padding, y);
                ctx.lineTo(w - padding, y);
                ctx.stroke();
                ctx.fillStyle = '#888';
                ctx.fillText(`${(maxPrice - (i / 4) * range).toFixed(0)} ₽`, 10, y + 3);
            }
            
            ctx.beginPath();
            ctx.strokeStyle = '#ff8c00';
            ctx.lineWidth = 2.5;
            for (let i = 0; i < prices.length; i++) {
                const x = padding + i * stepX;
                const y = 40 + chartH - ((prices[i] - minPrice) / range) * chartH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            
            ctx.lineTo(padding + (prices.length - 1) * stepX, 40 + chartH);
            ctx.lineTo(padding, 40 + chartH);
            ctx.fillStyle = 'rgba(255,140,0,0.15)';
            ctx.fill();
            
            for (let i = 0; i < prices.length; i++) {
                const x = padding + i * stepX;
                const y = 40 + chartH - ((prices[i] - minPrice) / range) * chartH;
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = '#ffa500';
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
    ''' + BASE_STYLES + '''
    <style>
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 25px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #2d2d2d;
            padding: 25px;
            border-radius: 20px;
            border: 1px solid #444;
            text-align: center;
        }
        .stat-card h4 { color: #ff8c00; font-size: 13px; margin-bottom: 12px; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: white; }
        .table-container {
            background: #2d2d2d;
            border-radius: 20px;
            overflow-x: auto;
            border: 1px solid #444;
        }
        table { width: 100%; border-collapse: collapse; min-width: 800px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #444; }
        th { background: #1a1a1a; color: #ff8c00; font-weight: 700; }
        tr:hover td { background: #3d3d3d; }
        td { color: #fff; }
        .stock-status { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .stock-low { background: #e53e3e; color: white; }
        .stock-medium { background: #ed8936; color: white; }
        .stock-high { background: #48bb78; color: white; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/spice-graph">📊 Графики</a>
                <a href="/ratings">⭐ Рейтинг</a>
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
                    </tr>
                </thead>
                <tbody>
                    {% for s in spices %}
                    <tr>
                        <td><strong style="color:#fff;">{{ s.name }}</strong></td>
                        <td>{{ s.supplier }}</td>
                        <td>{{ s.price }} ₽</td>
                        <td style="white-space: nowrap;">{{ "%.2f"|format(s.price / 10) }} ₽</td>
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
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="back-button">
            <a href="/" class="btn-primary">🏠 Вернуться на главную</a>
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
    <title>Добавить специю - SpiceDrugs Pro</title>
    ''' + BASE_STYLES + '''
    <style>
        .form-container { max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 40px; border-radius: 25px; border: 1px solid #444; }
        h2 { color: #ff8c00; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #ccc; }
        input { width: 100%; padding: 12px; border: 2px solid #444; border-radius: 12px; background: #1a1a1a; color: #fff; }
        input:focus { outline: none; border-color: #ff8c00; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <a href="/" style="color:#fff; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h2>➕ Добавление новой специи</h2>
            <form method="POST">
                <div class="form-group"><label>🌿 Название специи</label><input type="text" name="name" required placeholder="Например: Шафран"></div>
                <div class="form-group"><label>💰 Цена (₽ за кг)</label><input type="number" step="0.01" name="price" required placeholder="0.00"></div>
                <div class="form-group"><label>🏭 Поставщик</label><input type="text" name="supplier" required placeholder="ООО Поставщик"></div>
                <div class="form-group"><label>📦 Количество на складе (кг)</label><input type="number" name="stock" required placeholder="0"></div>
                <button type="submit" class="btn-primary">💾 Сохранить</button>
            </form>
            <div class="back-button" style="margin-top: 20px;">
                <a href="/" class="btn-secondary">← Вернуться на главную</a>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
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
    ''' + BASE_STYLES + '''
    <style>
        .form-container { max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 40px; border-radius: 25px; border: 1px solid #444; }
        h2 { color: #ed8936; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #ccc; }
        input { width: 100%; padding: 12px; border: 2px solid #444; border-radius: 12px; background: #1a1a1a; color: #fff; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <a href="/" style="color:#fff; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h2>✏️ Редактирование: {{ spice.name }}</h2>
            <form method="POST">
                <div class="form-group"><label>🌿 Название</label><input type="text" name="name" value="{{ spice.name }}" required></div>
                <div class="form-group"><label>💰 Цена (₽ за кг)</label><input type="number" step="0.01" name="price" value="{{ spice.price }}" required></div>
                <div class="form-group"><label>🏭 Поставщик</label><input type="text" name="supplier" value="{{ spice.supplier }}" required></div>
                <div class="form-group"><label>📦 Количество (кг)</label><input type="number" name="stock" value="{{ spice.stock }}" required></div>
                <button type="submit" class="btn-primary">💾 Сохранить изменения</button>
            </form>
            <div class="back-button" style="margin-top: 20px;">
                <a href="/" class="btn-secondary">← Назад</a>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
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
    ''' + BASE_STYLES + '''
    <style>
        .table-container {
            background: #2d2d2d;
            border-radius: 20px;
            overflow-x: auto;
            border: 1px solid #444;
        }
        table { width: 100%; border-collapse: collapse; min-width: 700px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #444; }
        th { background: #1a1a1a; color: #ff8c00; font-weight: 700; }
        tr:hover td { background: #3d3d3d; }
        td { color: #fff; }
        .btn-small { padding: 5px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; font-weight: 600; background: #333; border: 1px solid #444; }
        .btn-danger { background: #333; border-color: #e53e3e; color: white; }
        .btn-danger:hover { background: #e53e3e; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <a href="/" style="color:#fff; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    
    <div class="container">
        <h1>👥 Управление пользователями</h1>
        <div class="table-container">
            <table>
                <thead>
                    <tr><th>Логин</th><th>Имя</th><th>Роль</th><th>Дата регистрации</th><th>Действия</th></tr>
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
                            <span style="color:#888;">Защищён</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <div class="back-button">
            <a href="/" class="btn-primary">🏠 Вернуться на главную</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
    </div>
</body>
</html>
'''

RATING_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Рейтинг специй - SpiceDrugs Pro</title>
    ''' + BASE_STYLES + '''
    <style>
        .spice-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 25px;
        }
        .spice-card {
            background: #2d2d2d;
            border-radius: 20px;
            padding: 25px;
            border: 1px solid #444;
            transition: all 0.3s;
        }
        .spice-card:hover { transform: translateY(-5px); border-color: #ff8c00; }
        .spice-name { font-size: 20px; font-weight: bold; color: #fff; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #444; }
        .rating-stats {
            margin: 15px 0;
            padding: 10px;
            background: #1a1a1a;
            border-radius: 12px;
        }
        .avg-rating {
            text-align: center;
            margin-bottom: 15px;
        }
        .stars { margin: 5px 0; }
        .star { color: #444; font-size: 22px; }
        .star.filled { color: #ffc107; }
        .star.half { color: #ffc107; position: relative; }
        .value { font-size: 20px; color: #ffc107; font-weight: bold; margin-top: 5px; }
        .count { font-size: 12px; color: #888; margin-top: 3px; }
        .stat-bar { display: flex; align-items: center; gap: 10px; margin: 8px 0; }
        .stat-label { width: 35px; color: #ffc107; font-size: 13px; font-weight: 600; }
        .stat-bar-bg { flex: 1; height: 8px; background: #444; border-radius: 4px; overflow: hidden; }
        .stat-bar-fill { height: 100%; background: #ffc107; border-radius: 4px; }
        .stat-count { width: 40px; color: #888; font-size: 12px; }
        .btn-rate {
            background: #333;
            border: 1px solid #ff8c00;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            font-weight: 600;
            margin-top: 15px;
            text-align: center;
            width: 100%;
            transition: all 0.3s;
        }
        .btn-rate:hover { background: #ff8c00; color: #1a1a1a; }
        
        .info-banner {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border-left: 4px solid #ff8c00;
            border-right: 4px solid #ff8c00;
            border-radius: 12px;
            padding: 20px 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .info-banner h3 {
            color: #ff8c00;
            font-size: 18px;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        .info-banner p {
            color: #fff;
            font-size: 14px;
            line-height: 1.5;
            opacity: 0.9;
        }
        .info-icon {
            font-size: 32px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/analytics">📈 Аналитика</a>
                <a href="/spice-graph">📊 Графики</a>
                <a href="/ratings">⭐ Рейтинг</a>
                <a href="/logout">🚪 Выйти</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="info-banner">
            <div class="info-icon">⭐</div>
            <h3>Участвуйте в оценке специй!</h3>
            <p>Оценивайте качество специй и смотрите рейтинг от других пользователей. Ваше мнение помогает другим делать правильный выбор!</p>
        </div>
        
        <div class="spice-grid">
            {% for s in spices %}
            <div class="spice-card">
                <div class="spice-name">{{ s.name }}</div>
                <div class="rating-stats">
                    <div class="avg-rating">
                        <div class="stars">
                            {% set full = (s.rating)|round(0)|int %}
                            {% set half = (s.rating - full) >= 0.4 %}
                            {% for i in range(1, 6) %}
                                {% if i <= full %}
                                    <span class="star filled">★</span>
                                {% elif half and i == full + 1 %}
                                    <span class="star half">★</span>
                                {% else %}
                                    <span class="star">★</span>
                                {% endif %}
                            {% endfor %}
                        </div>
                        <div class="value">{{ "%.1f"|format(s.rating) }}/5</div>
                        <div class="count">{{ stats[s.id].count }} оценок</div>
                    </div>
                    <div class="stat-bar">
                        <span class="stat-label">5★</span>
                        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: {{ (stats[s.id]['5'] / stats[s.id].count * 100) if stats[s.id].count > 0 else 0 }}%"></div></div>
                        <span class="stat-count">{{ stats[s.id]['5'] }}</span>
                    </div>
                    <div class="stat-bar">
                        <span class="stat-label">4★</span>
                        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: {{ (stats[s.id]['4'] / stats[s.id].count * 100) if stats[s.id].count > 0 else 0 }}%"></div></div>
                        <span class="stat-count">{{ stats[s.id]['4'] }}</span>
                    </div>
                    <div class="stat-bar">
                        <span class="stat-label">3★</span>
                        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: {{ (stats[s.id]['3'] / stats[s.id].count * 100) if stats[s.id].count > 0 else 0 }}%"></div></div>
                        <span class="stat-count">{{ stats[s.id]['3'] }}</span>
                    </div>
                    <div class="stat-bar">
                        <span class="stat-label">2★</span>
                        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: {{ (stats[s.id]['2'] / stats[s.id].count * 100) if stats[s.id].count > 0 else 0 }}%"></div></div>
                        <span class="stat-count">{{ stats[s.id]['2'] }}</span>
                    </div>
                    <div class="stat-bar">
                        <span class="stat-label">1★</span>
                        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: {{ (stats[s.id]['1'] / stats[s.id].count * 100) if stats[s.id].count > 0 else 0 }}%"></div></div>
                        <span class="stat-count">{{ stats[s.id]['1'] }}</span>
                    </div>
                </div>
                <a href="/rate/{{ s.id }}" class="btn-rate">⭐ Оценить эту специю</a>
            </div>
            {% endfor %}
        </div>
        
        <div class="back-button">
            <a href="/" class="btn-primary">🏠 Вернуться на главную</a>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
    </div>
</body>
</html>
'''

RATE_FORM_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Оценить - {{ spice.name }}</title>
    ''' + BASE_STYLES + '''
    <style>
        .form-container { max-width: 700px; margin: 0 auto; }
        .spice-name { font-size: 24px; color: #fff; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #444; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 10px; color: #ccc; font-weight: 600; }
        select {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 2px solid #ff8c00;
            border-radius: 10px;
            color: #fff;
            font-size: 16px;
        }
        textarea {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 2px solid #444;
            border-radius: 10px;
            color: #fff;
            resize: vertical;
        }
        textarea:focus { outline: none; border-color: #ff8c00; }
        .history {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #444;
        }
        .history h3 { color: #ff8c00; margin-bottom: 15px; }
        .review-item {
            padding: 12px;
            border-bottom: 1px solid #444;
        }
        .review-user { color: #ffc107; font-weight: bold; }
        .review-rating { color: #ffc107; margin: 5px 0; }
        .review-comment { color: #ccc; margin: 5px 0; font-style: italic; }
        .review-date { color: #888; font-size: 11px; }
        .delete-review {
            color: #e53e3e;
            text-decoration: none;
            font-size: 11px;
            margin-left: 10px;
        }
        .delete-review:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="nav-container">
            <div class="logo">
                <span class="logo-icon">🌶️</span>
                <span class="logo-text">SpiceDrugs Pro</span>
            </div>
            <a href="/" style="color:#fff; text-decoration:none;">🏠 Главная</a>
        </div>
    </div>
    
    <div class="container">
        <div class="card form-container">
            <h1>⭐ Оцените специю</h1>
            <div class="spice-name">{{ spice.name }}</div>
            
            <form method="POST">
                <div class="form-group">
                    <label>Ваша оценка:</label>
                    <select name="rating" required>
                        <option value="5">★★★★★ (5) - Отлично</option>
                        <option value="4">★★★★☆ (4) - Хорошо</option>
                        <option value="3">★★★☆☆ (3) - Нормально</option>
                        <option value="2">★★☆☆☆ (2) - Плохо</option>
                        <option value="1">★☆☆☆☆ (1) - Ужасно</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Ваш комментарий (необязательно):</label>
                    <textarea name="comment" rows="3" placeholder="Поделитесь своим мнением о специи..."></textarea>
                </div>
                <button type="submit" class="btn-primary">⭐ Отправить оценку</button>
            </form>
            
            <div class="history">
                <h3>📝 История оценок</h3>
                {% if reviews %}
                    {% for r in reviews %}
                    <div class="review-item">
                        <div class="review-user">👤 {{ r.user }}</div>
                        <div class="review-rating">
                            {% for i in range(1, 6) %}
                                {% if i <= r.rating %}★{% else %}☆{% endif %}
                            {% endfor %}
                        </div>
                        <div class="review-comment">"{{ r.comment }}"</div>
                        <div class="review-date">📅 {{ r.date }}
                            {% if is_admin %}
                            <a href="/delete_rating/{{ spice.id }}/{{ loop.index0 }}" class="delete-review" onclick="return confirm('Удалить эту оценку?')">🗑️ Удалить</a>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="color:#888;">Пока нет оценок. Будьте первым!</p>
                {% endif %}
            </div>
            
            <div class="back-button" style="margin-top: 20px;">
                <a href="/ratings" class="btn-secondary">← Вернуться к рейтингу</a>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>🌶️ SpiceDrugs Pro — Система мониторинга специй</p>
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
    dates = [h['date'] for h in spice['price_history'][-90:]]
    return render_template_string(HISTORY_TEMPLATE, spice=spice, prices=prices, dates=dates)

@app.route('/ratings')
def ratings():
    if 'username' not in session:
        return redirect('/login_page')
    
    spices = db.get_all()
    stats = {}
    for s in spices:
        stats[s['id']] = db.get_rating_stats(s['id'])
    return render_template_string(RATING_TEMPLATE, spices=spices, stats=stats)

@app.route('/rate/<int:spice_id>', methods=['GET', 'POST'])
def rate_spice(spice_id):
    if 'username' not in session:
        return redirect('/login_page')
    
    spice = db.get_spice_by_id(spice_id)
    if not spice:
        return redirect('/ratings')
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '')
        username = session['username']
        
        db.add_rating(spice_id, username, rating, comment)
        return redirect(f'/ratings')
    
    reviews = db.get_rating_history(spice_id)[-15:][::-1]
    is_admin = auth.is_admin(session['username'])
    return render_template_string(RATE_FORM_TEMPLATE, spice=spice, reviews=reviews, is_admin=is_admin)

@app.route('/delete_rating/<int:spice_id>/<int:rating_index>')
def delete_rating(spice_id, rating_index):
    if 'username' not in session:
        return redirect('/login_page')
    if not auth.is_admin(session['username']):
        return redirect('/')
    
    db.delete_rating(spice_id, rating_index)
    return redirect(f'/rate/{spice_id}')

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
        
        db.add_spice(name, price, supplier, stock)
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
        
        db.update_spice(spice_id, name, price, supplier, stock)
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