from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Product, Category, CartItem, Order
from .serializers import ProductSerializer, CategorySerializer, CartItemSerializer
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import JsonResponse
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory
from .tasks import send_order_email_task
import json
import logging


logger = logging.getLogger(__name__)




class ProductListView(APIView):
    @swagger_auto_schema(
        operation_description="Получение списка товаров по категории",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID категории (необязательное поле, если пусто - возвращаются все товары)'
                ),
            }
        ),
        responses={200: ProductSerializer(many=True)}
    )
    def post(self, request):
        category_id = request.data.get('category')
        
        if category_id:
            # Рекурсивно собираем все вложенные категории
            category_ids = self.get_all_subcategories(category_id)
            products = Product.objects.filter(category_id__in=category_ids)
        else:
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def get_all_subcategories(self, category_id):
        """
        Рекурсивно собирает все вложенные категории, включая текущую.
        """
        category_ids = [category_id]
        subcategories = Category.objects.filter(parent_id=category_id)
        for subcategory in subcategories:
            category_ids.extend(self.get_all_subcategories(subcategory.id))
        return category_ids



class ProductDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Получение информации о конкретном товаре",
        responses={200: ProductSerializer(), 404: "Товар не найден"}
    )
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class CategoryListView(APIView):
    @swagger_auto_schema(
        operation_description="Получение списка категорий",
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request):
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение содержимого корзины текущего пользователя",
        responses={200: CartItemSerializer(many=True)}
    )
    def get(self, request):
        logger.info('cart info')
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Добавление товара в корзину",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID товара'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество'),
            },
        ),
        responses={201: "Товар добавлен в корзину"}
    )
    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product_id=product_id)
        if not created:
            cart_item.quantity += quantity
        cart_item.save()
        return Response({'message': 'Product added to cart'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Обновление количества товара в корзине",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'cart_item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID элемента корзины'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Новое количество'),
            }
        ),
        responses={200: "Корзина обновлена", 404: "Элемент корзины не найден"}
    )
    def put(self, request):
        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'message': 'Cart updated'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Удаление товара из корзины",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'cart_item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID элемента корзины'),
            }
        ),
        responses={200: "Товар удален из корзины", 404: "Элемент корзины не найден"}
    )
    def delete(self, request):
        cart_item_id = request.data.get('cart_item_id')
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
            cart_item.delete()
            return Response({'message': 'Cart item deleted'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info('aaaaaaaaa')
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.get_total_price() for item in cart_items)

        # Формируем список элементов заказа
        items = [
            {
                'product': item.product.name,
                'quantity': item.quantity,
                'price': float(item.product.price)
            }
            for item in cart_items
        ]

        # Создаём заказ в базе данных
        order = Order.objects.create(
            user=request.user,
            total_price=float(total_price),
            items=items
        )

        # Генерируем платёж через YooKassa, передавая items
        payment = self.create_payment(order.id, total_price, request.user.email, items)

        # Очищаем корзину
        cart_items.delete()

        return Response({'payment_url': payment.confirmation['confirmation_url']}, status=status.HTTP_201_CREATED)

    def create_payment(self, order_id, total_price, email, items):
        from yookassa import Configuration, Payment

        # Настройка API YooKassa
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

        # Создаём платёж
        payment = Payment.create({
            "amount": {
                "value": f"{total_price:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": settings.YOOKASSA_RETURN_URL
            },
            "capture": True,
            "description": f"Order #{order_id}",
            "receipt": {
                "customer": {"email": email},
                "items": [
                    {
                        "description": item['product'],
                        "quantity": str(item['quantity']),
                        "amount": {
                            "value": f"{item['price']:.2f}",
                            "currency": "RUB"
                        },
                        "vat_code": "1"  # НДС, настройте по требованию
                    }
                    for item in items
                ]
            }
        })

        return payment

    
class PaymentWebhookView(APIView):
    def post(self, request):
        logger.info(f"webhook workin")
        try:
            logger.info(f"webhook workin")
            # Преобразуем тело запроса из JSON-строки в словарь
            event_json = json.loads(request.body.decode('utf-8'))
            logger.info(f"webhook {event_json}")
            

            # Создаём объект уведомления из данных
            notification = WebhookNotificationFactory().create(event_json)

            if notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                payment = notification.object
                order_id = int(payment.description.split('#')[1])  # Извлекаем ID заказа из описания

                # Находим заказ и обновляем его статус
                order = Order.objects.get(id=order_id)
                order.status = 'paid'
                order.save()
                

                # Отправляем письмо пользователю
                # send_order_email_task.delay(order.user.email, 123, 1000, [{"product": "Test", "quantity": 1, "price": 1000}])
                # print(f'------------- {request.user.email} {order.id}   {order.total_price}     {order.items}')
                send_order_email_task.delay(
                    email=order.user.email,
                    order_id=order.id,
                    total_price=order.total_price,
                    items=order.items
                )
                

            return JsonResponse({'status': 'ok'}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        except Exception as e:
            # Логирование ошибок для отладки
            print(f"Error in Webhook processing: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    def send_order_email(self, email, order_id, total_price, items):
        # Преобразуем данные в удобный формат для шаблона
        items_with_total = [
            {
                "product": item["product"],
                "quantity": item["quantity"],
                "price": item["price"],
                "total": item["quantity"] * item["price"]
            }
            for item in items
        ]

        # Генерируем HTML-письмо
        html_content = render_to_string('order_email.html', {
            'order_id': order_id,
            'total_price': total_price,
            'items': items_with_total
        })

        subject = f"Ваш заказ #{order_id} успешно создан"
        text_content = (
            f"Ваш заказ #{order_id} был успешно создан и оплачен.\n"
            f"Общая сумма: {total_price} руб.\n"
        )

        # Создаём письмо
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,  # Текстовая версия письма (на случай, если HTML недоступен)
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_message.attach_alternative(html_content, "text/html")  # Прикрепляем HTML-версию
        email_message.send()


def payment_success(request):
    return JsonResponse({
        "status": "success",
        "message": "Ваш платеж успешно завершён. Спасибо за ваш заказ!"
    })