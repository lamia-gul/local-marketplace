from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "loci_secret_key_123"  # Required for flash messages and sessions

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database setup
DATABASE = 'loci_marketplace.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create user_locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create stores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            store_name TEXT NOT NULL,
            business_email TEXT NOT NULL,
            category TEXT,
            description TEXT,
            store_url TEXT,
            bank_account_number TEXT,
            routing_number TEXT,
            city TEXT,
            state TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def save_user_location(session_id, address):
    """Save or update user location in database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_locations (session_id, address, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(session_id)
        DO UPDATE SET address=?, updated_at=?
    ''', (session_id, address, datetime.now(), address, datetime.now()))

    conn.commit()
    conn.close()

def get_user_location(session_id):
    """Retrieve user location from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT address FROM user_locations WHERE session_id = ?', (session_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None

def save_store(session_id, store_data):
    """Save or update store information in database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO stores (session_id, store_name, business_email, category, description,
                           store_url, bank_account_number, routing_number, city, state, location, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id)
        DO UPDATE SET
            store_name=?, business_email=?, category=?, description=?,
            store_url=?, bank_account_number=?, routing_number=?,
            city=?, state=?, location=?, updated_at=?
    ''', (
        session_id, store_data['store_name'], store_data['business_email'],
        store_data.get('category'), store_data.get('description'),
        store_data.get('store_url'), store_data.get('bank_account_number'),
        store_data.get('routing_number'), store_data.get('city'),
        store_data.get('state'), store_data.get('location'), datetime.now(),
        # For UPDATE clause
        store_data['store_name'], store_data['business_email'],
        store_data.get('category'), store_data.get('description'),
        store_data.get('store_url'), store_data.get('bank_account_number'),
        store_data.get('routing_number'), store_data.get('city'),
        store_data.get('state'), store_data.get('location'), datetime.now()
    ))

    conn.commit()
    conn.close()

def get_store(session_id):
    """Retrieve store information from database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM stores WHERE session_id = ?', (session_id,))
    result = cursor.fetchone()

    conn.close()
    return dict(result) if result else None

# Initialize database on startup
init_db()

# 10 Main Categories with Descriptions and Profile Images
CATEGORIES = [
    {
        "id": 1,
        "name": "Groceries",
        "slug": "groceries",
        "icon": "🛒",
        "color": "#10B981",
        "description": "The Art of Freshness. Hand-selected organic produce and daily essentials delivered from local farms to your kitchen.",
        "profile_image": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=1200&h=800&fit=crop"
    },
    {
        "id": 2,
        "name": "Electronics",
        "slug": "electronics",
        "icon": "📱",
        "color": "#3B82F6",
        "description": "Future Forward. Discover cutting-edge technology and minimalist gadgets designed to elevate your digital life.",
        "profile_image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1200&h=800&fit=crop"
    },
    {
        "id": 3,
        "name": "Health & Beauty",
        "slug": "health-beauty",
        "icon": "💄",
        "color": "#EC4899",
        "description": "Pure Radiance. Premium skincare and wellness rituals crafted with clean ingredients for a glowing lifestyle.",
        "profile_image": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=1200&h=800&fit=crop"
    },
    {
        "id": 4,
        "name": "Home & Life Style",
        "slug": "home-lifestyle",
        "icon": "🏠",
        "color": "#F59E0B",
        "description": "Curated Comfort. Transform your space with artisanal decor and functional design that speaks to your soul.",
        "profile_image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=1200&h=800&fit=crop"
    },
    {
        "id": 5,
        "name": "Stationery & Craft",
        "slug": "stationery-craft",
        "icon": "✏️",
        "color": "#8B5CF6",
        "description": "Creative Soul. High-quality tools and textured papers for those who still believe in the magic of a handwritten note.",
        "profile_image": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1200&h=800&fit=crop"
    },
    {
        "id": 6,
        "name": "Kids",
        "slug": "kids",
        "icon": "🧸",
        "color": "#F472B6",
        "description": "Joyful Discovery. Sustainably made wooden toys and modern essentials for the next generation of explorers.",
        "profile_image": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=1200&h=800&fit=crop"
    },
    {
        "id": 7,
        "name": "Men's Care",
        "slug": "mens-care",
        "icon": "🧴",
        "color": "#6366F1",
        "description": "The Modern Ritual. Sophisticated grooming and fragrance collections for the man who values precision.",
        "profile_image": "https://images.unsplash.com/photo-1621607512214-68297480165e?w=1200&h=800&fit=crop"
    },
    {
        "id": 8,
        "name": "Men's Fashion",
        "slug": "mens-fashion",
        "icon": "👔",
        "color": "#14B8A6",
        "description": "Timeless Style. Sharp tailoring and premium fabrics that define modern masculine elegance.",
        "profile_image": "https://images.unsplash.com/photo-1523398002811-999ca8dec234?w=1200&h=800&fit=crop"
    },
    {
        "id": 9,
        "name": "Mother & Baby",
        "slug": "mother-baby",
        "icon": "👶",
        "color": "#F59E0B",
        "description": "Gentle Beginnings. Soft-textured apparel and nursery essentials designed with the utmost care for new chapters.",
        "profile_image": "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=1200&h=800&fit=crop"
    },
    {
        "id": 10,
        "name": "Sports & Outdoor",
        "slug": "sports-outdoor",
        "icon": "⚽",
        "color": "#EF4444",
        "description": "Peak Performance. Sleek athletic gear and outdoor equipment for those who find their rhythm in motion.",
        "profile_image": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1200&h=800&fit=crop"
    }
]

# Organized Products by Category (12 products per category)
PRODUCTS_BY_CATEGORY = {
    "groceries": [
        {"id": 1, "name": "Artisanal Sourdough Loaf", "price": "8.99", "old_price": "12.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=400&h=533&fit=crop", "store": "Organic Bazaar", "rating": 4.9},
        {"id": 2, "name": "Organic Cold-Pressed Olive Oil", "price": "24.99", "old_price": "34.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&h=533&fit=crop", "store": "Gourmet Store", "rating": 4.8},
        {"id": 3, "name": "Hand-Picked Hass Avocados", "price": "6.99", "old_price": "9.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400&h=533&fit=crop", "store": "Fresh Mart", "rating": 4.7},
        {"id": 4, "name": "Raw Manuka Honey 500g", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1587049352846-4a222e784acc?w=400&h=533&fit=crop", "store": "Organic Bazaar", "rating": 4.9},
        {"id": 5, "name": "Heritage Grain Pasta", "price": "7.99", "old_price": "11.99", "discount": "33%", "image": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=533&fit=crop", "store": "Gourmet Store", "rating": 4.6},
        {"id": 6, "name": "Grass-Fed Butter 250g", "price": "9.99", "old_price": "13.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400&h=533&fit=crop", "store": "Dairy Fresh", "rating": 4.8},
        {"id": 7, "name": "Himalayan Pink Salt", "price": "12.99", "old_price": "17.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1607672632458-9eb56696346b?w=400&h=533&fit=crop", "store": "Gourmet Store", "rating": 4.7},
        {"id": 8, "name": "Organic Quinoa 1kg", "price": "14.99", "old_price": "19.99", "discount": "25%", "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=533&fit=crop", "store": "Organic Bazaar", "rating": 4.8},
        {"id": 9, "name": "Wild-Caught Salmon Fillet", "price": "28.99", "old_price": "38.99", "discount": "26%", "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=533&fit=crop", "store": "Seafood Market", "rating": 4.9},
        {"id": 10, "name": "Aged Balsamic Vinegar", "price": "18.99", "old_price": "26.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1608818434003-1a7c2b9f8b8e?w=400&h=533&fit=crop", "store": "Gourmet Store", "rating": 4.8},
        {"id": 11, "name": "Free-Range Organic Eggs", "price": "8.99", "old_price": "12.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400&h=533&fit=crop", "store": "Farm Direct", "rating": 4.7},
        {"id": 12, "name": "Artisan Dark Chocolate 70%", "price": "11.99", "old_price": "16.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1511381939415-e44015466834?w=400&h=533&fit=crop", "store": "Gourmet Store", "rating": 4.9}
    ],
    "electronics": [
        {"id": 25, "name": "Acoustic Noise-Canceling Headphones", "price": "299.99", "old_price": "399.99", "discount": "25%", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=533&fit=crop", "store": "Tech Corner", "rating": 4.9},
        {"id": 26, "name": "Ultra-Slim Wireless Charger", "price": "49.99", "old_price": "69.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1591290619762-c588f0e8e23a?w=400&h=533&fit=crop", "store": "Gadget World", "rating": 4.7},
        {"id": 27, "name": "4K Portable Monitor 15.6\"", "price": "349.99", "old_price": "499.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&h=533&fit=crop", "store": "Tech Corner", "rating": 4.8},
        {"id": 28, "name": "Minimalist Mechanical Keyboard", "price": "159.99", "old_price": "219.99", "discount": "27%", "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=533&fit=crop", "store": "Gamer Zone", "rating": 4.8},
        {"id": 29, "name": "Precision Wireless Mouse", "price": "79.99", "old_price": "109.99", "discount": "27%", "image": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400&h=533&fit=crop", "store": "Tech Corner", "rating": 4.6},
        {"id": 30, "name": "USB-C Multi-Port Hub", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=400&h=533&fit=crop", "store": "Connector Store", "rating": 4.7},
        {"id": 31, "name": "Leather Phone Case Premium", "price": "39.99", "old_price": "59.99", "discount": "33%", "image": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&h=533&fit=crop", "store": "Mobile Accessories", "rating": 4.5},
        {"id": 32, "name": "Power Bank 30000mAh", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400&h=533&fit=crop", "store": "Battery Plus", "rating": 4.8},
        {"id": 33, "name": "Smart LED Desk Lamp", "price": "69.99", "old_price": "99.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=533&fit=crop", "store": "Lighting Store", "rating": 4.7},
        {"id": 34, "name": "4K Webcam with Ring Light", "price": "149.99", "old_price": "199.99", "discount": "25%", "image": "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=400&h=533&fit=crop", "store": "Video Tech", "rating": 4.8},
        {"id": 35, "name": "Bluetooth Speaker Waterproof", "price": "129.99", "old_price": "179.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=533&fit=crop", "store": "Audio Pro", "rating": 4.9},
        {"id": 36, "name": "Portable SSD 2TB", "price": "249.99", "old_price": "349.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400&h=533&fit=crop", "store": "Storage Pro", "rating": 4.9}
    ]
}

# Add remaining categories with premium products
PRODUCTS_BY_CATEGORY["health-beauty"] = [
    {"id": 37, "name": "Silk Foundation SPF 30", "price": "48.99", "old_price": "68.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=400&h=533&fit=crop", "store": "Beauty Haven", "rating": 4.9},
    {"id": 38, "name": "Velvet Matte Primer", "price": "36.99", "old_price": "52.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=400&h=533&fit=crop", "store": "Glow Studio", "rating": 4.8},
    {"id": 39, "name": "Hyaluronic Acid Serum", "price": "54.99", "old_price": "79.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=533&fit=crop", "store": "Skin Lab", "rating": 4.9},
    {"id": 40, "name": "Mineral Blush Palette", "price": "42.99", "old_price": "59.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400&h=533&fit=crop", "store": "Beauty Haven", "rating": 4.7},
    {"id": 41, "name": "Vitamin C Brightening Cream", "price": "62.99", "old_price": "89.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=533&fit=crop", "store": "Skin Lab", "rating": 4.8},
    {"id": 42, "name": "Luxury Face Oil Blend", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&h=533&fit=crop", "store": "Pure Essence", "rating": 4.9},
    {"id": 43, "name": "Retinol Night Serum", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400&h=533&fit=crop", "store": "Skin Lab", "rating": 4.9},
    {"id": 44, "name": "Rose Water Toner", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1571875257727-256c39da42af?w=400&h=533&fit=crop", "store": "Pure Essence", "rating": 4.6},
    {"id": 45, "name": "Clay Detox Face Mask", "price": "38.99", "old_price": "54.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400&h=533&fit=crop", "store": "Skin Lab", "rating": 4.7},
    {"id": 46, "name": "Luxury Lipstick Collection", "price": "52.99", "old_price": "74.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400&h=533&fit=crop", "store": "Beauty Haven", "rating": 4.8},
    {"id": 47, "name": "Micellar Cleansing Water", "price": "28.99", "old_price": "39.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=533&fit=crop", "store": "Pure Essence", "rating": 4.7},
    {"id": 48, "name": "Collagen Eye Cream", "price": "58.99", "old_price": "82.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400&h=533&fit=crop", "store": "Skin Lab", "rating": 4.8}
]

PRODUCTS_BY_CATEGORY["home-lifestyle"] = [
    {"id": 49, "name": "Ceramic Vase Minimalist", "price": "45.99", "old_price": "64.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1578500494198-246f612d3b3d?w=400&h=533&fit=crop", "store": "Home Atelier", "rating": 4.8},
    {"id": 50, "name": "Scented Soy Candle Set", "price": "38.99", "old_price": "54.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1602874801006-e24b3a31c3b7?w=400&h=533&fit=crop", "store": "Cozy Living", "rating": 4.9},
    {"id": 51, "name": "Linen Throw Blanket", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1631679706909-1844bbd07221?w=400&h=533&fit=crop", "store": "Textile House", "rating": 4.7},
    {"id": 52, "name": "Wooden Wall Clock Modern", "price": "52.99", "old_price": "74.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=400&h=533&fit=crop", "store": "Home Atelier", "rating": 4.6},
    {"id": 53, "name": "Marble Serving Tray", "price": "42.99", "old_price": "59.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1615486511484-92e172cc4fe0?w=400&h=533&fit=crop", "store": "Kitchen Luxe", "rating": 4.8},
    {"id": 54, "name": "Velvet Cushion Cover Set", "price": "34.99", "old_price": "49.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=400&h=533&fit=crop", "store": "Textile House", "rating": 4.7},
    {"id": 55, "name": "Brass Table Lamp", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400&h=533&fit=crop", "store": "Light & Co", "rating": 4.9},
    {"id": 56, "name": "Rattan Storage Basket", "price": "36.99", "old_price": "52.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=400&h=533&fit=crop", "store": "Home Atelier", "rating": 4.6},
    {"id": 57, "name": "Abstract Art Print Framed", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1513519245088-0e12902e35ca?w=400&h=533&fit=crop", "store": "Gallery Home", "rating": 4.8},
    {"id": 58, "name": "Ceramic Dinnerware Set", "price": "124.99", "old_price": "179.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=400&h=533&fit=crop", "store": "Kitchen Luxe", "rating": 4.9},
    {"id": 59, "name": "Macrame Wall Hanging", "price": "48.99", "old_price": "68.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1595815771614-ade9d652a65d?w=400&h=533&fit=crop", "store": "Boho Decor", "rating": 4.7},
    {"id": 60, "name": "Glass Terrarium Planter", "price": "42.99", "old_price": "59.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=400&h=533&fit=crop", "store": "Green Space", "rating": 4.8}
]

PRODUCTS_BY_CATEGORY["stationery-craft"] = [
    {"id": 61, "name": "Leather Journal Handcrafted", "price": "42.99", "old_price": "59.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=400&h=533&fit=crop", "store": "Paper & Co", "rating": 4.9},
    {"id": 62, "name": "Fountain Pen Gold Nib", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&h=533&fit=crop", "store": "Write Studio", "rating": 4.8},
    {"id": 63, "name": "Watercolor Paint Set Professional", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=533&fit=crop", "store": "Art Supply", "rating": 4.7},
    {"id": 64, "name": "Calligraphy Brush Set", "price": "52.99", "old_price": "74.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1604869515882-4d10fa4b0492?w=400&h=533&fit=crop", "store": "Ink & Brush", "rating": 4.8},
    {"id": 65, "name": "Washi Tape Collection 24pcs", "price": "28.99", "old_price": "39.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1606127093329-59d69b90d4e4?w=400&h=533&fit=crop", "store": "Craft Corner", "rating": 4.6},
    {"id": 66, "name": "Bullet Journal Dotted", "price": "24.99", "old_price": "34.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=400&h=533&fit=crop", "store": "Paper & Co", "rating": 4.9},
    {"id": 67, "name": "Acrylic Paint Markers Set", "price": "38.99", "old_price": "54.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=400&h=533&fit=crop", "store": "Art Supply", "rating": 4.7},
    {"id": 68, "name": "Origami Paper Premium", "price": "18.99", "old_price": "26.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=533&fit=crop", "store": "Craft Corner", "rating": 4.5},
    {"id": 69, "name": "Sketch Pencil Set 24pcs", "price": "45.99", "old_price": "64.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1452860606245-08befc0ff44b?w=400&h=533&fit=crop", "store": "Art Supply", "rating": 4.8},
    {"id": 70, "name": "Embossing Tool Kit", "price": "62.99", "old_price": "89.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=400&h=533&fit=crop", "store": "Craft Corner", "rating": 4.7},
    {"id": 71, "name": "Metallic Gel Pen Set", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1565022536102-b2f7b9e5d6b0?w=400&h=533&fit=crop", "store": "Write Studio", "rating": 4.6},
    {"id": 72, "name": "Scrapbook Album Leather", "price": "54.99", "old_price": "76.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=400&h=533&fit=crop", "store": "Paper & Co", "rating": 4.8}
]

PRODUCTS_BY_CATEGORY["kids"] = [
    {"id": 73, "name": "Wooden Building Blocks Set", "price": "48.99", "old_price": "68.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=533&fit=crop", "store": "Little Explorers", "rating": 4.9},
    {"id": 74, "name": "Organic Cotton Teddy Bear", "price": "38.99", "old_price": "54.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1560582861-45078880e48e?w=400&h=533&fit=crop", "store": "Toy Haven", "rating": 4.8},
    {"id": 75, "name": "Educational Puzzle Set", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400&h=533&fit=crop", "store": "Smart Kids", "rating": 4.7},
    {"id": 76, "name": "Wooden Train Set Classic", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400&h=533&fit=crop", "store": "Little Explorers", "rating": 4.9},
    {"id": 77, "name": "Kids Art Easel Adjustable", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1611689342806-0863700ce1e4?w=400&h=533&fit=crop", "store": "Creative Kids", "rating": 4.6},
    {"id": 78, "name": "Plush Dinosaur Collection", "price": "42.99", "old_price": "59.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1567358621394-b7a60c6e8f44?w=400&h=533&fit=crop", "store": "Toy Haven", "rating": 4.8},
    {"id": 79, "name": "Musical Instrument Set Kids", "price": "54.99", "old_price": "76.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=400&h=533&fit=crop", "store": "Little Explorers", "rating": 4.7},
    {"id": 80, "name": "Wooden Rocking Horse", "price": "124.99", "old_price": "179.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400&h=533&fit=crop", "store": "Classic Toys", "rating": 4.9},
    {"id": 81, "name": "Kids Science Experiment Kit", "price": "58.99", "old_price": "82.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1603354350317-6f7aaa5911c5?w=400&h=533&fit=crop", "store": "Smart Kids", "rating": 4.8},
    {"id": 82, "name": "Soft Play Mat Foam", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1584835907355-5175f8f6f0a8?w=400&h=533&fit=crop", "store": "Baby Comfort", "rating": 4.7},
    {"id": 83, "name": "Wooden Dollhouse Victorian", "price": "149.99", "old_price": "209.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1587912781766-c2c0421e3c24?w=400&h=533&fit=crop", "store": "Classic Toys", "rating": 4.9},
    {"id": 84, "name": "Kids Backpack Personalized", "price": "36.99", "old_price": "52.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=533&fit=crop", "store": "Little Explorers", "rating": 4.6}
]

PRODUCTS_BY_CATEGORY["mens-care"] = [
    {"id": 85, "name": "Sandalwood Beard Oil", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1621607512214-68297480165e?w=400&h=533&fit=crop", "store": "Gentleman's Club", "rating": 4.9},
    {"id": 86, "name": "Premium Shaving Kit", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1623654985803-c511d77b2d7c?w=400&h=533&fit=crop", "store": "Barber & Co", "rating": 4.8},
    {"id": 87, "name": "Charcoal Face Wash", "price": "28.99", "old_price": "39.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=533&fit=crop", "store": "Men's Grooming", "rating": 4.7},
    {"id": 88, "name": "Cologne Woody Notes 100ml", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400&h=533&fit=crop", "store": "Fragrance House", "rating": 4.9},
    {"id": 89, "name": "Anti-Aging Eye Cream Men", "price": "48.99", "old_price": "68.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1617897903246-719242758050?w=400&h=533&fit=crop", "store": "Men's Grooming", "rating": 4.6},
    {"id": 90, "name": "Beard Grooming Kit Complete", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1635274994902-b2986f0ad60c?w=400&h=533&fit=crop", "store": "Gentleman's Club", "rating": 4.8},
    {"id": 91, "name": "Moisturizer SPF 30 Men", "price": "38.99", "old_price": "54.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=533&fit=crop", "store": "Men's Grooming", "rating": 4.7},
    {"id": 92, "name": "Hair Styling Pomade", "price": "24.99", "old_price": "34.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=400&h=533&fit=crop", "store": "Barber & Co", "rating": 4.8},
    {"id": 93, "name": "Aftershave Balm Soothing", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400&h=533&fit=crop", "store": "Gentleman's Club", "rating": 4.7},
    {"id": 94, "name": "Body Wash Activated Charcoal", "price": "22.99", "old_price": "32.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&h=533&fit=crop", "store": "Men's Grooming", "rating": 4.6},
    {"id": 95, "name": "Luxury Shaving Cream", "price": "28.99", "old_price": "39.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1631730486572-226d1f595b68?w=400&h=533&fit=crop", "store": "Barber & Co", "rating": 4.8},
    {"id": 96, "name": "Deodorant Natural Aluminum-Free", "price": "18.99", "old_price": "26.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1615397349754-cfa2066a298e?w=400&h=533&fit=crop", "store": "Men's Grooming", "rating": 4.5}
]

PRODUCTS_BY_CATEGORY["mens-fashion"] = [
    {"id": 97, "name": "Slim Fit Oxford Shirt", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400&h=533&fit=crop", "store": "Modern Man", "rating": 4.8},
    {"id": 98, "name": "Italian Leather Belt", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1624222247344-550fb60583bb?w=400&h=533&fit=crop", "store": "Leather Goods", "rating": 4.9},
    {"id": 99, "name": "Tailored Wool Blazer", "price": "249.99", "old_price": "349.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400&h=533&fit=crop", "store": "Suit & Tie", "rating": 4.9},
    {"id": 100, "name": "Cashmere V-Neck Sweater", "price": "128.99", "old_price": "179.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400&h=533&fit=crop", "store": "Luxury Knits", "rating": 4.8},
    {"id": 101, "name": "Chino Pants Slim Fit", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400&h=533&fit=crop", "store": "Modern Man", "rating": 4.7},
    {"id": 102, "name": "Leather Dress Shoes Oxford", "price": "149.99", "old_price": "209.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=400&h=533&fit=crop", "store": "Shoe Gallery", "rating": 4.9},
    {"id": 103, "name": "Silk Tie Collection", "price": "58.99", "old_price": "82.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1589756823695-278bc8356c60?w=400&h=533&fit=crop", "store": "Suit & Tie", "rating": 4.6},
    {"id": 104, "name": "Merino Wool Socks 6-Pack", "price": "42.99", "old_price": "59.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=400&h=533&fit=crop", "store": "Comfort Wear", "rating": 4.7},
    {"id": 105, "name": "Leather Wallet Bifold", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=400&h=533&fit=crop", "store": "Leather Goods", "rating": 4.8},
    {"id": 106, "name": "Denim Jacket Classic", "price": "98.99", "old_price": "139.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=533&fit=crop", "store": "Denim Co", "rating": 4.8},
    {"id": 107, "name": "Polo Shirt Premium Cotton", "price": "54.99", "old_price": "76.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=400&h=533&fit=crop", "store": "Modern Man", "rating": 4.7},
    {"id": 108, "name": "Aviator Sunglasses Polarized", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400&h=533&fit=crop", "store": "Eyewear Studio", "rating": 4.9}
]

PRODUCTS_BY_CATEGORY["mother-baby"] = [
    {"id": 109, "name": "Organic Cotton Baby Onesie Set", "price": "38.99", "old_price": "54.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1519689373023-dd07c7988603?w=400&h=533&fit=crop", "store": "Baby Bliss", "rating": 4.9},
    {"id": 110, "name": "Nursing Pillow Ergonomic", "price": "48.99", "old_price": "68.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1584835907355-5175f8f6f0a8?w=400&h=533&fit=crop", "store": "Mom & Baby", "rating": 4.8},
    {"id": 111, "name": "Baby Carrier Ergonomic", "price": "89.99", "old_price": "129.99", "discount": "31%", "image": "https://images.unsplash.com/photo-1566004100631-35d015d6a491?w=400&h=533&fit=crop", "store": "Baby Comfort", "rating": 4.9},
    {"id": 112, "name": "Muslin Swaddle Blanket Set", "price": "42.99", "old_price": "59.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1522771930-78848d9293e8?w=400&h=533&fit=crop", "store": "Baby Bliss", "rating": 4.7},
    {"id": 113, "name": "Diaper Bag Leather", "price": "98.99", "old_price": "139.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400&h=533&fit=crop", "store": "Mom & Baby", "rating": 4.8},
    {"id": 114, "name": "Baby Monitor Video HD", "price": "149.99", "old_price": "209.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1609902726285-00668009f004?w=400&h=533&fit=crop", "store": "Tech Baby", "rating": 4.9},
    {"id": 115, "name": "Maternity Pillow Full Body", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1631679706909-1844bbd07221?w=400&h=533&fit=crop", "store": "Mom Comfort", "rating": 4.8},
    {"id": 116, "name": "Baby Bottle Sterilizer", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400&h=533&fit=crop", "store": "Baby Care", "rating": 4.7},
    {"id": 117, "name": "Organic Baby Lotion Set", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1608613304899-ea8098577e38?w=400&h=533&fit=crop", "store": "Pure Baby", "rating": 4.9},
    {"id": 118, "name": "Nursing Cover Breathable", "price": "28.99", "old_price": "39.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=400&h=533&fit=crop", "store": "Mom & Baby", "rating": 4.6},
    {"id": 119, "name": "Baby Crib Mobile Musical", "price": "54.99", "old_price": "76.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=400&h=533&fit=crop", "store": "Nursery Decor", "rating": 4.8},
    {"id": 120, "name": "Postpartum Recovery Kit", "price": "58.99", "old_price": "82.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=400&h=533&fit=crop", "store": "Mom Comfort", "rating": 4.7}
]

PRODUCTS_BY_CATEGORY["sports-outdoor"] = [
    {"id": 121, "name": "Yoga Mat Premium Non-Slip", "price": "48.99", "old_price": "68.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=533&fit=crop", "store": "Fitness Pro", "rating": 4.8},
    {"id": 122, "name": "Resistance Bands Set", "price": "32.99", "old_price": "45.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=400&h=533&fit=crop", "store": "Gym Gear", "rating": 4.7},
    {"id": 123, "name": "Running Shoes Lightweight", "price": "128.99", "old_price": "179.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=533&fit=crop", "store": "Athletic Wear", "rating": 4.9},
    {"id": 124, "name": "Camping Tent 4-Person", "price": "189.99", "old_price": "269.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=400&h=533&fit=crop", "store": "Outdoor Gear", "rating": 4.8},
    {"id": 125, "name": "Dumbbell Set Adjustable", "price": "149.99", "old_price": "209.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&h=533&fit=crop", "store": "Gym Gear", "rating": 4.9},
    {"id": 126, "name": "Hiking Backpack 50L", "price": "98.99", "old_price": "139.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1622260614927-9c2e4149e2e5?w=400&h=533&fit=crop", "store": "Outdoor Gear", "rating": 4.8},
    {"id": 127, "name": "Sports Water Bottle Insulated", "price": "28.99", "old_price": "39.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=533&fit=crop", "store": "Fitness Pro", "rating": 4.6},
    {"id": 128, "name": "Cycling Gloves Padded", "price": "38.99", "old_price": "54.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400&h=533&fit=crop", "store": "Bike Shop", "rating": 4.7},
    {"id": 129, "name": "Foam Roller Massage", "price": "34.99", "old_price": "49.99", "discount": "30%", "image": "https://images.unsplash.com/photo-1611672585731-fa10603fb9e0?w=400&h=533&fit=crop", "store": "Fitness Pro", "rating": 4.8},
    {"id": 130, "name": "Sleeping Bag Lightweight", "price": "78.99", "old_price": "109.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1487730116645-74489c95b41b?w=400&h=533&fit=crop", "store": "Outdoor Gear", "rating": 4.7},
    {"id": 131, "name": "Jump Rope Speed Training", "price": "24.99", "old_price": "34.99", "discount": "29%", "image": "https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=400&h=533&fit=crop", "store": "Gym Gear", "rating": 4.6},
    {"id": 132, "name": "Trekking Poles Carbon Fiber", "price": "68.99", "old_price": "95.99", "discount": "28%", "image": "https://images.unsplash.com/photo-1551632811-561732d1e306?w=400&h=533&fit=crop", "store": "Outdoor Gear", "rating": 4.9}
]

# Legacy products list for backward compatibility
products = PRODUCTS_BY_CATEGORY["groceries"][:4]

@app.route('/')
def search_gate():
    # Generate or retrieve session ID
    if 'session_id' not in session:
        session['session_id'] = os.urandom(24).hex()

    # Check if user has a saved location in database
    saved_location = get_user_location(session['session_id'])
    if saved_location:
        session['user_location'] = saved_location
        return redirect(url_for('home'))

    # If user already has a location in session, redirect to home
    if 'user_location' in session:
        return redirect(url_for('home'))

    return render_template('search_gate.html')

@app.route('/set-location', methods=['POST'])
def set_location():
    # Handle both old address field and new city/country fields
    address = request.form.get('address')
    city = request.form.get('city')
    country = request.form.get('country')

    # Prefer city/country format if available
    if city and country:
        location = f"{city}, {country}"
    elif address:
        location = address
    else:
        location = "Karachi, Pakistan"  # Default fallback

    if location:
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = os.urandom(24).hex()

        # Save to session
        session['user_location'] = location
        session['user_city'] = city if city else location.split(',')[0].strip()
        session['user_country'] = country if country else 'Pakistan'

        # Save to database for persistence
        save_user_location(session['session_id'], location)

        flash(f"Location set to: {location}", "success")

    return redirect(url_for('home'))

@app.route('/home')
def home():
    user_location = session.get('user_location', None)
    user_city = session.get('user_city', 'Karachi')
    user_name = session.get('user_name', None)
    is_logged_in = session.get('is_logged_in', False)

    # Karachi-specific mock data with neighborhoods
    karachi_stores = [
        {"name": "Fresh Mart Gulshan", "area": "Gulshan-e-Iqbal", "status": "Open", "category": "Groceries"},
        {"name": "Style Hub DHA", "area": "DHA Phase 5", "status": "Open", "category": "Fashion"},
        {"name": "Tech Corner Clifton", "area": "Clifton Block 2", "status": "Open", "category": "Electronics"},
        {"name": "Organic Bazaar Gulshan", "area": "Gulshan-e-Iqbal", "status": "Open", "category": "Groceries"},
        {"name": "Fashion Street DHA", "area": "DHA Phase 6", "status": "Open", "category": "Fashion"},
    ]

    # Mock trending products data with Karachi neighborhoods
    all_products = [
        {
            "id": 1,
            "name": "Organic Fresh Tomatoes",
            "price": "120.00",
            "original_price": "180.00",
            "discount": "33%",
            "image_url": "images/product_1.jpg",
            "category": "Groceries",
            "rating": 4.8,
            "city": "Karachi",
            "area": "Gulshan-e-Iqbal",
            "store": "Fresh Mart Gulshan"
        },
        {
            "id": 2,
            "name": "Premium Cotton T-Shirt",
            "price": "899.00",
            "original_price": "1499.00",
            "discount": "40%",
            "image_url": "images/product_2.jpg",
            "category": "Fashion",
            "rating": 4.6,
            "city": "Karachi",
            "area": "DHA Phase 5",
            "store": "Style Hub DHA"
        },
        {
            "id": 3,
            "name": "Wireless Bluetooth Earbuds",
            "price": "2499.00",
            "original_price": "4999.00",
            "discount": "50%",
            "image_url": "images/product_3.jpg",
            "category": "Electronics",
            "rating": 4.9,
            "city": "Karachi",
            "area": "Clifton Block 2",
            "store": "Tech Corner Clifton"
        },
        {
            "id": 4,
            "name": "Fresh Basmati Rice 5kg",
            "price": "850.00",
            "original_price": "1100.00",
            "discount": "23%",
            "image_url": "images/product_4.jpg",
            "category": "Groceries",
            "rating": 4.7,
            "city": "Karachi",
            "area": "Gulshan-e-Iqbal",
            "store": "Organic Bazaar Gulshan"
        },
        {
            "id": 5,
            "name": "Designer Leather Wallet",
            "price": "1299.00",
            "original_price": "2199.00",
            "discount": "41%",
            "image_url": "images/product_1.jpg",
            "category": "Fashion",
            "rating": 4.5,
            "city": "Karachi",
            "area": "DHA Phase 6",
            "store": "Fashion Street DHA"
        },
        {
            "id": 6,
            "name": "Smart Watch Series 5",
            "price": "8999.00",
            "original_price": "14999.00",
            "discount": "40%",
            "image_url": "images/product_2.jpg",
            "category": "Electronics",
            "rating": 4.8,
            "city": "Karachi",
            "area": "Clifton Block 2",
            "store": "Tech Corner Clifton"
        },
        {
            "id": 7,
            "name": "Organic Honey 500g",
            "price": "650.00",
            "original_price": "850.00",
            "discount": "24%",
            "image_url": "images/product_3.jpg",
            "category": "Groceries",
            "rating": 4.9,
            "city": "Karachi",
            "area": "Gulshan-e-Iqbal",
            "store": "Fresh Mart Gulshan"
        },
        {
            "id": 8,
            "name": "Running Shoes Pro",
            "price": "3499.00",
            "original_price": "5999.00",
            "discount": "42%",
            "image_url": "images/product_4.jpg",
            "category": "Fashion",
            "rating": 4.7,
            "city": "Karachi",
            "area": "DHA Phase 5",
            "store": "Style Hub DHA"
        },
        # Products from other cities for comparison
        {
            "id": 9,
            "name": "Fresh Mangoes 1kg",
            "price": "450.00",
            "original_price": "600.00",
            "discount": "25%",
            "image_url": "images/product_1.jpg",
            "category": "Groceries",
            "rating": 4.6,
            "city": "Lahore",
            "area": "Gulberg",
            "store": "Fruit Market Lahore"
        },
        {
            "id": 10,
            "name": "Laptop Stand Aluminum",
            "price": "1899.00",
            "original_price": "2999.00",
            "discount": "37%",
            "image_url": "images/product_2.jpg",
            "category": "Electronics",
            "rating": 4.7,
            "city": "Islamabad",
            "area": "F-7 Markaz",
            "store": "Tech Hub Islamabad"
        }
    ]

    # Filter products by user's city
    if user_city:
        trending_products = [p for p in all_products if p['city'] == user_city]
        # If no products found in user's city, show Karachi products as fallback
        if not trending_products:
            trending_products = [p for p in all_products if p['city'] == 'Karachi']
            location_display = f"Popular in Karachi (No products available in {user_city} yet)"
        else:
            location_display = user_location if user_location else f"{user_city}, Pakistan"
    else:
        # No location set, show Karachi products
        trending_products = [p for p in all_products if p['city'] == 'Karachi']
        location_display = "Popular in Karachi"

    return render_template('index.html',
                         user_location=location_display,
                         user_city=user_city,
                         user_name=user_name,
                         is_logged_in=is_logged_in,
                         show_search_bar=True,
                         trending_products=trending_products,
                         karachi_stores=karachi_stores,
                         has_location=bool(user_location))

@app.route('/store')
def store():
    # Shabs Cuisine - Food product catalog
    store_products = [
        # Frozen Items
        {"name": "Chicken Samosa (12 pcs)", "category": "frozen", "price": 8.99, "old_price": 12.99, "discount": 31, "rating": 4.8, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Samosa"},
        {"name": "Beef Samosa (12 pcs)", "category": "frozen", "price": 9.99, "old_price": 13.99, "discount": 29, "rating": 4.7, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Beef+Samosa"},
        {"name": "Vegetable Spring Rolls (15 pcs)", "category": "frozen", "price": 7.99, "old_price": 10.99, "discount": 27, "rating": 4.5, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Spring+Rolls"},
        {"name": "Chicken Nuggets (20 pcs)", "category": "frozen", "price": 11.99, "old_price": 15.99, "discount": 25, "rating": 4.6, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Nuggets"},
        {"name": "Frozen Paratha (10 pcs)", "category": "frozen", "price": 6.99, "old_price": 9.99, "discount": 30, "rating": 4.9, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Paratha"},
        {"name": "Chicken Seekh Kebab (8 pcs)", "category": "frozen", "price": 12.99, "old_price": 16.99, "discount": 24, "rating": 4.7, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Kebab"},
        {"name": "Frozen Biryani Pack (2 servings)", "category": "frozen", "price": 14.99, "old_price": 19.99, "discount": 25, "rating": 4.8, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Biryani"},
        {"name": "Frozen Naan Bread (6 pcs)", "category": "frozen", "price": 5.99, "old_price": 8.99, "discount": 33, "rating": 4.4, "image": "https://via.placeholder.com/300x250/8B4789/ffffff?text=Naan"},

        # Fresh Items
        {"name": "Fresh Chicken Tikka (500g)", "category": "fresh", "price": 13.99, "old_price": 17.99, "discount": 22, "rating": 4.9, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Tikka"},
        {"name": "Fresh Marinated Wings (1kg)", "category": "fresh", "price": 15.99, "old_price": 20.99, "discount": 24, "rating": 4.7, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Wings"},
        {"name": "Fresh Raita (500ml)", "category": "fresh", "price": 4.99, "old_price": 6.99, "discount": 29, "rating": 4.5, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Raita"},
        {"name": "Fresh Mint Chutney (250ml)", "category": "fresh", "price": 3.99, "old_price": 5.99, "discount": 33, "rating": 4.6, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Chutney"},
        {"name": "Fresh Tandoori Chicken (whole)", "category": "fresh", "price": 18.99, "old_price": 24.99, "discount": 24, "rating": 4.8, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Tandoori"},
        {"name": "Fresh Salad Bowl", "category": "fresh", "price": 6.99, "old_price": 9.99, "discount": 30, "rating": 4.4, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Salad"},
        {"name": "Fresh Gulab Jamun (6 pcs)", "category": "fresh", "price": 7.99, "old_price": 10.99, "discount": 27, "rating": 4.9, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Gulab+Jamun"},
        {"name": "Fresh Lassi (1L)", "category": "fresh", "price": 5.99, "old_price": 8.99, "discount": 33, "rating": 4.7, "image": "https://via.placeholder.com/300x250/E67E22/ffffff?text=Lassi"},

        # Platters
        {"name": "Family BBQ Platter", "category": "platters", "price": 49.99, "old_price": 69.99, "discount": 29, "rating": 4.9, "image": "https://via.placeholder.com/300x250/27AE60/ffffff?text=BBQ+Platter"},
        {"name": "Appetizer Platter", "category": "platters", "price": 29.99, "old_price": 39.99, "discount": 25, "rating": 4.7, "image": "https://via.placeholder.com/300x250/27AE60/ffffff?text=Appetizer"},
        {"name": "Biryani Party Platter (serves 8)", "category": "platters", "price": 59.99, "old_price": 79.99, "discount": 25, "rating": 4.8, "image": "https://via.placeholder.com/300x250/27AE60/ffffff?text=Biryani+Platter"},
        {"name": "Dessert Platter", "category": "platters", "price": 24.99, "old_price": 34.99, "discount": 29, "rating": 4.6, "image": "https://via.placeholder.com/300x250/27AE60/ffffff?text=Dessert"},
        {"name": "Kebab Platter (mixed)", "category": "platters", "price": 39.99, "old_price": 54.99, "discount": 27, "rating": 4.8, "image": "https://via.placeholder.com/300x250/27AE60/ffffff?text=Kebab+Platter"},
        {"name": "Vegetarian Platter", "category": "platters", "price": 34.99, "old_price": 44.99, "discount": 22, "rating": 4.5, "image": "https://via.placeholder.com/300x250/27AE60/ffffff?text=Veg+Platter"},
    ]

    return render_template('store.html', products=store_products)

@app.route('/products')
def product_display():
    # Show top 4 products from each category
    categories_with_products = []
    for category in CATEGORIES:
        category_products = PRODUCTS_BY_CATEGORY.get(category['slug'], [])[:4]  # Top 4 only
        categories_with_products.append({
            'category': category,
            'products': category_products
        })

    return render_template('products.html',
                         categories_with_products=categories_with_products,
                         all_categories=CATEGORIES)

@app.route('/all-categories')
def all_categories():
    return render_template('all_categories.html',
                         categories=CATEGORIES)

@app.route('/category/<slug>')
def category_page(slug):
    # Find the category
    category = next((cat for cat in CATEGORIES if cat['slug'] == slug), None)

    if not category:
        flash("Category not found", "error")
        return redirect(url_for('product_display'))

    # Get all 12 products for this category
    category_products = PRODUCTS_BY_CATEGORY.get(slug, [])

    return render_template('category.html',
                         category=category,
                         products=category_products,
                         all_categories=CATEGORIES)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # Find the product across all categories
    product = None
    product_category = None

    for category_slug, products in PRODUCTS_BY_CATEGORY.items():
        for p in products:
            if p['id'] == product_id:
                product = p
                product_category = next((cat for cat in CATEGORIES if cat['slug'] == category_slug), None)
                break
        if product:
            break

    if not product:
        flash("Product not found", "error")
        return redirect(url_for('product_display'))

    return render_template('product-detail.html',
                         product=product,
                         category=product_category,
                         all_categories=CATEGORIES)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Print contact form data to terminal
        print("\n" + "="*50)
        print("CONTACT FORM SUBMISSION")
        print("="*50)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("="*50 + "\n")

        flash("Thank you for contacting us! We'll get back to you soon.", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/help')
def help_center():
    return render_template('help.html')

@app.route('/shipping')
def shipping():
    return render_template('shipping.html')

@app.route('/returns')
def returns():
    return render_template('returns.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form.get('email')
    if email:
        # Here you would typically save to database or send to email service
        print(f"Newsletter subscription: {email}")
        flash(f"Thank you for subscribing! We'll send updates to {email}", "success")
    return redirect(request.referrer or url_for('home'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Print registration data to terminal
        print("\n" + "="*50)
        print("NEW USER REGISTRATION")
        print("="*50)
        print(f"Full Name: {fullname}")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {'*' * len(password)}")
        print("="*50 + "\n")

        # Basic validation
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        flash(f"Welcome {fullname}! Your account has been created successfully.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/create-store', methods=['GET', 'POST'])
def create_store():
    if request.method == 'POST':
        # Capture form data
        store_name = request.form.get('store_name')
        business_email = request.form.get('business_email')
        category = request.form.get('category')
        description = request.form.get('description')
        store_url = request.form.get('store_url')
        bank_account_number = request.form.get('bank_account_number')
        routing_number = request.form.get('routing_number')

        # Print data to terminal
        print("\n" + "="*50)
        print("STORE CREATION FORM DATA RECEIVED")
        print("="*50)
        print(f"Store Name: {store_name}")
        print(f"Business Email: {business_email}")
        print(f"Category: {category}")
        print(f"Description: {description}")
        print(f"Store URL: {store_url}")
        print(f"Bank Account Number: {bank_account_number}")
        print(f"Routing Number: {routing_number}")
        print("="*50 + "\n")

        # Get or create session ID
        if 'session_id' not in session:
            import uuid
            session['session_id'] = str(uuid.uuid4())

        # Save store data to database
        store_data = {
            'store_name': store_name,
            'business_email': business_email,
            'category': category,
            'description': description,
            'store_url': store_url,
            'bank_account_number': bank_account_number,
            'routing_number': routing_number,
            'city': 'Karachi',
            'state': 'Sindh',
            'location': 'Karachi, Pakistan'
        }
        save_store(session['session_id'], store_data)

        # Also save to session for quick access
        session['store_name'] = store_name
        session['store_location'] = 'Karachi, Pakistan'

        # Redirect to dashboard after successful submission
        return redirect(url_for('dashboard'))

    return render_template('create_store.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/store-profile')
def store_profile():
    # Get or create session ID
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())

    # Try to get store data from database
    store_data = get_store(session['session_id'])

    # If no store data exists, use default values
    if not store_data:
        store_data = {
            "store_name": session.get('store_name', 'shabs cuisine'),
            "description": "Premium rolls and samosas in Karachi.",
            "business_email": "business@example.com",
            "phone_number": "+92 300 1234567",
            "location": session.get('store_location', 'Karachi, Pakistan'),
            "store_url": "shabs-cuisine",
            "city": "Karachi",
            "state": "Sindh"
        }

    return render_template('store_profile.html', store=store_data)

@app.route('/seller/products')
def seller_products():
    return render_template('my_products.html')

@app.route('/seller/orders')
def seller_orders():
    return render_template('orders.html')

@app.route('/seller/finances')
def seller_finances():
    return render_template('finances.html')

@app.route('/manage-products')
def manage_products():
    return render_template('manage_products.html')

@app.route('/save-product', methods=['POST'])
def save_product():
    # Capture product data
    name = request.form.get('p_name')
    price = request.form.get('p_price')
    category = request.form.get('p_category')
    stock = request.form.get('p_stock')
    description = request.form.get('p_description')

    # Handle product image upload
    image = request.files.get('p_image')
    image_filename = 'No image uploaded'

    if image and image.filename:
        image_filename = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
        print(f"✓ Product Image saved to: {image_path}")

    # Print product details to terminal
    print("\n" + "="*60)
    print("NEW PRODUCT LISTED")
    print("="*60)
    print(f"Product Name: {name}")
    print(f"Category: {category}")
    print(f"Price: ${price}")
    print(f"Stock: {stock} units")
    print(f"Description: {description}")
    print(f"Image: {image_filename}")
    print("="*60 + "\n")

    # Flash success message
    flash(f"Successfully added {name} to your store!", "success")

    return redirect(url_for('manage_products'))

@app.route('/save-store-profile', methods=['POST'])
def save_store_profile():
    # Capture Personal Information fields
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone_no = request.form.get('phone_no')

    # Capture Store Profile data
    store_name = request.form.get('store_name')
    store_description = request.form.get('store_description')
    business_email = request.form.get('business_email')
    phone_number = request.form.get('phone_number')

    # Capture Store Identity
    store_permalink = request.form.get('store_permalink')

    # Capture Store Locator
    street_address = request.form.get('street_address')
    city = request.form.get('city')
    state = request.form.get('state')
    postal_code = request.form.get('postal_code')

    # Capture Financial Information
    acc_number = request.form.get('acc_number')
    acc_title = request.form.get('acc_title')
    routing_number = request.form.get('routing_number')
    tax_id = request.form.get('tax_id')

    # Handle file uploads
    w9_file = request.files.get('w9_pdf')
    w9_filename = 'No file uploaded'

    store_logo = request.files.get('store_logo')
    logo_filename = 'No logo uploaded'

    if w9_file and w9_file.filename:
        w9_filename = w9_file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], w9_filename)
        w9_file.save(file_path)
        print(f"✓ W-9 File saved to: {file_path}")

    if store_logo and store_logo.filename:
        logo_filename = store_logo.filename
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
        store_logo.save(logo_path)
        print(f"✓ Store Logo saved to: {logo_path}")

    # Print data to terminal
    print("\n" + "="*60)
    print("STORE PROFILE DATA RECEIVED")
    print("="*60)
    print("PERSONAL INFORMATION:")
    print(f"User: {first_name} {last_name}")
    print(f"Email: {email}")
    print(f"Phone: {phone_no}")
    print("-" * 60)
    print("STORE DETAILS:")
    print(f"Store Name: {store_name}")
    print(f"Store Description: {store_description}")
    print(f"Business Email: {business_email}")
    print(f"Phone Number: {phone_number}")
    print("-" * 60)
    print("STORE IDENTITY:")
    print(f"Store Permalink: {store_permalink}")
    print(f"Store Logo: {logo_filename}")
    print("-" * 60)
    print("STORE LOCATOR:")
    print(f"Address: {street_address}")
    print(f"City: {city}")
    print(f"State: {state}")
    print(f"Postal Code: {postal_code}")
    print("-" * 60)
    print("FINANCIAL INFORMATION:")
    print(f"Account Number: {acc_number}")
    print(f"Account Title: {acc_title}")
    print(f"Routing Number: {routing_number}")
    print(f"Tax ID: {tax_id}")
    print(f"W-9 Form: {w9_filename}")
    print("="*60 + "\n")

    # Get or create session ID
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())

    # Save store data to database
    location = f"{city}, {state}" if city and state else "Karachi, Pakistan"
    store_data = {
        'store_name': store_name,
        'business_email': business_email,
        'category': None,  # Can be added later
        'description': store_description,
        'store_url': store_permalink,
        'bank_account_number': acc_number,
        'routing_number': routing_number,
        'city': city,
        'state': state,
        'location': location
    }
    save_store(session['session_id'], store_data)

    # Update session
    session['store_name'] = store_name
    session['store_location'] = location

    # Flash success message
    flash("Store Profile Updated Successfully!", "success")

    # Redirect to dashboard
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
