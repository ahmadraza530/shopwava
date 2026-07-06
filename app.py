import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-later")
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    emoji = db.Column(db.String(10), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_emoji = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)


@app.route("/product/<int:id>")
def product_details(id):
    product = Product.query.get_or_404(id)
    return render_template("product.html", product=product)


@app.route("/add-to-cart/<int:id>", methods=["POST"])
def add_to_cart(id):
    cart = session.get("cart", {})
    id_str = str(id)
    cart[id_str] = cart.get(id_str, 0) + 1
    session["cart"] = cart
    return redirect(url_for("home"))


@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    cart_items = []
    total = 0
    for id_str, quantity in cart.items():
        product = Product.query.get(int(id_str))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })
    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart = session.get("cart", {})
    if not cart:
        return redirect(url_for("view_cart"))

    total = 0
    order_items_data = []
    for id_str, quantity in cart.items():
        product = Product.query.get(int(id_str))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            order_items_data.append((product, quantity))

    new_order = Order(user_id=current_user.id, total=total)
    db.session.add(new_order)
    db.session.commit()

    for product, quantity in order_items_data:
        item = OrderItem(
            order_id=new_order.id,
            product_name=product.name,
            product_emoji=product.emoji,
            price=product.price,
            quantity=quantity
        )
        db.session.add(item)
    db.session.commit()

    session["cart"] = {}
    return redirect(url_for("order_confirmation", order_id=new_order.id))


@app.route("/order-confirmation/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("order_confirmation.html", order=order)


@app.route("/orders")
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("orders.html", orders=orders)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("That username is already taken.")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)