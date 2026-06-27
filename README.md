# 👟 SoleStyle - Online Shoe Store

A modern, full-featured e-commerce platform for selling shoes online. Built with Flask and SQLAlchemy.

## ✨ Features

### Customer Features
- 🛍️ Browse products by category (Men, Women, Kids)
- 🔍 Search and filter by price/rating
- ❤️ Wishlist management
- 🛒 Shopping cart with quantity management
- 📦 Checkout and order management
- ⭐ Product reviews and ratings
- 👤 User authentication and profile management

### Admin Features
- 📊 Admin dashboard with analytics
- 📈 Revenue tracking (daily/monthly)
- 📉 Profit margin analysis
- 📦 Stock management and tracking
- 📋 Order management and tracking
- 👥 Customer management
- 🏭 Supplier and purchase management
- 💹 Cost of Goods Sold (COGS) calculation

### Technical Features
- ✅ Full-featured product management
- ✅ Stock movement tracking (purchases, sales, cancellations)
- ✅ User authentication with Flask-Login
- ✅ Database-backed shopping cart
- ✅ Order history and status tracking
- ✅ RESTful API endpoints
- ✅ Responsive design ready
- ✅ BDT/USD price display

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 3.0.0 |
| **Database ORM** | SQLAlchemy |
| **User Management** | Flask-Login |
| **Web Server** | Gunicorn (production) |
| **Database** | PostgreSQL (production) / SQLite (dev) |
| **Security** | Werkzeug (password hashing) |

---

## 📋 Project Structure

```
solestyle/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── requirements.txt          # Python dependencies
├── seed_sample_data.py       # Sample data seeder
├── Procfile                  # Deployment config (Render/Heroku)
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── templates/                # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   └── admin/
│       └── dashboard.html
└── static/                   # Static files
    ├── images/               # Product images
    ├── css/                  # Stylesheets
    └── js/                   # JavaScript files
```

---

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone the project
git clone <your-repo-url>
cd solestyle

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# 5. Open browser
# Visit http://localhost:5000
```

**Test accounts:**
- Admin: `admin` / `admin`
- Demo: `demo` / `demo123`

---

## 🌐 Deployment

### Recommended Hosting Platforms

#### 1. **Render.com** ⭐ (Easiest - Free Tier)
- See `QUICK_START.md` for step-by-step guide
- Free tier available
- Auto-deploys from GitHub
- Built-in PostgreSQL support

#### 2. **Railway.app** ⚡ (Very Easy)
- Auto-detects Flask projects
- Simple environment variable setup
- Fast deployment (~1 minute)

#### 3. **DigitalOcean** 💰 ($6+/month)
- Full control and scalability
- Detailed guide in `DEPLOYMENT_GUIDE.md`
- Best for production workloads

#### 4. **Heroku** (Paid - no free tier)
- Classic choice, now requires payment
- Detailed guide in `DEPLOYMENT_GUIDE.md`

### Environment Variables

Create `.env` file (don't commit!):
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///solestyle.db
FLASK_ENV=production
```

For production, use PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@host/dbname
```

---

## 📊 Database Models

### User
- Profile management
- Authentication
- Order history
- Wishlist
- Reviews

### Product
- Name, description, category
- Pricing (price + cost_price for profit margin)
- Stock management
- Ratings and reviews
- Image management
- Sizes and colors (JSON)

### Order & OrderItem
- Complete order tracking
- Shipping information
- Payment details
- Status management (pending, confirmed, shipped, delivered, cancelled)

### Cart & CartItem
- User shopping cart
- Product selections with quantities
- Size/color preferences

### Wishlist
- Save favorite products
- User-specific wishlists

### Stock Management
- Purchase orders
- Stock movements tracking
- Inventory auditing
- COGS calculation

---

## 🔑 API Endpoints

### Public Routes
- `GET /` - Homepage
- `GET /search` - Product search
- `GET /product/<id>` - Product detail
- `GET /login` - Login page
- `GET /register` - Registration page

### Authenticated Routes
- `GET /cart` - View shopping cart
- `POST /api/cart/add` - Add to cart
- `POST /api/cart/remove/<id>` - Remove from cart
- `POST /api/cart/update/<id>` - Update cart quantity
- `GET /checkout` - Checkout page
- `POST /checkout` - Place order
- `GET /orders` - Order history
- `GET /order/<id>` - Order details
- `POST /api/wishlist/add/<id>` - Add to wishlist
- `POST /api/wishlist/remove/<id>` - Remove from wishlist
- `POST /api/product/<id>/review` - Add product review

### Admin Routes
- `GET /admin` - Admin dashboard (requires admin role)

---

## 🔐 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Session-based authentication
- ✅ Login required decorators
- ✅ Admin role verification
- ✅ Environment variable for secret key
- ✅ HTTPS ready (via reverse proxy)

---

## 📈 What's Next?

After deployment:

1. **Add Product Images**
   - Place images in `static/images/`
   - They auto-sync with products

2. **Configure Payment Gateway**
   - Integrate Stripe (international)
   - Integrate Bkash (Bangladesh)
   - Integrate Nagad (Bangladesh)

3. **Email Notifications**
   - Order confirmations
   - Password reset
   - Shipping updates

4. **Analytics & Monitoring**
   - Google Analytics integration
   - Error tracking (Sentry)
   - Performance monitoring

5. **Advanced Features**
   - Product inventory alerts
   - Automated reorder emails
   - Customer reviews moderation
   - Discount codes and coupons
   - Multi-currency support

---

## 🐛 Troubleshooting

### App won't start
```bash
# Check if port 5000 is in use
lsof -i :5000
# Kill the process if needed
kill -9 <PID>
# Try running again
python app.py
```

### Database errors
```bash
# Reset database (development only!)
rm solestyle.db
python app.py
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Virtual environment issues
```bash
# Deactivate and recreate
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 Documentation

- **QUICK_START.md** - Fast setup and deployment guide
- **DEPLOYMENT_GUIDE.md** - Comprehensive deployment documentation
- **Code comments** - Inline documentation in app.py

---

## 🚀 Performance Tips

- SQLite fine for small projects, switch to PostgreSQL for production
- Use Nginx reverse proxy for better performance
- Add CDN for static files (CloudFlare, AWS CloudFront)
- Enable gzip compression in Nginx
- Use connection pooling for database
- Monitor response times and database queries

---

## 📝 License

This project is open source and available for educational purposes.

---

## 💬 Support

For issues and questions:
1. Check troubleshooting section
2. Review deployment guide
3. Check Flask documentation

---

## ✅ Checklist Before Going Live

- [ ] Changed SECRET_KEY in production
- [ ] Set DATABASE_URL to PostgreSQL
- [ ] Enabled HTTPS/SSL certificate
- [ ] Configured firewall rules
- [ ] Setup database backups
- [ ] Added error monitoring
- [ ] Tested all checkout flows
- [ ] Verified email notifications work
- [ ] Added product images
- [ ] Reviewed security settings

---

**Happy selling! 🎉 Your store is ready to go live!**

**Questions?** Refer to QUICK_START.md or DEPLOYMENT_GUIDE.md
