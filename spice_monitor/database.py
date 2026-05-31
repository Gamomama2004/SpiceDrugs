import json
import os
from datetime import datetime, timedelta
import random

class SpiceDatabase:
    def __init__(self, data_file='data/spices.json'):
        self.data_file = data_file
        self.spices = []
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.spices = json.load(f)
        else:
            os.makedirs('data', exist_ok=True)
            self.spices = self.generate_spices_with_history()
            self.save_data()
    
    def generate_spices_with_history(self):
        """Генерация 34 специй с историей цен за год"""
        base_spices = [
            {'name': 'Чёрный перец горошком', 'base_price': 350, 'supplier': 'ООО "Специи Мира"', 'in_stock': 100, 'volatility': 0.08},
            {'name': 'Корица цейлонская', 'base_price': 580, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 45, 'volatility': 0.12},
            {'name': 'Куркума молотая', 'base_price': 220, 'supplier': 'ООО "Специи Мира"', 'in_stock': 150, 'volatility': 0.06},
            {'name': 'Паприка сладкая', 'base_price': 180, 'supplier': 'ООО "АгроСпеции"', 'in_stock': 200, 'volatility': 0.05},
            {'name': 'Имбирь молотый', 'base_price': 320, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 80, 'volatility': 0.09},
            {'name': 'Кардамон зелёный', 'base_price': 1250, 'supplier': 'ООО "Восток-Специи"', 'in_stock': 25, 'volatility': 0.15},
            {'name': 'Гвоздика', 'base_price': 450, 'supplier': 'ООО "Специи Мира"', 'in_stock': 60, 'volatility': 0.07},
            {'name': 'Мускатный орех', 'base_price': 680, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 35, 'volatility': 0.11},
            {'name': 'Кунжут белый', 'base_price': 150, 'supplier': 'ООО "АгроСпеции"', 'in_stock': 300, 'volatility': 0.04},
            {'name': 'Зира (кумин)', 'base_price': 280, 'supplier': 'ООО "Восток-Специи"', 'in_stock': 90, 'volatility': 0.08},
            {'name': 'Кориандр молотый', 'base_price': 190, 'supplier': 'ООО "Специи Мира"', 'in_stock': 120, 'volatility': 0.05},
            {'name': 'Шафран настоящий', 'base_price': 3500, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 5, 'volatility': 0.2},
            {'name': 'Бадьян (звёздчатый анис)', 'base_price': 520, 'supplier': 'ООО "Восток-Специи"', 'in_stock': 40, 'volatility': 0.1},
            {'name': 'Асафетида', 'base_price': 890, 'supplier': 'ООО "Специи Мира"', 'in_stock': 20, 'volatility': 0.13},
            {'name': 'Фенхель семена', 'base_price': 240, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 110, 'volatility': 0.06},
            {'name': 'Тмин обыкновенный', 'base_price': 210, 'supplier': 'ООО "АгроСпеции"', 'in_stock': 95, 'volatility': 0.07},
            {'name': 'Горчица белая', 'base_price': 120, 'supplier': 'ООО "Специи Мира"', 'in_stock': 250, 'volatility': 0.04},
            {'name': 'Укроп семена', 'base_price': 160, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 180, 'volatility': 0.05},
            {'name': 'Петрушка сушёная', 'base_price': 140, 'supplier': 'ООО "АгроСпеции"', 'in_stock': 200, 'volatility': 0.05},
            {'name': 'Базилик сушёный', 'base_price': 170, 'supplier': 'ООО "Специи Мира"', 'in_stock': 160, 'volatility': 0.06},
            {'name': 'Орегано (душица)', 'base_price': 230, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 85, 'volatility': 0.07},
            {'name': 'Розмарин сушёный', 'base_price': 290, 'supplier': 'ООО "Восток-Специи"', 'in_stock': 70, 'volatility': 0.08},
            {'name': 'Тимьян (чабрец)', 'base_price': 260, 'supplier': 'ООО "Специи Мира"', 'in_stock': 75, 'volatility': 0.07},
            {'name': 'Майоран', 'base_price': 310, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 55, 'volatility': 0.09},
            {'name': 'Ваниль стручки', 'base_price': 2800, 'supplier': 'ООО "Восток-Специи"', 'in_stock': 8, 'volatility': 0.18},
            {'name': 'Перец розовый', 'base_price': 720, 'supplier': 'ООО "Специи Мира"', 'in_stock': 30, 'volatility': 0.12},
            {'name': 'Перец душистый', 'base_price': 430, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 65, 'volatility': 0.08},
            {'name': 'Хмели-сунели', 'base_price': 250, 'supplier': 'ООО "АгроСпеции"', 'in_stock': 130, 'volatility': 0.06},
            {'name': 'Аджика сухая', 'base_price': 200, 'supplier': 'ООО "Специи Мира"', 'in_stock': 140, 'volatility': 0.05},
            {'name': 'Карри', 'base_price': 270, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 120, 'volatility': 0.07},
            {'name': 'Пажитник (шамбала)', 'base_price': 340, 'supplier': 'ООО "Восток-Специи"', 'in_stock': 50, 'volatility': 0.09},
            {'name': 'Чили хлопья', 'base_price': 310, 'supplier': 'ООО "Специи Мира"', 'in_stock': 95, 'volatility': 0.08},
            {'name': 'Суммах', 'base_price': 380, 'supplier': 'ИП "Пряный Двор"', 'in_stock': 45, 'volatility': 0.1},
            {'name': 'Чернушка (нигелла)', 'base_price': 290, 'supplier': 'ООО "АгроСпеции"', 'in_stock': 60, 'volatility': 0.07}
        ]
        
        spices = []
        current_id = 1
        end_date = datetime.now()
        
        for spice_data in base_spices:
            price_history = []
            current_price = spice_data['base_price']
            
            for days_ago in range(365, -1, -1):
                date = (end_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                change = random.uniform(-spice_data['volatility'], spice_data['volatility'])
                current_price = current_price * (1 + change)
                current_price = max(10, round(current_price, 2))
                price_history.append({'date': date, 'price': current_price})
            
            spices.append({
                'id': current_id,
                'name': spice_data['name'],
                'current_price': price_history[-1]['price'],
                'supplier': spice_data['supplier'],
                'in_stock': spice_data['in_stock'],
                'price_history': price_history
            })
            current_id += 1
        
        return spices
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.spices, f, ensure_ascii=False, indent=2)
    
    def get_all_spices(self):
        return self.spices
    
    def get_spice_by_id(self, spice_id):
        for spice in self.spices:
            if spice['id'] == spice_id:
                return spice
        return None
    
    def add_spice(self, name, price, supplier, stock):
        new_id = max([s['id'] for s in self.spices]) + 1 if self.spices else 1
        today = datetime.now().strftime('%Y-%m-%d')
        new_spice = {
            'id': new_id,
            'name': name,
            'current_price': float(price),
            'supplier': supplier,
            'in_stock': int(stock),
            'price_history': [{'date': today, 'price': float(price)}]
        }
        self.spices.append(new_spice)
        self.save_data()
        return new_spice
    
    def update_spice(self, spice_id, name, price, supplier, stock):
        spice = self.get_spice_by_id(spice_id)
        if spice:
            spice['name'] = name
            spice['supplier'] = supplier
            spice['in_stock'] = int(stock)
            if spice['current_price'] != float(price):
                spice['price_history'].append({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'price': float(price)
                })
                spice['current_price'] = float(price)
            self.save_data()
            return True
        return False
    
    def delete_spice(self, spice_id):
        self.spices = [s for s in self.spices if s['id'] != spice_id]
        self.save_data()
    
    def update_prices_randomly(self):
        for spice in self.spices:
            change = random.uniform(-0.1, 0.1)
            new_price = round(max(10, spice['current_price'] * (1 + change)), 2)
            if new_price != spice['current_price']:
                spice['price_history'].append({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'price': new_price
                })
                spice['current_price'] = new_price
        self.save_data()
        return True
    
    def get_price_history_for_period(self, spice_id, period):
        """Получить историю цен за период: week, month, year"""
        spice = self.get_spice_by_id(spice_id)
        if not spice:
            return [], []
        
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:  # year
            start_date = now - timedelta(days=365)
        
        filtered = [h for h in spice['price_history'] 
                   if datetime.strptime(h['date'], '%Y-%m-%d') >= start_date]
        
        dates = [h['date'] for h in filtered]
        prices = [h['price'] for h in filtered]
        
        return dates, prices
    
    def get_statistics(self):
        if not self.spices:
            return {'total_items': 0, 'avg_price': 0, 'min_price': 0, 'max_price': 0, 'total_stock': 0, 'total_value': 0}
        
        prices = [s['current_price'] for s in self.spices]
        total_value = sum(s['current_price'] * s['in_stock'] for s in self.spices)
        
        return {
            'total_items': len(self.spices),
            'avg_price': round(sum(prices) / len(prices), 2),
            'min_price': min(prices),
            'max_price': max(prices),
            'total_stock': sum(s['in_stock'] for s in self.spices),
            'total_value': round(total_value, 2)
        }
        if not os.path.exists(self.user_file):
    self.users = {
        'admin': {
            'password': hashlib.sha256('admin123'.encode()).hexdigest(),
            'name': 'Администратор',
            'role': 'admin'
        },
        'user': {
            'password': hashlib.sha256('user123'.encode()).hexdigest(),
            'name': 'Менеджер',
            'role': 'user'
        }
    }
    self.save_users()
