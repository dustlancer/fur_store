from django.contrib import admin
from .models import Category, Product, CartItem, Order

# Регистрация модели Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)

# Регистрация модели Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category')
    search_fields = ('name', 'description')
    list_filter = ('category', 'price')

# Регистрация модели CartItem
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')
    list_filter = ('user',)

# Регистрация модели Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'status')
    search_fields = ('user__username',)
    list_filter = ('created_at',)