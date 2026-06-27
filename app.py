import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Product, Review, Cart, CartItem, Order, OrderItem, Wishlist
from models import Supplier, Purchase, PurchaseItem, StockMovement

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico', '.tiff', '.avif'}


def get_available_images():
    image_dir = os.path.join(app.static_folder, 'images')
    images = []
    try:
        for f in sorted(os.listdir(image_dir)):
            ext = os.path.splitext(f)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                images.append(f)
    except FileNotFoundError:
        pass
    return images


def image_exists(filename):
    if not filename:
        return False
    return os.path.isfile(os.path.join(app.static_folder, 'images', filename))


def humanize_filename(filename):
    name = os.path.splitext(filename)[0]
    name = name.replace('_', ' ').replace('-', ' ')
    return ' '.join(w.capitalize() for w in name.split())


def sync_images_to_products():
    images = get_available_images()
    existing = {p.image for p in Product.query.all()}
    count = 0
    for img in images:
        if ' - copy' in img.lower():
            continue
        if img in existing:
            continue
        product = Product(
            name=humanize_filename(img),
            description=f"Auto-created from {img}. Edit this product to add full details.",
            category='men',
            price=49.99,
            cost_price=0,
            rating=4.0,
            image=img,
            sizes='[]',
            colors='[]',
            stock=10,
            featured=False,
        )
        db.session.add(product)
        db.session.flush()
        db.session.add(
            StockMovement(
                product_id=product.id,
                quantity=product.stock,
                movement_type='initial',
                notes=f'Auto-created from image: {img}',
            )
        )
        existing.add(img)
        count += 1
    if count:
        db.session.commit()
    return count


# ─── Flask App Configuration ─────────────────────────────────────────
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "change-this-secret"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///solestyle.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

BDT_RATE = 120


def format_bdt(usd_amount):
    return f"BDT {usd_amount * BDT_RATE:,.0f}"


def format_dual(usd_amount):
    return f"{format_bdt(usd_amount)} / ${usd_amount:.2f}"


app.jinja_env.filters['bdt'] = format_bdt
app.jinja_env.filters['dual'] = format_dual

# ─── Database & Auth Setup ───────────────────────────────────────────
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_globals():
    count = 0
    if current_user.is_authenticated:
        cart = current_user.cart
        if cart:
            count = sum(item.quantity for item in cart.items.all())
    return {
        'cart_count': count,
        'categories': ['men', 'women', 'kids'],
        'available_images': get_available_images(),
        'image_exists': image_exists,
        'bdt_rate': BDT_RATE,
    }


# ─── Home ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    products = Product.query.order_by(Product.created_at.desc()).all()
    featured = Product.query.filter_by(featured=True).all()
    return render_template('index.html', products=products, featured=featured)


@app.route('/search')
def search():
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 500, type=float)
    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
    if category:
        query = query.filter_by(category=category)
    query = query.filter(Product.price >= min_price, Product.price <= max_price)
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    products = query.all()
    return render_template('search.html', products=products, q=q, category=category, sort=sort)


# ─── Product Detail ──────────────────────────────────────────────────
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = product.reviews.order_by(Review.created_at.desc()).all()
    related = (
        Product.query.filter(Product.category == product.category, Product.id != product.id)
        .limit(4)
        .all()
    )
    return render_template('product.html', product=product, reviews=reviews, related=related)


@app.route('/api/product/<int:product_id>/reviews')
def product_reviews(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = [
        {
            'id': r.id,
            'rating': r.rating,
            'comment': r.comment,
            'user': r.user.username,
            'date': r.created_at.strftime('%b %d, %Y'),
        }
        for r in product.reviews.order_by(Review.created_at.desc()).all()
    ]
    return jsonify(reviews)


@app.route('/api/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    if not data or 'rating' not in data:
        return jsonify({'error': 'Missing rating'}), 400
    existing = Review.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    if existing:
        return jsonify({'error': 'You already reviewed this product'}), 400
    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=rating,
        comment=data.get('comment', ''),
    )
    db.session.add(review)
    avg = db.session.query(db.func.avg(Review.rating)).filter_by(product_id=product_id).scalar()
    product.rating = round(avg, 1) if avg else rating
    db.session.commit()
    return jsonify({'message': 'Review added'})


# ─── Auth ────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.flush()
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ─── Cart ────────────────────────────────────────────────────────────
@app.route('/cart')
@login_required
def view_cart():
    cart = current_user.cart
    items = cart.items.all() if cart else []
    return render_template('cart.html', items=items)


@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    size = data.get('size', '')
    color = data.get('color', '')

    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock'}), 400

    cart = current_user.cart
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.flush()

    existing = CartItem.query.filter_by(
        cart_id=cart.id, product_id=product_id, size=size, color=color
    ).first()
    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart.id, product_id=product_id, quantity=quantity, size=size, color=color
        )
        db.session.add(item)

    db.session.commit()
    count = sum(item.quantity for item in cart.items.all())
    return jsonify({'message': 'Added to cart', 'cart_count': count})


@app.route('/api/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(item)
    db.session.commit()
    count = sum(i.quantity for i in current_user.cart.items.all())
    return jsonify({'message': 'Removed from cart', 'cart_count': count})


@app.route('/api/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    quantity = data.get('quantity', 1)
    if quantity <= 0:
        db.session.delete(item)
    else:
        if item.product.stock < quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        item.quantity = quantity
    db.session.commit()
    count = sum(i.quantity for i in current_user.cart.items.all())
    return jsonify({'message': 'Updated cart', 'cart_count': count})


# ─── Wishlist ────────────────────────────────────────────────────────
@app.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    products = [item.product for item in items]
    return render_template('wishlist.html', products=products)


@app.route('/api/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        return jsonify({'message': 'Already in wishlist'}), 200
    item = Wishlist(user_id=current_user.id, product_id=product_id)
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Added to wishlist'})


@app.route('/api/wishlist/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Removed from wishlist'})


# ─── Orders ──────────────────────────────────────────────────────────
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = current_user.cart
    items = cart.items.all() if cart else []
    if not items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('view_cart'))
    
    if request.method == 'POST':
        total = sum(item.product.price * item.quantity for item in items)
        order = Order(
            user_id=current_user.id,
            total=total,
            status='pending',
            payment_method=request.form.get('payment_method', 'card'),
            payment_number=request.form.get('payment_number', ''),
            shipping_name=request.form.get('shipping_name'),
            shipping_email=request.form.get('shipping_email'),
            shipping_address=request.form.get('shipping_address'),
            shipping_city=request.form.get('shipping_city'),
            shipping_zip=request.form.get('shipping_zip'),
        )
        db.session.add(order)
        db.session.flush()
        
        for item in items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price,
                size=item.size,
                color=item.color,
            ))
            item.product.stock -= item.quantity
            db.session.add(StockMovement(
                product_id=item.product_id,
                quantity=-item.quantity,
                movement_type='sale',
                reference_type='order',
                reference_id=order.id,
                notes=f"Order {order.id}: {item.product.name}",
            ))
        
        db.session.delete(cart)
        new_cart = Cart(user_id=current_user.id)
        db.session.add(new_cart)
        db.session.commit()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_detail', order_id=order.id))
    
    return render_template('checkout.html', items=items)


@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized', 'error')
        return redirect(url_for('index'))
    return render_template('order_detail.html', order=order)


# ─── Admin ───────────────────────────────────────────────────────────
def admin_required(f):
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated


@app.route('/admin')
@admin_required
def admin_dashboard():
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    revenue = db.session.query(db.func.sum(Order.total)).filter(Order.status != 'cancelled').scalar() or 0
    month_revenue = (
        db.session.query(db.func.sum(Order.total))
        .filter(Order.status != 'cancelled', Order.created_at >= month_start)
        .scalar()
        or 0
    )
    total_cost = db.session.query(db.func.sum(PurchaseItem.quantity * PurchaseItem.unit_cost)).scalar() or 0
    cogs = (
        db.session.query(db.func.sum(OrderItem.quantity * db.func.coalesce(Product.cost_price, 0)))
        .join(Product, OrderItem.product_id == Product.id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status != 'cancelled')
        .scalar()
        or 0
    )
    profit = revenue - cogs
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock <= 5).count()
    return render_template(
        'admin/dashboard.html',
        total_products=total_products,
        total_orders=total_orders,
        total_users=total_users,
        revenue=round(revenue, 2),
        month_revenue=round(month_revenue, 2),
        total_cost=round(total_cost, 2),
        cogs=round(cogs, 2),
        profit=round(profit, 2),
        recent_orders=recent_orders,
        low_stock=low_stock,
    )


# ─── Initialize Database ─────────────────────────────────────────────
def seed_db():
    if Product.query.count() > 0:
        return

    products_data = [
        {
            'name': 'Air Max Pro',
            'category': 'men',
            'price': 129.99,
            'cost_price': 65.0,
            'rating': 4.5,
            'image': 'shoe1.png',
            'featured': True,
            'stock': 25,
            'sizes': json.dumps(['7', '8', '9', '10', '11', '12']),
            'colors': json.dumps(['Black', 'Blue', 'Red']),
        },
        {
            'name': 'Urban Runner',
            'category': 'men',
            'price': 99.99,
            'cost_price': 48.0,
            'rating': 4.2,
            'image': 'shoe2.png',
            'featured': True,
            'stock': 30,
            'sizes': json.dumps(['7', '8', '9', '10', '11', '12']),
            'colors': json.dumps(['Red', 'White', 'Gray']),
        },
        {
            'name': 'Classic Leather',
            'category': 'men',
            'price': 149.99,
            'cost_price': 82.0,
            'rating': 4.7,
            'image': 'shoe3.png',
            'featured': True,
            'stock': 15,
            'sizes': json.dumps(['8', '9', '10', '11', '12', '13']),
            'colors': json.dumps(['Brown', 'Black', 'Tan']),
        },
        {
            'name': 'Trail Blazer',
            'category': 'men',
            'price': 119.99,
            'cost_price': 55.0,
            'rating': 4.3,
            'image': 'shoe4.png',
            'featured': False,
            'stock': 20,
            'sizes': json.dumps(['7', '8', '9', '10', '11']),
            'colors': json.dumps(['Green', 'Black', 'Orange']),
        },
        {
            'name': 'Elegance Heel',
            'category': 'women',
            'price': 89.99,
            'cost_price': 38.0,
            'rating': 4.6,
            'image': 'shoe5.png',
            'featured': True,
            'stock': 35,
            'sizes': json.dumps(['5', '6', '7', '8', '9', '10']),
            'colors': json.dumps(['Pink', 'Red', 'Black']),
        },
        {
            'name': 'Floral Sneak',
            'category': 'women',
            'price': 79.99,
            'cost_price': 32.0,
            'rating': 4.4,
            'image': 'shoe6.png',
            'featured': True,
            'stock': 28,
            'sizes': json.dumps(['5', '6', '7', '8', '9']),
            'colors': json.dumps(['Purple', 'White', 'Blue']),
        },
        {
            'name': 'Grace Sandal',
            'category': 'women',
            'price': 59.99,
            'cost_price': 22.0,
            'rating': 4.1,
            'image': 'shoe7.png',
            'featured': False,
            'stock': 40,
            'sizes': json.dumps(['5', '6', '7', '8', '9', '10']),
            'colors': json.dumps(['Orange', 'Gold', 'White']),
        },
        {
            'name': 'Diva Boot',
            'category': 'women',
            'price': 139.99,
            'cost_price': 72.0,
            'rating': 4.8,
            'image': 'shoe8.png',
            'featured': True,
            'stock': 18,
            'sizes': json.dumps(['6', '7', '8', '9', '10']),
            'colors': json.dumps(['Blue', 'Black', 'Gray']),
        },
        {
            'name': 'Tiny Star',
            'category': 'kids',
            'price': 49.99,
            'cost_price': 18.0,
            'rating': 4.5,
            'image': 'shoe9.png',
            'featured': True,
            'stock': 45,
            'sizes': json.dumps(['10', '11', '12', '13', '1', '2', '3']),
            'colors': json.dumps(['Cyan', 'Blue', 'Green']),
        },
        {
            'name': 'Jump Sprint',
            'category': 'kids',
            'price': 44.99,
            'cost_price': 16.0,
            'rating': 4.3,
            'image': 'shoe10.png',
            'featured': False,
            'stock': 50,
            'sizes': json.dumps(['10', '11', '12', '13', '1', '2']),
            'colors': json.dumps(['Orange', 'Red', 'Yellow']),
        },
        {
            'name': 'Rainbow Step',
            'category': 'kids',
            'price': 39.99,
            'cost_price': 14.0,
            'rating': 4.6,
            'image': 'shoe11.png',
            'featured': False,
            'stock': 30,
            'sizes': json.dumps(['9', '10', '11', '12', '13', '1']),
            'colors': json.dumps(['Green', 'Rainbow', 'Blue']),
        },
        {
            'name': 'Sport Junior',
            'category': 'kids',
            'price': 54.99,
            'cost_price': 22.0,
            'rating': 4.4,
            'image': 'shoe12.png',
            'featured': True,
            'stock': 35,
            'sizes': json.dumps(['10', '11', '12', '13', '1', '2', '3']),
            'colors': json.dumps(['Gray', 'Blue', 'Red']),
        },
    ]

    for pd in products_data:
        desc = f"Premium {pd['category']}'s {pd['name']} shoe. Comfortable, durable, and stylish. Perfect for everyday wear."
        product = Product(**pd, description=desc)
        db.session.add(product)
        db.session.flush()
        db.session.add(
            StockMovement(
                product_id=product.id,
                quantity=product.stock,
                movement_type='initial',
                notes='Initial stock',
            )
        )

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@solestyle.com',
            password_hash=generate_password_hash('admin'),
            is_admin=True,
        )
        db.session.add(admin)

    if not User.query.filter_by(username='demo').first():
        demo = User(
            username='demo',
            email='demo@example.com',
            password_hash=generate_password_hash('demo123'),
        )
        db.session.add(demo)

    db.session.commit()
    print('Database seeded!')


# ─── App Initialization ──────────────────────────────────────────────
with app.app_context():
    db.create_all()
    seed_db()
    created = sync_images_to_products()
    if created:
        print(f'Synced {created} new product(s) from images/')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
