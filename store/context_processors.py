from .cart import Cart


def cart_summary(request):
    """Make `cart_count` available in every template."""
    return {"cart_count": Cart(request).count()}
