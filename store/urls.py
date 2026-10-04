from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Shop pages
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    # Cart
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:pk>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    # Checkout and orders
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("my-orders/", views.my_orders, name="my_orders"),
    # Accounts (login/logout use Django's built-in views)
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html", redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
