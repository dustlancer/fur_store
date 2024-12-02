from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryListView, CartView, OrderCreateView, PaymentWebhookView, payment_success

urlpatterns = [
    path('products', ProductListView.as_view(), name='products'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('categories', CategoryListView.as_view(), name='categories'),
    path('cart', CartView.as_view(), name='cart'),
    path('order', OrderCreateView.as_view(), name='order'),
    path('payment/webhook', PaymentWebhookView.as_view(), name='payment_webhook'),
    path('payment/success', payment_success, name='payment_success'),
]
