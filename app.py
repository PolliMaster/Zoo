from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads/avatars'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    avatar = db.Column(db.String(200), default='default.jpg')
    cart_data = db.Column(db.Text, default='[]')  # JSON с данными корзины
    favorites = db.relationship('Favorite', backref='user', lazy=True)

# Модель товара
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=False)

# Модель избранного
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def seed_data():
    db.create_all()
    if not Product.query.first():
        products = [
            Product(name="Игрушка мяч", category="toys", price=200, image="/images/appointment9/мяч.webp"),
            Product(name="Игрушка косточка", category="toys", price=250, image="/images/appointment9/кость.webp"),
            Product(name="Игрушка верёвка", category="toys", price=300, image="/images/appointment9/веревка.jpg"),
            Product(name="Корм для собак", category="food", price=500, image="/images/appointment9/кормдлясобак.webp"),
            Product(name="Корм для кошек", category="food", price=450, image="/images/appointment9/кормдлякошек.jpg"),
            Product(name="Лежак круглый", category="beds", price=1000, image="/images/appointment9/Лежак круглый.jpg"),
            Product(name="Лежак прямоугольный", category="beds", price=1200, image="/images/appointment9/Лежак прямоугольный.jpg"),
            Product(name="Куртка для собак", category="clothing", price=800, image="/images/appointment9/Куртка для собак.webp"),
            Product(name="Пальто для кошек", category="clothing", price=850, image="/images/appointment9/Пальто для кошек.jpg"),
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()

@app.route('/category')
def index():
    category = request.args.get('category')
    products = Product.query.filter_by(category=category).all() if category else Product.query.all()
    return render_template('appointment.html', products=products)

@app.route('/checkout')
def checkout():
    return "Оформление заказа (заглушка)"

# Модель для записи данных о бронированиях
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)

# Модель для хранения почтовых адресов пользователей
class Mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(50), nullable=False)
    check_in = db.Column(db.String(50), nullable=False)
    check_out = db.Column(db.String(50), nullable=False)
    pet_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)

@app.route('/book_room', methods=['POST'])
def book_room():
    try:
        room_type = request.form.get('roomType')
        check_in = request.form.get('checkIn')
        check_out = request.form.get('checkOut')
        pet_name = request.form.get('petName')
        owner_name = request.form.get('ownerName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        notes = request.form.get('notes', '')

        # Проверка на заполненность всех обязательных полей
        if not all([room_type, check_in, check_out, pet_name, owner_name, email, phone]):
            return "Ошибка: Все поля, кроме 'Дополнительные замечания', обязательны!", 400

        # Создание нового бронирования
        new_booking = Booking(
            room_type=room_type,
            check_in=check_in,
            check_out=check_out,
            pet_name=pet_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            notes=notes
        )
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('rooms'))  # Перенаправление на страницу rooms

    except Exception as e:
        print(f"Ошибка при сохранении данных в базе: {e}")
        return "Ошибка при сохранении данных в базе", 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/blago')
def blago():
    return render_template('blago.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/appointment')
def appointment():
    categories = request.args.getlist('category')  # Поддержка нескольких категорий
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Product.query
    if categories:
        query = query.filter(Product.category.in_(categories))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.all()
    return render_template('appointment.html', products=products)

@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    data = request.get_json()
    product_id = int(data['product_id'])
    favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'success': True, 'action': 'removed'})
    else:
        new_favorite = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'success': True, 'action': 'added'})

@app.route('/save_cart', methods=['POST'])
@login_required
def save_cart():
    data = request.get_json()
    cart = data['cart']
    current_user.cart_data = json.dumps(cart)  # Сохраняем корзину как JSON
    db.session.commit()
    return jsonify({'success': True})

@app.route('/save_favorites', methods=['POST'])
@login_required
def save_favorites():
    data = request.get_json()
    favorites = data['favorites']
    # Удаляем старые записи избранного
    Favorite.query.filter_by(user_id=current_user.id).delete()
    # Добавляем новые
    for product_id in favorites:
        new_favorite = Favorite(user_id=current_user.id, product_id=int(product_id))
        db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/grooming', methods=['GET', 'POST'])
def grooming():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        service = request.form['service']
        date = request.form['date']
        new_appointment = Appointment(name=name, phone=phone, service=service, date=date)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('grooming'))
    appointments = Appointment.query.all()
    return render_template('grooming.html', appointments=appointments)

@app.route('/info')
def info():
    return render_template('info.html')

# Обработка формы подписки на рассылку
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    if email:
        new_email = Mail(email=email)
        db.session.add(new_email)
        db.session.commit()
        return redirect(url_for('home'))  # перенаправление на главную страницу
    return redirect(url_for('home'))  # если почта не введена, просто возвращаемся

# Регистрация через AJAX
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone = data.get('phone')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email уже зарегистрирован'}), 400

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        phone=phone
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({'success': 'Регистрация успешна', 'redirect': url_for('profile')})

# Вход через AJAX
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'success': 'Вход успешен', 'redirect': url_for('profile')})
    return jsonify({'error': 'Неверный email или пароль'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Страница профиля
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar = filename
                db.session.commit()
                flash('Аватар успешно обновлен!')
        elif 'full_name' in request.form:
            current_user.full_name = request.form['full_name']
            current_user.phone = request.form['phone']
            db.session.commit()
            flash('Данные профиля обновлены!')
        return redirect(url_for('profile'))
    avatars = os.listdir(app.config['UPLOAD_FOLDER'])  # Список доступных аватаров
    return render_template('profile.html', avatars=avatars)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)