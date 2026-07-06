from app import app, db, Product

with app.app_context():
    db.session.add(Product(name="Cotton t-shirt", price=19.99, emoji="👕"))
    db.session.add(Product(name="Wireless headphones", price=59.99, emoji="🎧"))
    db.session.add(Product(name="Running shoes", price=74.50, emoji="👟"))
    db.session.add(Product(name="Smart watch", price=129.00, emoji="⌚"))
    db.session.commit()
    print("Products added successfully!")