from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from store.models import Product

# name, description, price, stock, featured, image file in media/products/
SAMPLE_PRODUCTS = [
    ("Wireless Headphones", "Over-ear Bluetooth headphones with deep bass, soft ear cushions and up to 30 hours of battery life.", "2499.00", 25, True, "headphones.png"),
    ("Smart Watch", "Track steps, heart rate and sleep. Water resistant, with a bright touch display and 7-day battery.", "3999.00", 15, True, "smart-watch.png"),
    ("Everyday Backpack", "A roomy 25-litre backpack with a padded laptop sleeve, water-resistant fabric and comfortable straps.", "1899.00", 30, True, "backpack.png"),
    ("Insulated Water Bottle", "Stainless steel bottle that keeps drinks cold for 24 hours or hot for 12. Leak-proof lid, 750 ml.", "799.00", 50, False, "water-bottle.png"),
    ("Ceramic Coffee Mug", "A sturdy 350 ml ceramic mug with a comfortable handle. Microwave and dishwasher safe.", "449.00", 40, False, "coffee-mug.png"),
    ("LED Desk Lamp", "Adjustable desk lamp with three brightness levels and warm or cool light. Easy on the eyes while studying.", "1299.00", 18, True, "desk-lamp.png"),
    ("Mechanical Keyboard", "Compact keyboard with tactile switches, backlight and a durable build. Great for typing and gaming.", "3499.00", 12, False, "keyboard.png"),
    ("Bluetooth Speaker", "Portable speaker with clear sound and 12 hours of playtime. (Sample of an out-of-stock product.)", "1999.00", 0, False, "speaker.png"),
    ("Polarized Sunglasses", "Lightweight UV400 polarized sunglasses with a scratch-resistant finish. Includes a protective case.", "999.00", 22, False, "sunglasses.png"),
    ("Hardcover Notebook", "A5 notebook with 200 thick, smooth pages and an elastic closure. Perfect for notes and sketches.", "349.00", 60, False, "notebook.png"),
]


class Command(BaseCommand):
    help = "Adds the sample products (re-running resets their details and stock to the sample values)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-admin",
            action="store_true",
            help="Also create a demo admin user (username: admin, password: admin12345). Local demo only!",
        )

    def handle(self, *args, **options):
        created_count = 0
        for name, description, price, stock, featured, image_file in SAMPLE_PRODUCTS:
            image_path = Path(settings.MEDIA_ROOT) / "products" / image_file
            product, created = Product.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": Decimal(price),
                    "stock": stock,
                    "is_featured": featured,
                    "image": f"products/{image_file}" if image_path.exists() else "",
                },
            )
            created_count += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Sample products ready: {created_count} created, {len(SAMPLE_PRODUCTS) - created_count} updated."
        ))

        if options["with_admin"]:
            if User.objects.filter(username="admin").exists():
                self.stdout.write("Admin user 'admin' already exists, skipping.")
            else:
                User.objects.create_superuser("admin", "admin@example.com", "admin12345")
                self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin12345"))
