# BlueCart – Simple E-commerce Store

A beginner-friendly online store built with **Django (Python)**, **SQLite**, and plain **HTML, CSS and JavaScript**.
Blue + white, responsive design for mobile and desktop.

## Features

- Home page with store logo, navigation bar, featured products, **Shop Now** button and footer
- Product listing with cards (image, name, price, description), **Add to Cart**, search, sort and "in stock only" filter
- Product details page with image, full description, price, stock, quantity selector and **Add to Cart**
- Shopping cart: change quantity, remove items, live total, **Proceed to Checkout**
- Register, login and logout using Django's built-in authentication
- Checkout form (name, email, phone, address), order summary, **Place Order**, "Order Successful" page
- **My Orders**: order ID, date, total and status (plus the items in each order)
- Django Admin: add/edit/delete products, view orders, update order status
- 10 sample products with images (one is out of stock, to demonstrate that case)

## Quick start

You need **Python 3.10 or newer**.

```bash
# 1. Go into the project folder
cd simple-ecommerce-store

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 3. Install the requirements
pip install -r requirements.txt

# 4. Create the database tables
python manage.py makemigrations store
python manage.py migrate

# 5. Add the sample products (and a demo admin user for local testing)
python manage.py load_sample_data --with-admin

# 6. Start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

- Shop: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/ (username `admin`, password `admin12345`, created by `--with-admin`)

Prefer your own admin account? Skip `--with-admin` and run `python manage.py createsuperuser` instead.
The demo admin password is for **local demonstration only**. Never use it on a real website.

## Demo walkthrough (for your assignment)

1. Open the home page, then click **Shop Now**.
2. Try the search box, the sort menu and "In stock only".
3. Open a product, pick a quantity and click **Add to Cart**.
4. Open the **Cart**: change a quantity, remove an item, and check the total.
5. Click **Proceed to Checkout**. You will be asked to **Register** or **Login**.
6. Fill in the checkout form (try leaving fields empty or entering a bad phone number to see validation) and click **Place Order**.
7. See the **Order Successful** page, then open **My Orders**.
8. Log in to `/admin/` as admin: open **Orders**, change an order's **Status** from the list, and refresh **My Orders** to see it change.
9. In **Products**, change a product's stock to 0 and see it become "Sold out" in the shop.

## How the important rules work

| Rule | Where it happens |
|------|------------------|
| Out-of-stock products cannot be added | `cart_add` view in `store/views.py` |
| Quantity can't exceed stock (cart and checkout) | `cart_add`, `cart_update` and `place_order` in `store/views.py` |
| Order total is calculated on the server | `place_order` reads prices from the database. Prices never come from the browser |
| Stock is reduced when an order is placed | `place_order`, inside a database transaction |
| Order keeps the price paid | `OrderItem` copies name and price at purchase time |
| Forms are validated | `store/forms.py` (phone, name, address, email, quantity) |
| Only your own orders are visible | `my_orders` and `order_success` filter by the logged-in user |

## Project structure

```
simple-ecommerce-store/
├── manage.py
├── requirements.txt
├── README.md
├── config/                  # project settings and main URLs
│   ├── settings.py
│   └── urls.py
├── store/                   # the shop app
│   ├── models.py            # Product, Order, OrderItem
│   ├── views.py             # all pages and the order logic
│   ├── urls.py              # page addresses
│   ├── forms.py             # register, add-to-cart and checkout forms
│   ├── admin.py             # admin panel setup
│   ├── cart.py              # session-based shopping cart
│   ├── context_processors.py
│   └── management/commands/load_sample_data.py
├── templates/               # HTML (Django templates)
│   ├── base.html
│   ├── store/               # home, products, cart, checkout, orders...
│   └── registration/        # login and register pages
├── static/
│   ├── css/style.css
│   └── js/main.js
└── media/products/          # product images
```

## Models

- **Product**: name, description, price, stock, image, is_featured
- **Order**: user (Django's built-in `User`), name, email, phone, address, total, status, date
- **OrderItem**: order, product, product name, price, quantity

Order statuses: Pending, Processing, Shipped, Delivered, Cancelled.

## Troubleshooting

- **"No module named django"**: activate your virtual environment and run `pip install -r requirements.txt`.
- **"no such table"**: run `python manage.py makemigrations store` and then `python manage.py migrate`.
- **Product images not showing**: run the server with `python manage.py runserver` (images are served from `media/` in debug mode), and run `load_sample_data` again.
- **Start fresh**: delete `db.sqlite3` and repeat steps 4 and 5.
