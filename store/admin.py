from django.contrib import admin

from .models import Order, OrderItem, Product

admin.site.site_header = "BlueCart Admin"
admin.site.site_title = "BlueCart Admin"
admin.site.index_title = "Manage your store"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "is_featured", "created_at")
    list_editable = ("price", "stock", "is_featured")  # edit straight from the list
    list_filter = ("is_featured",)
    search_fields = ("name", "description")


class OrderItemInline(admin.TabularInline):
    """Shows the products of an order inside the order page (read-only)."""

    model = OrderItem
    extra = 0
    can_delete = False
    fields = ("product_name", "price", "quantity", "subtotal")
    readonly_fields = ("product_name", "price", "quantity", "subtotal")

    def subtotal(self, obj):
        return obj.get_subtotal()

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "user", "total", "status", "created_at")
    list_editable = ("status",)  # change the status straight from the list
    list_filter = ("status", "created_at")
    search_fields = ("id", "full_name", "email", "user__username")
    readonly_fields = ("user", "total", "created_at")
    inlines = [OrderItemInline]
    actions = ["mark_processing", "mark_shipped", "mark_delivered"]

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        queryset.update(status=Order.STATUS_PROCESSING)

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.STATUS_SHIPPED)

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status=Order.STATUS_DELIVERED)
