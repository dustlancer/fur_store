# from yookassa.domain.notification import WebhookNotificationEventType
# from django.test import TestCase, Client
# from shop.models import Order
# from django.contrib.auth.models import User
# from django.urls import reverse
# import json

# class PaymentWebhookTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.order = Order.objects.create(
#             user=User.objects.create_user(username='testuser', password='12345',  email='dustlancer@gmail.com'),
#             total_price=250000.00,
#             items=[{'product': 'Шуба «Зимняя королева»', 'quantity': 1, 'price': 250000.00}],
#         )

#     def test_webhook_payment_succeeded(self):
#         data = {
#             "type": "notification",
#             "event": "payment.succeeded",
#             "object": {
#                 "status": "succeeded",
#                 "description": f"Order #{self.order.id}",
#                 "amount": {"value": "250000.00", "currency": "RUB"}
#             }
#         }
#         response = self.client.post(reverse('payment_webhook'), data=json.dumps(data), content_type="application/json")
#         self.assertEqual(response.status_code, 200)

#         # Проверяем, что статус заказа обновился
#         self.order.refresh_from_db()
