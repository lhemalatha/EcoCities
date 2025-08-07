from flask import Flask, render_template_string, request, jsonify, session, redirect
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ecoshop_secret_key_2025'

# Database setup
def init_db():
    conn = sqlite3.connect('ecoshop_orders.db')
    cursor = conn.cursor()
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT NOT NULL,
            customer_email TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    
        # Create reused_items table for EcoReuse Exchange
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reused_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            condition TEXT,
            owner_email TEXT,
            status TEXT DEFAULT 'Available',
            posted_at TEXT
        )
    ''')
    # Create eco_tips table for blog
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eco_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            posted_at TEXT

        )
    ''')
    # Create green_points table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS green_points (
            email TEXT PRIMARY KEY,
            points INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ---------- Green Points helpers ----------

def award_points(email: str, delta: int):
    if not email:
        return
    conn = sqlite3.connect('ecoshop_orders.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO green_points (email, points) VALUES (?, ?)
                   ON CONFLICT(email) DO UPDATE SET points = points + ?''',
                (email, delta, delta))
    conn.commit(); conn.close()


def get_points(email: str) -> int:
    conn = sqlite3.connect('ecoshop_orders.db'); cur = conn.cursor()
    cur.execute('SELECT points FROM green_points WHERE email=?', (email,))
    row = cur.fetchone(); conn.close()
    return row[0] if row else 0


def tier_discount(points: int):
    if points < 20:
        return 0.0, 'No discount yet'
    if points < 51:
        return 0.05, '5% off next order'
    if points < 100:
        return 0.10, '10% off / $50 NGO donation'
    if points < 300:
        return 0.15, '15% off + eco-gift'
    return 0.20, '20% off + 🌱 badge'

# Product data with enhanced features
products = [
    {'id': 1, 'name': 'Eco-Friendly Water Bottle', 'price': 25.99, 'image': '🍃', 'description': 'Sustainable stainless steel water bottle', 'category': 'Drinkware', 'stock': 50},
    {'id': 2, 'name': 'Organic Cotton T-Shirt', 'price': 35.00, 'image': '👕', 'description': 'Super soft organic cotton t-shirt', 'category': 'Clothing', 'stock': 30},
    {'id': 3, 'name': 'Bamboo Phone Case', 'price': 18.50, 'image': '📱', 'description': 'Stylish bamboo phone case', 'category': 'Accessories', 'stock': 25},
    {'id': 4, 'name': 'Solar Power Bank', 'price': 45.00, 'image': '🔋', 'description': 'Portable solar charging device', 'category': 'Electronics', 'stock': 15},
    {'id': 5, 'name': 'Refillable Soap Dispenser', 'price': 22.99, 'image': '🧴', 'description': 'Glass soap dispenser with refills', 'category': 'Home', 'stock': 40},
    {'id': 6, 'name': 'Plant-Based Cleaning Kit', 'price': 39.99, 'image': '🌱', 'description': 'Non-toxic cleaning products', 'category': 'Home', 'stock': 20},
    {'id': 7, 'name': 'Reusable Coffee Cup', 'price': 19.99, 'image': '☕', 'description': 'Insulated bamboo fiber coffee cup with silicone lid', 'category': 'Drinkware', 'stock': 35},
    {'id': 8, 'name': 'Organic Hemp Backpack', 'price': 65.00, 'image': '🎒', 'description': 'Durable hemp backpack with laptop compartment', 'category': 'Accessories', 'stock': 18},
    {'id': 9, 'name': 'LED Solar Garden Lights', 'price': 32.50, 'image': '💡', 'description': 'Weather-resistant solar-powered garden lighting set', 'category': 'Electronics', 'stock': 28},
    {'id': 10, 'name': 'Organic Cotton Bed Sheets', 'price': 89.99, 'image': '🛏️', 'description': 'Luxurious organic cotton bed sheet set', 'category': 'Home', 'stock': 12},
    {'id': 11, 'name': 'Recycled Plastic Yoga Mat', 'price': 42.00, 'image': '🧘', 'description': 'Non-slip yoga mat made from recycled ocean plastic', 'category': 'Fitness', 'stock': 22},
    {'id': 12, 'name': 'Beeswax Food Wraps', 'price': 16.75, 'image': '🐝', 'description': 'Reusable beeswax wraps for food storage', 'category': 'Kitchen', 'stock': 45},
    {'id': 13, 'name': 'Recycled Plastic Bricks', 'price': 120.00, 'image': '🧱', 'description': 'Durable construction bricks made from recycled plastic waste', 'category': 'Construction', 'stock': 80},
    {'id': 14, 'name': 'Upcycled Rubber Tiles', 'price': 45.00, 'image': '🟫', 'description': 'Shock-absorbing floor tiles from discarded rubber', 'category': 'Flooring', 'stock': 60},
    {'id': 15, 'name': 'Eco-Friendly Helmet', 'price': 79.99, 'image': '🪖', 'description': 'Lightweight bike helmet crafted from recycled polymers', 'category': 'Safety', 'stock': 25}
]

@app.route('/')
def home():
    if 'cart' not in session:
        session['cart'] = []
    cart_count = len(session['cart'])
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>EcoCities - Enhanced Shopping Experience</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #e8f5e8, #f0f8f0); }
        
        .navbar { background: linear-gradient(135deg, #2e7d32, #4caf50); color: white; padding: 1rem 0; position: sticky; top: 0; z-index: 1000; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
        .logo { font-size: 2rem; font-weight: bold; text-decoration: none; color: white; }
        .nav-links { display: flex; gap: 2rem; align-items: center; }
        .nav-link { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 20px; transition: background 0.3s; }
        .nav-link:hover { background: rgba(255,255,255,0.2); }
        
        .cart-icon { position: relative; background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 50%; cursor: pointer; transition: all 0.3s; }
        .cart-icon:hover { background: rgba(255,255,255,0.3); transform: scale(1.1); }
        .cart-count { position: absolute; top: -5px; right: -5px; background: #ff5722; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; }
        
        .header { background: linear-gradient(135deg, #2e7d32, #4caf50); color: white; padding: 3rem 0; text-align: center; }
        .header h1 { font-size: 3.5rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.3rem; opacity: 0.9; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        .search-bar { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 2rem 0; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
        .search-input { flex: 1; min-width: 250px; padding: 1rem; font-size: 1.1rem; border: 2px solid #4caf50; border-radius: 25px; outline: none; }
        .filter-select { padding: 1rem; font-size: 1rem; border: 2px solid #4caf50; border-radius: 25px; outline: none; background: white; }
        .search-btn { padding: 1rem 2rem; background: #4caf50; color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 1.1rem; transition: all 0.3s; }
        .search-btn:hover { background: #388e3c; transform: translateY(-2px); }
        
        .products { margin: 4rem 0; }
        .products h2 { text-align: center; font-size: 2.5rem; color: #2e7d32; margin-bottom: 3rem; }
        .product-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        
        .product-card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-8px); }
        .product-image { height: 200px; background: linear-gradient(45deg, #81c784, #a5d6a7); display: flex; align-items: center; justify-content: center; font-size: 4rem; color: white; position: relative; }
        .stock-badge { position: absolute; top: 10px; right: 10px; background: #4caf50; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
        .low-stock { background: #ff9800; }
        
        .product-info { padding: 1.5rem; }
        .product-title { font-size: 1.3rem; font-weight: bold; color: #2e7d32; margin-bottom: 0.5rem; }
        .product-price { font-size: 1.5rem; font-weight: bold; color: #4caf50; margin: 1rem 0; }
        .product-description { color: #666; margin-bottom: 1rem; font-size: 0.9rem; }
        .product-category { display: inline-block; background: #e8f5e8; color: #2e7d32; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-bottom: 1rem; }
        
        .btn { background: linear-gradient(135deg, #4caf50, #66bb6a); color: white; padding: 0.8rem 2rem; border: none; border-radius: 25px; cursor: pointer; font-size: 1rem; transition: all 0.3s; width: 100%; text-align: center; }
        .btn:hover { background: linear-gradient(135deg, #388e3c, #4caf50); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        
        /* Cart Modal */
        .modal { display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: white; margin: 5% auto; padding: 2rem; border-radius: 15px; width: 90%; max-width: 600px; max-height: 80vh; overflow-y: auto; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: #000; }
        .cart-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #eee; }
        .cart-total { font-size: 1.5rem; font-weight: bold; color: #2e7d32; text-align: right; margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #4caf50; }
        .quantity-controls { display: flex; align-items: center; gap: 0.5rem; }
        .quantity-btn { background: #4caf50; color: white; border: none; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; }
        .checkout-btn { background: linear-gradient(135deg, #ff9800, #ffa726); color: white; padding: 1rem 2rem; border: none; border-radius: 25px; cursor: pointer; font-size: 1.1rem; width: 100%; margin-top: 1rem; }
        
        .footer { background: #2e7d32; color: white; text-align: center; padding: 2rem 0; margin-top: 4rem; }
        
        @media (max-width: 768px) {
            .nav-container { flex-direction: column; gap: 1rem; }
            .search-bar { flex-direction: column; }
            .search-input { min-width: 100%; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">🌱 EcoCities</a>
            <div class="nav-links">
                <a href="/" class="nav-link">Home</a>
                <a href="/products" class="nav-link">Products</a>
                <a href="/admin" class="nav-link">📊 Orders</a>
                <a href="/about" class="nav-link">About</a>
                    <a href="/exchange" class="nav-link">EcoReuse</a>
                    <a href="/blog" class="nav-link">Eco Tips</a>
                    <a href="/points" class="nav-link">Green Points</a>
                <div class="cart-icon" onclick="openCart()">
                    🛒
                    <span class="cart-count" id="cartCount">{{ cart_count }}</span>
                </div>
            </div>
        </div>
    </nav>
    
    <header class="header">
        <h1>🌱 EcoCities</h1>
        <p>Your Enhanced Sustainable Shopping Experience</p>
    </header>
    
    <div class="container">
        <div class="search-bar">
            <input type="text" class="search-input" id="searchInput" placeholder="Search eco-friendly products...">
            <select class="filter-select" id="categoryFilter">
                <option value="">All Categories</option>
                <option value="Drinkware">Drinkware</option>
                <option value="Clothing">Clothing</option>
                <option value="Accessories">Accessories</option>
                <option value="Electronics">Electronics</option>
                <option value="Home">Home</option>
                <option value="Fitness">Fitness</option>
                <option value="Kitchen">Kitchen</option>
                <option value="Construction">Construction</option>
                <option value="Flooring">Flooring</option>
                <option value="Safety">Safety</option>
            </select>
            <button class="search-btn" onclick="filterProducts()">🔍 Search</button>
        </div>
        
        <section class="products">
            <h2>Featured Sustainable Products</h2>
            <div class="product-grid" id="productGrid">
                {% for product in products %}
                <div class="product-card" data-category="{{ product.category }}" data-name="{{ product.name.lower() }}">
                    <div class="product-image">
                        {{ product.image }}
                        <span class="stock-badge {% if product.stock < 10 %}low-stock{% endif %}">
                            {{ product.stock }} left
                        </span>
                    </div>
                    <div class="product-info">
                        <div class="product-category">{{ product.category }}</div>
                        <div class="product-title">{{ product.name }}</div>
                        <div class="product-price">${{ "%.2f"|format(product.price) }}</div>
                        <div class="product-description">{{ product.description }}</div>
                        <button class="btn" onclick="addToCart({{ product.id }}, '{{ product.name }}', {{ product.price }}, '{{ product.image }}')">
                            Add to Cart 🛒
                        </button>
                        <button class="btn" style="margin-top:0.5rem;background:linear-gradient(135deg,#2196f3,#42a5f5);" onclick="showJourney({{ product.id }})">Sustainability Journey 🌍</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
    </div>
    
    <!-- Cart Modal -->
    <div id="cartModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeCart()">&times;</span>
            <h2>🛒 Your Shopping Cart</h2>
            <div id="cartItems"></div>
            <div class="cart-total" id="cartTotal">Total: $0.00</div>
            <button class="checkout-btn" onclick="checkout()">🚀 Proceed to Checkout</button>
        </div>
    </div>
    
    <!-- Sustainability Modal -->
    <div id="journeyModal" class="modal">
        <div class="modal-content" style="max-width:500px;">
            <span class="close" onclick="closeJourney()">&times;</span>
            <h2>🌍 Sustainability Journey</h2>
            <p><strong>Source:</strong> <span id="journeySource"></span></p>
            <p><strong>Manufacturing:</strong> <span id="journeyMade"></span></p>
            <p><strong>End-of-Life:</strong> <span id="journeyEnd"></span></p>
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2025 EcoCities - Enhanced Shopping Experience 🌍</p>
        <p>Contact: hello@ecoshop.com | 1-800-ECO-SHOP</p>
    </footer>
    
    <script>
        let cart = [];
        // Sustainability info lookup by product id
        const sustainabilityInfo = {
            1:{source:'Recycled stainless steel sourced ethically',made:'Manufactured in a solar-powered facility using eco-friendly processes',end:'100% recyclable metal'},
            2:{source:'Organic cotton from certified farms',made:'Low-impact dyes and fair-trade sewing',end:'Biodegradable or recyclable as textile'},
            3:{source:'Fast-growing bamboo harvested sustainably',made:'CNC machining with minimal waste',end:'Compostable bamboo and recyclable packaging'},
            4:{source:'High-efficiency photovoltaic cells',made:'Assembly in ISO-14001 factory',end:'Electronics recycling recommended'},
            5:{source:'Reusable glass produced with 30% cullet',made:'Filled locally to reduce transport emissions',end:'Glass recycling'},
            6:{source:'Plant-based ingredients grown organically',made:'Blended in zero-waste facility',end:'Refillable bottles recyclable'},
            7:{source:'Bamboo fiber from FSC forests',made:'Molded under low-heat process',end:'Compostable bamboo body'},
            8:{source:'Hemp grown without pesticides',made:'Woven and sewn in fair-wage workshop',end:'Fabric recyclable or compostable'},
            9:{source:'LEDs sourced from RoHS suppliers',made:'Solar panels assembled with renewable energy',end:'E-waste recycling'},
            10:{source:'GOTS-certified organic cotton',made:'Bleach-free processing',end:'Fully biodegradable textile'},
            11:{source:'Plastic reclaimed from oceans',made:'Compression-molded with no added dyes',end:'Return-to-recycle program'},
            12:{source:'Organic cotton infused with beeswax',made:'Handcrafted wraps',end:'Home compostable'},
             13:{source:'Mixed post-consumer plastic collected locally',made:'Compression-molded in low-energy presses',end:'Bricks can be re-ground and remolded'},
             14:{source:'End-of-life vehicle tires diverted from landfill',made:'Crumb rubber bonded with non-toxic binders',end:'Tiles recyclable into new rubber products'},
             15:{source:'Recycled polycarbonate and EPS foam',made:'Factory powered by 100% renewable energy',end:'Manufacturer take-back recycling scheme'}
        };

        function showJourney(id){
            const info = sustainabilityInfo[id];
            if(!info){alert('Information unavailable');return;}
            document.getElementById('journeySource').textContent = info.source;
            document.getElementById('journeyMade').textContent = info.made;
            document.getElementById('journeyEnd').textContent = info.end;
            document.getElementById('journeyModal').style.display='block';
        }
        function closeJourney(){
            document.getElementById('journeyModal').style.display='none';
        }
        
        function addToCart(id, name, price, image) {
            const existingItem = cart.find(item => item.id === id);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({id, name, price, image, quantity: 1});
            }
            updateCartCount();
            showNotification(`Added ${name} to cart! 🌱`);
            
            // Update session cart
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, name, price, image})
            });
        }
        
        function updateCartCount() {
            document.getElementById('cartCount').textContent = cart.length;
        }
        
        function openCart() {
            updateCartDisplay();
            document.getElementById('cartModal').style.display = 'block';
        }
        
        function closeCart() {
            document.getElementById('cartModal').style.display = 'none';
        }
        
        function updateCartDisplay() {
            const cartItems = document.getElementById('cartItems');
            const cartTotal = document.getElementById('cartTotal');
            
            if (cart.length === 0) {
                cartItems.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">Your cart is empty 🛒</p>';
                cartTotal.textContent = 'Total: $0.00';
                return;
            }
            
            let html = '';
            let total = 0;
            
            cart.forEach(item => {
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                html += `
                    <div class="cart-item">
                        <div>
                            <span style="font-size: 2rem;">${item.image}</span>
                            <strong>${item.name}</strong><br>
                            <span style="color: #4caf50;">$${item.price.toFixed(2)} each</span>
                        </div>
                        <div class="quantity-controls">
                            <button class="quantity-btn" onclick="changeQuantity(${item.id}, -1)">-</button>
                            <span style="margin: 0 1rem;">${item.quantity}</span>
                            <button class="quantity-btn" onclick="changeQuantity(${item.id}, 1)">+</button>
                            <button class="quantity-btn" onclick="removeFromCart(${item.id})" style="background: #f44336; margin-left: 1rem;">×</button>
                        </div>
                    </div>
                `;
            });
            
            cartItems.innerHTML = html;
            cartTotal.textContent = `Total: $${total.toFixed(2)}`;
        }
        
        function changeQuantity(id, change) {
            const item = cart.find(item => item.id === id);
            if (item) {
                item.quantity += change;
                if (item.quantity <= 0) {
                    removeFromCart(id);
                } else {
                    updateCartDisplay();
                }
            }
        }
        
        function removeFromCart(id) {
            cart = cart.filter(item => item.id !== id);
            updateCartCount();
            updateCartDisplay();
        }
        
        function checkout() {
            if (cart.length === 0) {
                alert('Your cart is empty!');
                return;
            }

            // collect customer info (simple prompt flow)
            const customer_name = prompt('Enter your name:');
            if (!customer_name) return;
            const customer_email = prompt('Enter your email:');
            if (!customer_email) return;
            const customer_phone = prompt('Enter your phone number:');
            if (!customer_phone) return;

            const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

            fetch('/place_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_name,
                    customer_email,
                    customer_phone,
                    items: cart,
                    total: total
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(`🎉 Thank you for your order! Your order ID is #${data.order_id}.\\nTotal: $${total.toFixed(2)}\\n\\n🌱 Your sustainable choices make a difference!`);
                    cart = [];
                    updateCartCount();
                    closeCart();
                } else {
                    alert('❌ Unable to place order: ' + data.error);
                }
            })
            .catch(err => {
                alert('❌ Network error: ' + err);
            });
        }
        
        function filterProducts() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categoryFilter = document.getElementById('categoryFilter').value;
            const products = document.querySelectorAll('.product-card');
            
            products.forEach(product => {
                const name = product.getAttribute('data-name');
                const category = product.getAttribute('data-category');
                
                const matchesSearch = name.includes(searchTerm);
                const matchesCategory = !categoryFilter || category === categoryFilter;
                
                if (matchesSearch && matchesCategory) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        }
        
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px; background: #4caf50; color: white;
                padding: 1rem 2rem; border-radius: 25px; z-index: 3000; font-weight: bold;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3); animation: slideIn 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // Load cart from session on page load
        fetch('/get_cart')
            .then(response => response.json())
            .then(data => {
                cart = data.cart || [];
                updateCartCount();
            });
    </script>
</body>
</html>
    ''', products=products, cart_count=cart_count)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    
    item = request.json
    session['cart'].append(item)
    session.modified = True
    
    return jsonify({'success': True, 'cart_count': len(session['cart'])})

@app.route('/get_cart')
def get_cart():
    return jsonify({'cart': session.get('cart', [])})

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        order_data = request.json
        
        conn = sqlite3.connect('ecoshop_orders.db')
        cursor = conn.cursor()
        
        # Apply any available discount based on existing points BEFORE awarding new points
        customer_email = order_data.get('customer_email')
        current_pts = get_points(customer_email)
        disc_rate, _ = tier_discount(current_pts)
        discounted_total = round(order_data['total'] * (1 - disc_rate), 2)

        # Insert order with discounted total
        cursor.execute('''
            INSERT INTO orders (order_date, customer_name, customer_email, customer_phone, items, total_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            order_data['customer_name'],
            customer_email,
            order_data['customer_phone'],
            json.dumps(order_data['items']),
            discounted_total
        ))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Award Green Points (+10 per order)
        # Award points AFTER order placement
        award_points(customer_email, 10)
        total_pts = get_points(customer_email)
        disc_rate, reward_text = tier_discount(total_pts)

        # Clear cart
        session['cart'] = []
        
        return jsonify({'success': True,
                        'order_id': order_id,
                        'green_points': total_pts,
                        'reward': reward_text,
                        'discount_rate': disc_rate})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/products')
def products_page():
    if 'cart' not in session:
        session['cart'] = []
    cart_count = len(session['cart'])
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Products - EcoCities</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #e8f5e8, #f0f8f0); }
        
        .navbar { background: linear-gradient(135deg, #2e7d32, #4caf50); color: white; padding: 1rem 0; position: sticky; top: 0; z-index: 1000; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
        .logo { font-size: 2rem; font-weight: bold; text-decoration: none; color: white; }
        .nav-links { display: flex; gap: 2rem; align-items: center; }
        .nav-link { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 20px; transition: background 0.3s; }
        .nav-link:hover { background: rgba(255,255,255,0.2); }
        .nav-link.active { background: rgba(255,255,255,0.3); }
        
        .cart-icon { position: relative; background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 50%; cursor: pointer; transition: all 0.3s; }
        .cart-icon:hover { background: rgba(255,255,255,0.3); transform: scale(1.1); }
        .cart-count { position: absolute; top: -5px; right: -5px; background: #ff5722; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; }
        
        .header { background: linear-gradient(135deg, #2e7d32, #4caf50); color: white; padding: 2rem 0; text-align: center; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        .search-bar { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin: 2rem 0; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
        .search-input { flex: 1; min-width: 250px; padding: 1rem; font-size: 1.1rem; border: 2px solid #4caf50; border-radius: 25px; outline: none; }
        .filter-select { padding: 1rem; font-size: 1rem; border: 2px solid #4caf50; border-radius: 25px; outline: none; background: white; }
        .search-btn { padding: 1rem 2rem; background: #4caf50; color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 1.1rem; transition: all 0.3s; }
        .search-btn:hover { background: #388e3c; transform: translateY(-2px); }
        
        .products { margin: 2rem 0; }
        .products h2 { text-align: center; font-size: 2.5rem; color: #2e7d32; margin-bottom: 3rem; }
        .product-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        
        .product-card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-8px); }
        .product-image { height: 200px; background: linear-gradient(45deg, #81c784, #a5d6a7); display: flex; align-items: center; justify-content: center; font-size: 4rem; color: white; position: relative; }
        .stock-badge { position: absolute; top: 10px; right: 10px; background: #4caf50; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
        .low-stock { background: #ff9800; }
        
        .product-info { padding: 1.5rem; }
        .product-title { font-size: 1.3rem; font-weight: bold; color: #2e7d32; margin-bottom: 0.5rem; }
        .product-price { font-size: 1.5rem; font-weight: bold; color: #4caf50; margin: 1rem 0; }
        .product-description { color: #666; margin-bottom: 1rem; font-size: 0.9rem; }
        .product-category { display: inline-block; background: #e8f5e8; color: #2e7d32; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-bottom: 1rem; }
        
        .btn { background: linear-gradient(135deg, #4caf50, #66bb6a); color: white; padding: 0.8rem 2rem; border: none; border-radius: 25px; cursor: pointer; font-size: 1rem; transition: all 0.3s; width: 100%; text-align: center; }
        .btn:hover { background: linear-gradient(135deg, #388e3c, #4caf50); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        
        .footer { background: #2e7d32; color: white; text-align: center; padding: 2rem 0; margin-top: 4rem; }
        
        /* Cart Modal */
        .modal { display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: white; margin: 5% auto; padding: 2rem; border-radius: 15px; width: 90%; max-width: 600px; max-height: 80vh; overflow-y: auto; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: #000; }
        .cart-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #eee; }
        .cart-total { font-size: 1.5rem; font-weight: bold; color: #2e7d32; text-align: right; margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #4caf50; }
        .quantity-controls { display: flex; align-items: center; gap: 0.5rem; }
        .quantity-btn { background: #4caf50; color: white; border: none; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; }
        .checkout-btn { background: linear-gradient(135deg, #ff9800, #ffa726); color: white; padding: 1rem 2rem; border: none; border-radius: 25px; cursor: pointer; font-size: 1.1rem; width: 100%; margin-top: 1rem; }
        
        @media (max-width: 768px) {
            .nav-container { flex-direction: column; gap: 1rem; }
            .search-bar { flex-direction: column; }
            .search-input { min-width: 100%; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">🌱 EcoCities</a>
            <div class="nav-links">
                <a href="/" class="nav-link">Home</a>
                <a href="/products" class="nav-link active">Products</a>
                <a href="/about" class="nav-link">About</a>
                    <a href="/exchange" class="nav-link">EcoReuse</a>
                    <a href="/blog" class="nav-link">Eco Tips</a>
                    <a href="/points" class="nav-link">Green Points</a>
                <div class="cart-icon" onclick="openCart()">
                    🛒
                    <span class="cart-count" id="cartCount">{{ cart_count }}</span>
                </div>
            </div>
        </div>
    </nav>
    
    <header class="header">
        <h1>🛍️ Our Products</h1>
        <p>Discover our complete collection of sustainable products</p>
    </header>
    
    <div class="container">
        <div class="search-bar">
            <input type="text" class="search-input" id="searchInput" placeholder="Search eco-friendly products...">
            <select class="filter-select" id="categoryFilter">
                <option value="">All Categories</option>
                <option value="Drinkware">Drinkware</option>
                <option value="Clothing">Clothing</option>
                <option value="Accessories">Accessories</option>
                <option value="Electronics">Electronics</option>
                <option value="Home">Home</option>
                <option value="Fitness">Fitness</option>
                <option value="Kitchen">Kitchen</option>
                <option value="Construction">Construction</option>
                <option value="Flooring">Flooring</option>
                <option value="Safety">Safety</option>
            </select>
            <button class="search-btn" onclick="filterProducts()">🔍 Search</button>
        </div>
        
        <section class="products">
            <h2>All Sustainable Products</h2>
            <div class="product-grid" id="productGrid">
                {% for product in products %}
                <div class="product-card" data-category="{{ product.category }}" data-name="{{ product.name.lower() }}">
                    <div class="product-image">
                        {{ product.image }}
                        <span class="stock-badge {% if product.stock < 10 %}low-stock{% endif %}">
                            {{ product.stock }} left
                        </span>
                    </div>
                    <div class="product-info">
                        <div class="product-category">{{ product.category }}</div>
                        <div class="product-title">{{ product.name }}</div>
                        <div class="product-price">${{ "%.2f"|format(product.price) }}</div>
                        <div class="product-description">{{ product.description }}</div>
                        <button class="btn" onclick="addToCart({{ product.id }}, '{{ product.name }}', {{ product.price }}, '{{ product.image }}')">
                            Add to Cart 🛒
                        </button>
                        <button class="btn" style="margin-top:0.5rem;background:linear-gradient(135deg,#2196f3,#42a5f5);" onclick="showJourney({{ product.id }})">Sustainability Journey 🌍</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
    </div>
    
    <!-- Cart Modal -->
    <div id="cartModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeCart()">&times;</span>
            <h2>🛒 Your Shopping Cart</h2>
            <div id="cartItems"></div>
            <div class="cart-total" id="cartTotal">Total: $0.00</div>
            <button class="checkout-btn" onclick="checkout()">🚀 Proceed to Checkout</button>
        </div>
    </div>
    
    <!-- Sustainability Modal -->
    <div id="journeyModal" class="modal">
        <div class="modal-content" style="max-width:500px;">
            <span class="close" onclick="closeJourney()">&times;</span>
            <h2>🌍 Sustainability Journey</h2>
            <p><strong>Source:</strong> <span id="journeySource"></span></p>
            <p><strong>Manufacturing:</strong> <span id="journeyMade"></span></p>
            <p><strong>End-of-Life:</strong> <span id="journeyEnd"></span></p>
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2025 EcoCities - All Products Page 🌍</p>
        <p>Contact: hello@ecoshop.com | 1-800-ECO-SHOP</p>
    </footer>
    
    <script>
        let cart = [];
        // Sustainability info lookup by product id
        const sustainabilityInfo = {
            1:{source:'Recycled stainless steel sourced ethically',made:'Manufactured in a solar-powered facility using eco-friendly processes',end:'100% recyclable metal'},
            2:{source:'Organic cotton from certified farms',made:'Low-impact dyes and fair-trade sewing',end:'Biodegradable or recyclable as textile'},
            3:{source:'Fast-growing bamboo harvested sustainably',made:'CNC machining with minimal waste',end:'Compostable bamboo and recyclable packaging'},
            4:{source:'High-efficiency photovoltaic cells',made:'Assembly in ISO-14001 factory',end:'Electronics recycling recommended'},
            5:{source:'Reusable glass produced with 30% cullet',made:'Filled locally to reduce transport emissions',end:'Glass recycling'},
            6:{source:'Plant-based ingredients grown organically',made:'Blended in zero-waste facility',end:'Refillable bottles recyclable'},
            7:{source:'Bamboo fiber from FSC forests',made:'Molded under low-heat process',end:'Compostable bamboo body'},
            8:{source:'Hemp grown without pesticides',made:'Woven and sewn in fair-wage workshop',end:'Fabric recyclable or compostable'},
            9:{source:'LEDs sourced from RoHS suppliers',made:'Solar panels assembled with renewable energy',end:'E-waste recycling'},
            10:{source:'GOTS-certified organic cotton',made:'Bleach-free processing',end:'Fully biodegradable textile'},
            11:{source:'Plastic reclaimed from oceans',made:'Compression-molded with no added dyes',end:'Return-to-recycle program'},
            12:{source:'Organic cotton infused with beeswax',made:'Handcrafted wraps',end:'Home compostable'},
             13:{source:'Mixed post-consumer plastic collected locally',made:'Compression-molded in low-energy presses',end:'Bricks can be re-ground and remolded'},
             14:{source:'End-of-life vehicle tires diverted from landfill',made:'Crumb rubber bonded with non-toxic binders',end:'Tiles recyclable into new rubber products'},
             15:{source:'Recycled polycarbonate and EPS foam',made:'Factory powered by 100% renewable energy',end:'Manufacturer take-back recycling scheme'}
        };

        function showJourney(id){
            const info = sustainabilityInfo[id];
            if(!info){alert('Information unavailable');return;}
            document.getElementById('journeySource').textContent = info.source;
            document.getElementById('journeyMade').textContent = info.made;
            document.getElementById('journeyEnd').textContent = info.end;
            document.getElementById('journeyModal').style.display='block';
        }
        function closeJourney(){
            document.getElementById('journeyModal').style.display='none';
        }
        
        function addToCart(id, name, price, image) {
            const existingItem = cart.find(item => item.id === id);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({id, name, price, image, quantity: 1});
            }
            updateCartCount();
            showNotification(`Added ${name} to cart! 🌱`);
            
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, name, price, image})
            });
        }
        
        function updateCartCount() {
            document.getElementById('cartCount').textContent = cart.length;
        }
        
        function openCart() {
            updateCartDisplay();
            document.getElementById('cartModal').style.display = 'block';
        }
        
        function closeCart() {
            document.getElementById('cartModal').style.display = 'none';
        }
        
        function updateCartDisplay() {
            const cartItems = document.getElementById('cartItems');
            const cartTotal = document.getElementById('cartTotal');
            
            if (cart.length === 0) {
                cartItems.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">Your cart is empty 🛒</p>';
                cartTotal.textContent = 'Total: $0.00';
                return;
            }
            
            let html = '';
            let total = 0;
            
            cart.forEach(item => {
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                html += `
                    <div class="cart-item">
                        <div>
                            <span style="font-size: 2rem;">${item.image}</span>
                            <strong>${item.name}</strong><br>
                            <span style="color: #4caf50;">$${item.price.toFixed(2)} each</span>
                        </div>
                        <div class="quantity-controls">
                            <button class="quantity-btn" onclick="changeQuantity(${item.id}, -1)">-</button>
                            <span style="margin: 0 1rem;">${item.quantity}</span>
                            <button class="quantity-btn" onclick="changeQuantity(${item.id}, 1)">+</button>
                            <button class="quantity-btn" onclick="removeFromCart(${item.id})" style="background: #f44336; margin-left: 1rem;">×</button>
                        </div>
                    </div>
                `;
            });
            
            cartItems.innerHTML = html;
            cartTotal.textContent = `Total: $${total.toFixed(2)}`;
        }
        
        function changeQuantity(id, change) {
            const item = cart.find(item => item.id === id);
            if (item) {
                item.quantity += change;
                if (item.quantity <= 0) {
                    removeFromCart(id);
                } else {
                    updateCartDisplay();
                }
            }
        }
        
        function removeFromCart(id) {
            cart = cart.filter(item => item.id !== id);
            updateCartCount();
            updateCartDisplay();
        }
        
        function checkout() {
            if (cart.length === 0) {
                alert('Your cart is empty!');
                return;
            }

            // Collect customer info – quick prompt UI (can be replaced with proper form)
            const customer_name = prompt('Enter your name:');
            if (!customer_name) return;
            const customer_email = prompt('Enter your email:');
            if (!customer_email) return;
            const customer_phone = prompt('Enter your phone number:');
            if (!customer_phone) return;

            const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

            fetch('/place_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_name,
                    customer_email,
                    customer_phone,
                    items: cart,
                    total: total
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`🎉 Thank you for your order! Your order ID is #${data.order_id}.\nTotal: $${total.toFixed(2)}\n\n🌱 Your sustainable choices make a difference!`);
                    cart = [];
                    updateCartCount();
                    closeCart();
                } else {
                    alert('❌ Unable to place order: ' + data.error);
                }
            })
            .catch(err => {
                alert('❌ Network error: ' + err);
            });
        }
        
        function filterProducts() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categoryFilter = document.getElementById('categoryFilter').value;
            const products = document.querySelectorAll('.product-card');
            
            products.forEach(product => {
                const name = product.getAttribute('data-name');
                const category = product.getAttribute('data-category');
                
                const matchesSearch = name.includes(searchTerm);
                const matchesCategory = !categoryFilter || category === categoryFilter;
                
                if (matchesSearch && matchesCategory) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        }
        
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px; background: #4caf50; color: white;
                padding: 1rem 2rem; border-radius: 25px; z-index: 3000; font-weight: bold;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3); animation: slideIn 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // Load cart from session on page load
        fetch('/get_cart')
            .then(response => response.json())
            .then(data => {
                cart = data.cart || [];
                updateCartCount();
            });
    </script>
</body>
</html>
    ''', products=products, cart_count=cart_count)

@app.route('/admin')
def admin_orders():
    conn = sqlite3.connect('ecoshop_orders.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, order_date, customer_name, customer_email, customer_phone, total_amount, status, items
        FROM orders ORDER BY order_date DESC
    ''')
    raw_orders = cursor.fetchall()
    
    # Parse JSON items for each order
    orders = []
    for order in raw_orders:
        order_dict = {
            'id': order[0],
            'date': order[1],
            'name': order[2],
            'email': order[3],
            'phone': order[4],
            'total': order[5],
            'status': order[6],
            'item_list': json.loads(order[7]) if order[7] else []
        }
        orders.append(order_dict)
    
    conn.close()
    
    # Calculate statistics
    total_orders = len(orders)
    total_revenue = sum(order['total'] for order in orders)
    pending_orders = sum(1 for order in orders if order['status'] == 'Pending')
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Order Database | EcoCities</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #e8f5e8, #f0f8f0); }
        .navbar { background: linear-gradient(135deg, #2e7d32, #4caf50); color: white; padding: 1rem 0; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 2rem; }
        .logo { font-size: 2rem; font-weight: bold; text-decoration: none; color: white; }
        .nav-links { display: flex; gap: 2rem; align-items: center; }
        .nav-link { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 20px; transition: background 0.3s; }
        .nav-link:hover { background: rgba(255,255,255,0.2); }
        .nav-link.active { background: rgba(255,255,255,0.3); }
        .header { background: linear-gradient(135deg, #2e7d32, #4caf50); color: white; padding: 2rem 0; text-align: center; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin: 2rem 0; }
        .stat-card { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2.5rem; font-weight: bold; color: #4caf50; }
        .stat-label { color: #666; margin-top: 0.5rem; }
        .orders-table { background: white; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); overflow: hidden; margin: 2rem 0; }
        .table-header { background: #4caf50; color: white; padding: 1.5rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f5f5f5; font-weight: bold; color: #2e7d32; }
        tr:hover { background: #f9f9f9; }
        .status-badge { padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold; background: #fff3cd; color: #856404; }
        .order-items { font-size: 0.9rem; color: #666; max-width: 200px; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">🌱 EcoCities</a>
            <div class="nav-links">
                <a href="/" class="nav-link">Home</a>
                <a href="/products" class="nav-link">Products</a>
                <a href="/admin" class="nav-link active">📊 Orders</a>
                <a href="/about" class="nav-link">About</a>
                    <a href="/exchange" class="nav-link">EcoReuse</a>
                    <a href="/blog" class="nav-link">Eco Tips</a>
                    <a href="/points" class="nav-link">Green Points</a>
            </div>
        </div>
    </nav>
    
    <header class="header">
        <h1>📊 Order Database</h1>
        <p>View all customer orders and checkout data</p>
    </header>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_orders }}</div>
                <div class="stat-label">Total Orders</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${{ "%.2f"|format(total_revenue) }}</div>
                <div class="stat-label">Total Revenue</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ pending_orders }}</div>
                <div class="stat-label">Pending Orders</div>
            </div>
        </div>
        
        <div class="orders-table">
            <div class="table-header">
                <h2>🛒 All Customer Orders</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Date</th>
                        <th>Customer</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Items</th>
                        <th>Total</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in orders %}
                    <tr>
                        <td><strong>#{{ order.id }}</strong></td>
                        <td>{{ order.date }}</td>
                        <td>{{ order.name }}</td>
                        <td>{{ order.email }}</td>
                        <td>{{ order.phone }}</td>
                        <td class="order-items">
                            {% for item in order.item_list %}
                                {{ item.name }} ({{ item.quantity }}x)<br>
                            {% endfor %}
                        </td>
                        <td><strong>${{ "%.2f"|format(order.total) }}</strong></td>
                        <td>
                            <span class="status-badge">{{ order.status }}</span>
                            {% if order.status == 'Pending' %}
                                <form method="POST" action="/admin/order/{{ order.id }}/delivered" style="display:inline-block;margin-left:6px;">
                                    <button type="submit" style="background:#4caf50;border:none;color:white;padding:0.3rem 0.8rem;border-radius:12px;font-size:0.75rem;cursor:pointer;">Delivered</button>
                                </form>
                            {% endif %}
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="8" style="text-align: center; padding: 3rem; color: #666;">
                            📦 No orders yet. Customers will appear here after checkout.
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
    ''', orders=orders, total_orders=total_orders, total_revenue=total_revenue, pending_orders=pending_orders)

# -------- Order status update ---------
@app.route('/admin/order/<int:order_id>/delivered', methods=['POST'])
def mark_order_delivered(order_id):
    """Set order status to Delivered"""
    conn = sqlite3.connect('ecoshop_orders.db')
    cur = conn.cursor()
    cur.execute('UPDATE orders SET status = ? WHERE id = ?', ("Delivered", order_id))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/exchange')

def exchange_page():
    # Fetch available items
    conn = sqlite3.connect('ecoshop_orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, condition, owner_email, posted_at FROM reused_items WHERE status="Available" ORDER BY posted_at DESC')
    items = cursor.fetchall()
    conn.close()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>EcoReuse Exchange - EcoCities</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body{font-family:Arial, sans-serif;background:#f5fff5;margin:0;padding:0}
            .header{background:#2e7d32;color:white;padding:1.5rem;text-align:center}
            .container{max-width:900px;margin:2rem auto;padding:0 1rem}
            .item-card{background:white;border-radius:12px;padding:1rem;margin-bottom:1.5rem;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
            .item-title{font-size:1.3rem;font-weight:bold;color:#2e7d32}
            .btn{background:#4caf50;color:white;border:none;border-radius:20px;padding:0.5rem 1rem;cursor:pointer;margin-top:0.5rem}
            .form-card{background:white;padding:1rem;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);margin-bottom:2rem}
            input,textarea{width:100%;padding:0.7rem;border:2px solid #4caf50;border-radius:10px;margin-top:0.5rem}
        </style>
    </head>
    <body>
        <div class="header"><h1>♻️ EcoReuse Exchange</h1><p>Give eco-products a second life and earn EcoCredits!</p></div>
        <div class="container">
            <div class="form-card">
                <h2>Post an Item</h2>
                <form method="POST" action="/exchange/new">
                    <label>Title</label>
                    <input name="title" required>
                    <label>Description</label>
                    <textarea name="description" rows="3" required></textarea>
                    <label>Condition</label>
                    <input name="condition" placeholder="Like new / Good / Used" required>
                    <label>Your Email</label>
                    <input type="email" name="email" required>
                    <button type="submit" class="btn">Post Item</button>
                </form>
            </div>
            <h2>Available Items</h2>
            {% for item in items %}
            <div class="item-card">
                <div class="item-title">{{ item[1] }}</div>
                <p>{{ item[2] }}</p>
                <p><strong>Condition:</strong> {{ item[3] }}</p>
                <p><strong>Posted by:</strong> {{ item[4] }}</p>
                <form method="POST" action="/exchange/request/{{ item[0] }}">
                    <input type="email" name="email" placeholder="Your email to request" required>
                    <button type="submit" class="btn">Request Item</button>
                </form>
            </div>
            {% else %}
            <p>No items yet. Be the first to post!</p>
            {% endfor %}
            <p style="text-align:center;margin-top:2rem;"><a href="/" style="text-decoration:none;color:#2e7d32">← Back to Home</a></p>
        </div>
    </body>
    </html>
    ''', items=items)


@app.route('/exchange/new', methods=['POST'])

def post_exchange_item():
    data = request.form
    conn = sqlite3.connect('ecoshop_orders.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO reused_items (title, description, condition, owner_email, posted_at) VALUES (?,?,?,?,?)''',
                   (data['title'], data['description'], data['condition'], data['email'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    return redirect('/exchange')


@app.route('/exchange/request/<int:item_id>', methods=['POST'])

def request_exchange_item(item_id):
    requester_email = request.form['email']
    # For MVP we just mark item as reserved and show basic message
    conn = sqlite3.connect('ecoshop_orders.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE reused_items SET status="Reserved" WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    return f"Thank you! Your request for item #{item_id} has been recorded. The owner will contact you soon. <a href='/exchange'>Back</a>"


@app.route('/blog')

def blog_page():
    conn = sqlite3.connect('ecoshop_orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, posted_at FROM eco_tips ORDER BY posted_at DESC')
    tips = cursor.fetchall()
    conn.close()
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Eco Tips & Reuse Hacks - EcoCities</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body{font-family:Arial,sans-serif;background:#f9fff9;margin:0;padding:0}
            .header{background:#388e3c;color:white;text-align:center;padding:2rem}
            .container{max-width:800px;margin:2rem auto;padding:0 1rem}
            .tip-card{background:white;border-radius:12px;padding:1.2rem;margin-bottom:1.5rem;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
            .tip-title{font-size:1.4rem;font-weight:bold;color:#2e7d32}
            .btn{background:#4caf50;color:white;border:none;border-radius:20px;padding:0.5rem 1rem;cursor:pointer;margin-top:0.5rem}
            textarea,input{width:100%;padding:0.7rem;border:2px solid #4caf50;border-radius:10px;margin-top:0.5rem}
            .form-card{background:white;padding:1rem;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);margin-bottom:2rem}
        </style>
    </head>
    <body>
        <div class="header"><h1>🌿 Eco Tips & Reuse Hacks</h1><p>Daily challenges and planet-friendly ideas</p></div>
        <div class="container">
            <div class="form-card">
                <h2>Share a Tip</h2>
                <form method="POST" action="/blog/new">
                    <label>Title</label>
                    <input name="title" required>
                    <label>Content</label>
                    <textarea name="content" rows="4" required></textarea>
                    <label>Your Email (to earn Green Points)</label>
                    <input type="email" name="email" required>
                    <button class="btn" type="submit">Post Tip</button>
                </form>
            </div>
            {% for tip in tips %}
            <div class="tip-card">
                <div class="tip-title">{{ tip[1] }}</div>
                <p>{{ tip[2] }}</p>
                <p style="font-size:0.8rem;color:#666">Posted {{ tip[3] }}</p>
            </div>
            {% else %}
            <p>No tips yet – share your first reuse hack!</p>
            {% endfor %}
            <p style="text-align:center;margin-top:2rem"><a href="/" style="text-decoration:none;color:#2e7d32">← Back to Home</a></p>
        </div>
    </body>
    </html>
    ''', tips=tips)


@app.route('/blog/new', methods=['POST'])

def post_blog_tip():
    data = request.form
    conn = sqlite3.connect('ecoshop_orders.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO eco_tips (title, content, posted_at) VALUES (?,?,?)', (data['title'], data['content'], datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    # Award Green Points for sharing a tip (+15) - run after releasing first DB lock
    award_points(data.get('email', ''), 15)
    return redirect('/blog')


@app.route('/about')
def about():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>About EcoCities</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body{font-family:Arial, sans-serif;margin:0;padding:0;background:#f5fff5;line-height:1.6}
            .hero{background:linear-gradient(135deg,#2e7d32,#4caf50);color:white;text-align:center;padding:4rem 1rem}
            .hero h1{font-size:3rem;margin-bottom:1rem}
            .hero p{font-size:1.2rem;max-width:700px;margin:0 auto}
            .section{max-width:900px;margin:3rem auto;padding:0 1rem}
            .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:2rem}
            .card{background:white;border-radius:15px;padding:2rem;box-shadow:0 6px 18px rgba(0,0,0,0.1);text-align:center}
            .card span{font-size:2rem;display:block;margin-bottom:0.5rem}
            .values{display:flex;flex-direction:column;gap:1rem;margin-top:1rem}
            .value{background:#e8f5e8;border-left:6px solid #4caf50;padding:1rem;border-radius:10px}
            a.back{display:inline-block;margin:2rem auto;text-decoration:none;color:#2e7d32;font-weight:bold}
        </style>
    </head>
    <body>
        <section class="hero">
            <h1>🌱 Welcome to EcoCities</h1>
            <p>Your one-stop marketplace for planet-positive products and inspiration. We believe shopping should nourish the Earth, not deplete it.</p>
        </section>
        <section class="section">
            <h2 style="text-align:center;color:#2e7d32;margin-bottom:2rem;">Why Shop With Us?</h2>
            <div class="grid">
                <div class="card"><span>🛒</span><h3>Seamless Experience</h3><p>Smart cart, quick checkout, mobile-first design.</p></div>
                <div class="card"><span>🌍</span><h3>100% Sustainable Catalog</h3><p>Every item vetted for eco-materials & ethical sourcing.</p></div>
                <div class="card"><span>♻️</span><h3>Circular Features</h3><p>EcoReuse Exchange and tips to keep products in use longer.</p></div>
                <div class="card"><span>📊</span><h3>Transparency</h3><p>Track your carbon savings & EcoCredits with every order.</p></div>
            </div>
        </section>
        <section class="section" style="margin-top:4rem;">
            <h2 style="text-align:center;color:#2e7d32;margin-bottom:1rem;">Our Core Values</h2>
            <div class="values">
                <div class="value"><strong>🔄 Circularity:</strong> Design waste out of the system through reuse, refill, and recycling.</div>
                <div class="value"><strong>🤝 Community:</strong> Empower shoppers and makers to collaborate on a greener future.</div>
                <div class="value"><strong>📚 Education:</strong> Share actionable eco-tips and challenges every day.</div>
                <div class="value"><strong>🚀 Innovation:</strong> Continually build features that make sustainable choices effortless.</div>
            </div>
        </section>
        <p style="text-align:center"><a class="back" href="/">← Back to Home</a></p>
    </body>
    </html>
    '''


@app.route('/points')
def points_dashboard():
    email = request.args.get('email', '')
    pts = get_points(email) if email else None
    disc, reward = tier_discount(pts or 0)
    return render_template_string('''
    <!DOCTYPE html>
    <html><head><title>Green Points</title>
    <meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="font-family:Arial;background:#f4fff4;text-align:center;padding:3rem;">
        <h1>🌟 My Green Points</h1>
        <form method="get" style="margin-bottom:2rem;">
            <input name="email" placeholder="Enter email" value="{{ email }}" required style="padding:0.6rem;border:2px solid #4caf50;border-radius:8px;">
            <button style="padding:0.6rem 1.4rem;background:#4caf50;color:white;border:none;border-radius:8px;">Check</button>
        </form>
        {% if pts is not none %}
            <h2>{{ pts }} points</h2>
            <p>{{ reward }}</p>
        {% endif %}
        <p><a href="/">← Back to Home</a></p>
    </body></html>
    ''', email=email, pts=pts, reward=reward)

if __name__ == '__main__':
    print("🌱 Enhanced EcoCities Starting...")
    print("🛒 Features: Shopping Cart, Search, Filters, Mobile-Responsive")
    print("🌐 Open: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)
