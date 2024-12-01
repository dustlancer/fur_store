from django.test import TestCase, Client
from shop.models import User, CartItem, Category, Product
from django.urls import reverse

class OrderEndpointTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345',  email='dustlancer@gmail.com')
        self.client.login(username='testuser', password='12345')

    def test_create_order(self):
        category = Category.objects.create(name="Шубы")
        product = Product.objects.create(
            name="Шуба «Зимняя королева»",
            description="Теплая шуба из натурального меха.",
            price=250000.00,
            characteristics={"Материал": "Мех", "Цвет": "Белый"},
            category=category
        )
        CartItem.objects.create(user=self.user, product=product, quantity=1)

        response = self.client.post(reverse('order'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('payment_url', response.json())
