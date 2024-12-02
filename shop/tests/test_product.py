from django.test import TestCase, Client
from shop.models import Product, Category
from django.urls import reverse

class ProductEndpointTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Шубы")
        self.product = Product.objects.create(
            name="Шуба «Зимняя королева»",
            description="Теплая шуба из натурального меха.",
            price=250000.00,
            characteristics={"Материал": "Мех", "Цвет": "Белый"},
            category=self.category
        )

    def test_get_products(self):
        response = self.client.post(
            reverse('products'),
            data={"category": self.category.id},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product.name, [p['name'] for p in response.json()])

    def test_get_product_detail(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], self.product.name)
