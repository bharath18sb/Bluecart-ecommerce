from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import AddToCartForm, CheckoutForm, RegisterForm
from .models import Order, OrderItem, Product

# ---------------------------------------------------------------- Home & products

SORT_OPTIONS = {
    "name": "name",
    "newest": "-created_at",
    "price_low": "price",
    "price_high": "-price",
}


def home(request):
    featured_products = Product.objects.filter(is_featured=True)[:4]
    return render(request, "store/home.html", {"featured_products": featured_products})


def product_list(request):
    products = Product.objects.all()

    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")
    availability = request.GET.get("availability", "")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if availability == "in_stock":
        products = products.filter(stock__gt=0)
    if sort not in SORT_OPTIONS:
        sort = "name"
    products = products.order_by(SORT_OPTIONS[sort])

    context = {
        "products": products,
        "query": query,
        "sort": sort,
        "availability": availability,
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "store/product_detail.html", {"product": product})


# ---------------------------------------------------------------- Cart

def redirect_back(request, default):
    """Go back to the page the user came from (the hidden 'next' field).
    Only same-site addresses are allowed, for safety."""
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect(default)


def cart_detail(request):
    cart = Cart(request)
    rows = cart.items()
    context = {
        "rows": rows,
        "total": sum(row["subtotal"] for row in rows),
        "can_checkout": bool(rows) and all(row["available"] for row in rows),
    }
    return render(request, "store/cart.html", context)


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = AddToCartForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please enter a valid quantity (1 or more).")
        return redirect_back(request, "product_list")

    if not product.in_stock:
        messages.error(request, f'Sorry, "{product.name}" is out of stock.')
        return redirect_back(request, "product_list")

    cart = Cart(request)
    wanted = form.cleaned_data["quantity"]
    room_left = product.stock - cart.get_quantity(product.id)

    if room_left <= 0:
        messages.warning(request, f'You already have all {product.stock} available "{product.name}" in your cart.')
    elif wanted > room_left:
        cart.add(product.id, room_left)
        messages.warning(
            request, f'Only {product.stock} in stock, so we added {room_left} of "{product.name}" to your cart.'
        )
    else:
        cart.add(product.id, wanted)
        messages.success(request, f'Added {wanted} x "{product.name}" to your cart.')
    return redirect_back(request, "cart")


@require_POST
def cart_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = Cart(request)
    try:
        quantity = int(request.POST.get("quantity", ""))
    except ValueError:
        messages.error(request, "Please enter a valid quantity.")
        return redirect("cart")

    if quantity <= 0:
        cart.remove(product.id)
        messages.success(request, f'Removed "{product.name}" from your cart.')
    elif not product.in_stock:
        cart.remove(product.id)
        messages.error(request, f'"{product.name}" is now out of stock and was removed.')
    elif quantity > product.stock:
        cart.set_quantity(product.id, product.stock)
        messages.warning(request, f'Only {product.stock} of "{product.name}" in stock. Quantity adjusted.')
    else:
        cart.set_quantity(product.id, quantity)
        messages.success(request, "Cart updated.")
    return redirect("cart")


@require_POST
def cart_remove(request, pk):
    Cart(request).remove(pk)
    messages.success(request, "Item removed from your cart.")
    return redirect("cart")


# ---------------------------------------------------------------- Checkout & orders

def place_order(user, form, cart):
    """Create the order safely.

    Everything happens inside one database transaction, so either the whole
    order is saved or nothing is. Prices and the total come from the database,
    never from the browser, and stock is checked again before saving.

    Returns (order, problems). If something is wrong, order is None.
    """
    with transaction.atomic():
        product_ids = [int(key) for key in cart.cart]
        products = Product.objects.select_for_update().in_bulk(product_ids)

        problems = []
        lines = []
        for key, quantity in cart.cart.items():
            product = products.get(int(key))
            if product is None:
                problems.append("A product in your cart is no longer available.")
            elif product.stock == 0:
                problems.append(f'"{product.name}" is out of stock.')
            elif quantity > product.stock:
                problems.append(f'Only {product.stock} of "{product.name}" in stock.')
            else:
                lines.append((product, quantity))

        if problems or not lines:
            return None, problems or ["Your cart is empty."]

        order = form.save(commit=False)
        order.user = user
        order.total = Decimal("0.00")
        order.save()

        total = Decimal("0.00")
        for product, quantity in lines:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=quantity,
            )
            product.stock -= quantity
            product.save(update_fields=["stock"])
            total += product.price * quantity

        order.total = total
        order.save(update_fields=["total"])

    cart.clear()
    return order, []


@login_required
def checkout(request):
    cart = Cart(request)
    rows = cart.items()
    if not rows:
        messages.info(request, "Your cart is empty. Add some products first.")
        return redirect("product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order, problems = place_order(request.user, form, cart)
            if order:
                return redirect("order_success", order_id=order.id)
            for problem in problems:
                messages.error(request, problem)
            return redirect("cart")
    else:
        form = CheckoutForm(
            initial={"full_name": request.user.get_full_name(), "email": request.user.email}
        )

    context = {
        "form": form,
        "rows": rows,
        "total": sum(row["subtotal"] for row in rows),
    }
    return render(request, "store/checkout.html", context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})


@login_required
def my_orders(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "store/my_orders.html", {"orders": orders})


# ---------------------------------------------------------------- Accounts

def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)  # log the new user in straight away
        messages.success(request, f"Welcome, {user.username}! Your account has been created.")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})
