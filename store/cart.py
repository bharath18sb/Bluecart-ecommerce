"""
A very small shopping cart that lives in the user's session.

The session holds a dictionary like {"3": 2, "7": 1}, which means
"2 of product 3 and 1 of product 7". Prices are NEVER stored in the cart:
they are always read from the database, so they cannot be tampered with.
"""
from .models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        # Reading does not touch the session, so visitors who never add
        # anything don't get a session saved for them.
        self.cart = self.session.get(CART_SESSION_KEY, {})

    def _save(self):
        # Write the cart back and tell Django the session changed.
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def get_quantity(self, product_id):
        return self.cart.get(str(product_id), 0)

    def add(self, product_id, quantity=1):
        key = str(product_id)
        self.cart[key] = self.cart.get(key, 0) + quantity
        self._save()

    def set_quantity(self, product_id, quantity):
        self.cart[str(product_id)] = quantity
        self._save()

    def remove(self, product_id):
        self.cart.pop(str(product_id), None)
        self._save()

    def clear(self):
        self.cart = {}
        self._save()

    def items(self):
        """Return a list of rows: product, quantity, subtotal and 'available'."""
        products = Product.objects.in_bulk([int(key) for key in self.cart])
        rows = []
        for key, quantity in list(self.cart.items()):
            product = products.get(int(key))
            if product is None:
                # The product was deleted by the admin, so drop it from the cart.
                del self.cart[key]
                self._save()
                continue
            rows.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "subtotal": product.price * quantity,
                    "available": quantity <= product.stock,
                }
            )
        return rows

    def count(self):
        """Total number of units in the cart (shown next to the cart icon)."""
        return sum(self.cart.values())
