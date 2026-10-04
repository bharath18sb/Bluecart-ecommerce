from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """Something we sell in the shop."""

    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock = models.PositiveIntegerField(default=0, help_text="How many are available to buy.")
    image = models.ImageField(upload_to="products/", blank=True)
    is_featured = models.BooleanField(default=False, help_text="Show on the home page.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0


class Order(models.Model):
    """One checkout made by a logged-in user."""

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Django's built-in User model
        on_delete=models.CASCADE,
        related_name="orders",
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    """One product line inside an order.

    The name and price are copied from the product at the time of purchase,
    so old orders stay correct even if the product changes later.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    def get_subtotal(self):
        return self.price * self.quantity
