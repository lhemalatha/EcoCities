from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EcoShop - Sustainable Products Store</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
            }
            
            .header {
                background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
                color: white;
                padding: 2rem 0;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .header h1 {
                font-size: 3rem;
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 2rem;
                margin: 3rem 0;
            }
            
            .feature-card {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }
            
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .products {
                margin: 4rem 0;
            }
            
            .products h2 {
                text-align: center;
                font-size: 2.5rem;
                color: #2e7d32;
                margin-bottom: 3rem;
            }
            
            .product-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 2rem;
            }
            
            .product-card {
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .product-card:hover {
                transform: translateY(-8px);
            }
            
            .product-image {
                height: 200px;
                background: linear-gradient(45deg, #81c784, #a5d6a7);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 4rem;
                color: white;
            }
            
            .product-info {
                padding: 1.5rem;
            }
            
            .product-title {
                font-size: 1.3rem;
                font-weight: bold;
                color: #2e7d32;
                margin-bottom: 0.5rem;
            }
            
            .product-price {
                font-size: 1.5rem;
                font-weight: bold;
                color: #4caf50;
                margin: 1rem 0;
            }
            
            .product-description {
                color: #666;
                margin-bottom: 1rem;
            }
            
            .btn {
                background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
                color: white;
                padding: 0.8rem 2rem;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1rem;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            
            .btn:hover {
                background: linear-gradient(135deg, #388e3c 0%, #4caf50 100%);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .footer {
                background: #2e7d32;
                color: white;
                text-align: center;
                padding: 2rem 0;
                margin-top: 4rem;
            }
            
            .search-bar {
                text-align: center;
                margin: 2rem 0;
            }
            
            .search-input {
                padding: 1rem;
                font-size: 1.1rem;
                border: 2px solid #4caf50;
                border-radius: 25px;
                width: 300px;
                outline: none;
            }
            
            .search-btn {
                padding: 1rem 2rem;
                margin-left: 1rem;
                background: #4caf50;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        <header class="header">
            <h1>🌱 EcoShop</h1>
            <p>Your Sustainable Shopping Destination</p>
        </header>
        
        <div class="container">
            <div class="search-bar">
                <input type="text" class="search-input" placeholder="Search eco-friendly products...">
                <button class="search-btn">🔍 Search</button>
            </div>
            
            <section class="features">
                <div class="feature-card">
                    <div class="feature-icon">🌿</div>
                    <h3>100% Eco-Friendly</h3>
                    <p>All our products are sustainably sourced and environmentally friendly</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">♻️</div>
                    <h3>Zero Waste Packaging</h3>
                    <p>We use only recyclable and biodegradable packaging materials</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🚚</div>
                    <h3>Carbon Neutral Shipping</h3>
                    <p>Free carbon-neutral shipping on all orders over $50</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💚</div>
                    <h3>Give Back Program</h3>
                    <p>1% of all profits go to environmental conservation projects</p>
                </div>
            </section>
            
            <section class="products">
                <h2>Featured Sustainable Products</h2>
                <div class="product-grid">
                    <div class="product-card">
                        <div class="product-image">🍃</div>
                        <div class="product-info">
                            <div class="product-title">Eco-Friendly Water Bottle</div>
                            <div class="product-price">$25.99</div>
                            <div class="product-description">Sustainable stainless steel water bottle that keeps drinks cold for 24 hours</div>
                            <button class="btn">Add to Cart</button>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">👕</div>
                        <div class="product-info">
                            <div class="product-title">Organic Cotton T-Shirt</div>
                            <div class="product-price">$35.00</div>
                            <div class="product-description">Super soft organic cotton t-shirt made from sustainably grown cotton</div>
                            <button class="btn">Add to Cart</button>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">📱</div>
                        <div class="product-info">
                            <div class="product-title">Bamboo Phone Case</div>
                            <div class="product-price">$18.50</div>
                            <div class="product-description">Stylish and durable bamboo phone case that's 100% biodegradable</div>
                            <button class="btn">Add to Cart</button>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">🔋</div>
                        <div class="product-info">
                            <div class="product-title">Solar Power Bank</div>
                            <div class="product-price">$45.00</div>
                            <div class="product-description">Portable solar-powered charging device with 20,000mAh capacity</div>
                            <button class="btn">Add to Cart</button>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">🧴</div>
                        <div class="product-info">
                            <div class="product-title">Refillable Soap Dispenser</div>
                            <div class="product-price">$22.99</div>
                            <div class="product-description">Beautiful glass soap dispenser with organic hand soap refills</div>
                            <button class="btn">Add to Cart</button>
                        </div>
                    </div>
                    
                    <div class="product-card">
                        <div class="product-image">🌱</div>
                        <div class="product-info">
                            <div class="product-title">Plant-Based Cleaning Kit</div>
                            <div class="product-price">$39.99</div>
                            <div class="product-description">Complete cleaning kit with plant-based, non-toxic cleaning products</div>
                            <button class="btn">Add to Cart</button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
        
        <footer class="footer">
            <p>&copy; 2025 EcoShop - Making the world greener, one purchase at a time 🌍</p>
            <p>Contact us: hello@ecoshop.com | 1-800-ECO-SHOP</p>
        </footer>
        
        <script>
            // Add some interactivity
            document.querySelector('.search-btn').addEventListener('click', function() {
                const searchTerm = document.querySelector('.search-input').value;
                if (searchTerm) {
                    alert('Searching for: ' + searchTerm + '\\n\\nFeature coming soon! 🌱');
                }
            });
            
            // Add to cart functionality
            document.querySelectorAll('.btn').forEach(button => {
                button.addEventListener('click', function() {
                    const productName = this.parentElement.querySelector('.product-title').textContent;
                    alert('Added "' + productName + '" to cart! 🛒\\n\\nThank you for choosing sustainable products! 🌱');
                });
            });
        </script>
    </body>
    </html>
    '''

@app.route('/about')
def about():
    return '''
    <h1>About EcoShop</h1>
    <p>EcoShop is dedicated to providing sustainable, eco-friendly products that help reduce environmental impact.</p>
    <p>Our mission is to make sustainable living accessible and affordable for everyone.</p>
    <a href="/">← Back to Home</a>
    '''

if __name__ == '__main__':
    print("🌱 EcoShop Website Starting...")
    print("🌐 Open your browser and go to: http://localhost:8080")
    print("🛒 Your EcoShop website is ready!")
    app.run(debug=True, host='0.0.0.0', port=8080)
