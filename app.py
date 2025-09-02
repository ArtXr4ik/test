from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'XR4K-XR4K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///telegram_acc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

# Модель отзыва
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=True)

# Модель просмотров товаров
class ProductView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Данные товаров
PRODUCTS = [
    {
        'id': 1,
        'name': 'Аккаунт Telegram Мьянма(+95)',
        'price': '45руб',
        'original_price': '50руб',
        'sale': '10%',
        'available': True,
        'description': 'Премиум аккаунт с номером Мьянмы'
    },
    {
        'id': 2,
        'name': 'Аккаунт Telegram Бангладеш(+880)',
        'price': '50руб',
        'original_price': '',
        'sale': '',
        'available': True,
        'description': 'Качественный аккаунт с бангладешским номером'
    },
    {
        'id': 3,
        'name': 'Аккаунт Telegram США(вирт)(+1)',
        'price': '50руб',
        'original_price': '',
        'sale': '',
        'available': True,
        'description': 'Виртуальный номер США для Telegram'
    },
    {
        'id': 4,
        'name': 'Аккаунт Telegram Нигерия(+234)',
        'price': '55руб',
        'original_price': '',
        'sale': '',
        'available': True,
        'description': 'Надежный аккаунт с нигерийским номером'
    },
    {
        'id': 5,
        'name': 'Аккаунт Telegram Зимбабве(+263)',
        'price': '50руб',
        'original_price': '',
        'sale': '',
        'available': False,
        'description': 'Эксклюзивный аккаунт (скоро в наличии)'
    }
]

def init_db():
    with app.app_context():
        db.create_all()

def validate_user_email(email):
    try:
        valid = validate_email(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    search_query = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'name')
    
    # Фильтрация и сортировка товаров
    filtered_products = PRODUCTS.copy()
    
    if search_query:
        filtered_products = [p for p in filtered_products if search_query in p['name'].lower()]
    
    if sort_by == 'price':
        filtered_products.sort(key=lambda x: int(x['price'].replace('руб', '')))
    elif sort_by == 'name':
        filtered_products.sort(key=lambda x: x['name'])
    
    # Получаем просмотры для каждого товара
    for product in filtered_products:
        views_count = ProductView.query.filter_by(product_id=product['id']).count()
        product['views'] = views_count
    
    # Получаем последние отзывы
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         products=filtered_products,
                         reviews=reviews,
                         search_query=request.args.get('search', ''),
                         sort_by=sort_by)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Валидация
        errors = []
        if not email or not password or not confirm_password:
            errors.append('Все поля обязательны для заполнения')
        
        if password != confirm_password:
            errors.append('Пароли не совпадают')
        
        if len(password) < 6:
            errors.append('Пароль должен содержать минимум 6 символов')
        
        is_valid_email, email_error = validate_user_email(email)
        if not is_valid_email:
            errors.append(f'Неверный формат email: {email_error}')
        
        if User.query.filter_by(email=email).first():
            errors.append('Пользователь с таким email уже существует')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        try:
            user = User(email=email)
            user.password_hash = generate_password_hash(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации. Попробуйте позже.', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Неверный email или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/api/track_view/<int:product_id>')
@login_required
def track_view(product_id):
    try:
        # Проверяем существование товара
        product = next((p for p in PRODUCTS if p['id'] == product_id), None)
        if not product:
            return jsonify({'error': 'Товар не найден'}), 404
        
        # Сохраняем просмотр
        view = ProductView(
            product_id=product_id,
            user_id=current_user.id,
            ip_address=request.remote_addr
        )
        db.session.add(view)
        db.session.commit()
        
        # Получаем общее количество просмотров
        views_count = ProductView.query.filter_by(product_id=product_id).count()
        
        return jsonify({
            'success': True,
            'views': views_count,
            'product_id': product_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_review', methods=['POST'])
@login_required
def add_review():
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        rating = data.get('rating', 0)
        product_id = data.get('product_id', 0)
        
        # Валидация
        if not content or not rating or not product_id:
            return jsonify({'error': 'Все поля обязательны'}), 400
        
        if len(content) < 10:
            return jsonify({'error': 'Отзыв должен содержать минимум 10 символов'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Рейтинг должен быть от 1 до 5'}), 400
        
        # Проверяем существование товара
        product = next((p for p in PRODUCTS if p['id'] == product_id), None)
        if not product:
            return jsonify({'error': 'Товар не найден'}), 404
        
        # Создаем отзыв
        review = Review(
            content=content,
            rating=rating,
            product_id=product_id,
            user_id=current_user.id
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'review': {
                'id': review.id,
                'content': content,
                'rating': rating,
                'user_email': current_user.email,
                'created_at': review.created_at.strftime('%d.%m.%Y %H:%M'),
                'product_name': product['name']
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка сервера'}), 500

@app.route('/api/product_stats')
@login_required
def product_stats():
    stats = {}
    for product in PRODUCTS:
        views = ProductView.query.filter_by(product_id=product['id']).count()
        reviews = Review.query.filter_by(product_id=product['id'], is_approved=True).count()
        avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(
            product_id=product['id'], is_approved=True
        ).scalar() or 0
        
        stats[product['id']] = {
            'views': views,
            'reviews': reviews,
            'avg_rating': round(float(avg_rating), 1)
        }
    
    return jsonify(stats)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5555)