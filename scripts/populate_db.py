# scripts/populate_db.py

from shop.models import Category, Product
from decimal import Decimal

def populate_categories_and_products():
    # Пример категорий
    categories = [
        {"name": "Верхняя одежда", "subcategories": ["Шубы", "Пальто"]},
        {"name": "Аксессуары", "subcategories": ["Перчатки", "Шарфы"]},
    ]

    # Создание категорий
    for category_data in categories:
        parent_category, _ = Category.objects.get_or_create(name=category_data["name"], parent=None)
        for subcategory_name in category_data["subcategories"]:
            Category.objects.get_or_create(name=subcategory_name, parent=parent_category)

    # Пример продуктов
    products = [
        # Шубы
        {"name": "Шуба «Зимняя королева»", "description": "Теплая шуба из натурального меха.", 
         "price": Decimal("250000.00"), "characteristics": {"Материал": "Мех", "Цвет": "Белый"}, 
         "category": "Шубы"},
        {"name": "Шуба «Северная роскошь»", "description": "Эксклюзивная шуба для холодной зимы.", 
         "price": Decimal("300000.00"), "characteristics": {"Материал": "Мех", "Цвет": "Черный"}, 
         "category": "Шубы"},
        {"name": "Шуба «Грация»", "description": "Элегантная шуба средней длины.", 
         "price": Decimal("180000.00"), "characteristics": {"Материал": "Мех", "Цвет": "Коричневый"}, 
         "category": "Шубы"},
        {"name": "Шуба «Морозная сказка»", "description": "Роскошная шуба для особых случаев.", 
         "price": Decimal("400000.00"), "characteristics": {"Материал": "Мех", "Цвет": "Серый"}, 
         "category": "Шубы"},

        # Пальто
        {"name": "Пальто «Осенний шик»", "description": "Стильное пальто для осени.", 
         "price": Decimal("75000.00"), "characteristics": {"Материал": "Шерсть", "Цвет": "Серый"}, 
         "category": "Пальто"},
        {"name": "Пальто «Весенний рассвет»", "description": "Лёгкое пальто для весны.", 
         "price": Decimal("60000.00"), "characteristics": {"Материал": "Хлопок", "Цвет": "Бежевый"}, 
         "category": "Пальто"},
        {"name": "Пальто «Зимний уют»", "description": "Утепленное пальто для зимы.", 
         "price": Decimal("90000.00"), "characteristics": {"Материал": "Шерсть", "Цвет": "Темно-синий"}, 
         "category": "Пальто"},
        {"name": "Пальто «Городская классика»", "description": "Современное пальто для городских прогулок.", 
         "price": Decimal("80000.00"), "characteristics": {"Материал": "Шерсть", "Цвет": "Черный"}, 
         "category": "Пальто"},

        # Перчатки
        {"name": "Перчатки «Элегантный стиль»", "description": "Теплые кожаные перчатки.", 
         "price": Decimal("12000.00"), "characteristics": {"Материал": "Кожа", "Размер": "M"}, 
         "category": "Перчатки"},
        {"name": "Перчатки «Комфорт»", "description": "Перчатки с подкладкой из флиса.", 
         "price": Decimal("9000.00"), "characteristics": {"Материал": "Кожа", "Размер": "L"}, 
         "category": "Перчатки"},
        {"name": "Перчатки «Северное сияние»", "description": "Длинные женские перчатки для вечернего образа.", 
         "price": Decimal("15000.00"), "characteristics": {"Материал": "Замша", "Размер": "S"}, 
         "category": "Перчатки"},
        {"name": "Перчатки «Тепло зимой»", "description": "Мягкие перчатки из натуральной шерсти.", 
         "price": Decimal("10000.00"), "characteristics": {"Материал": "Шерсть", "Размер": "M"}, 
         "category": "Перчатки"},

        # Шарфы
        {"name": "Шарф «Тепло и уют»", "description": "Шерстяной шарф ручной вязки.", 
         "price": Decimal("8000.00"), "characteristics": {"Материал": "Шерсть", "Цвет": "Красный"}, 
         "category": "Шарфы"},
        {"name": "Шарф «Городской комфорт»", "description": "Универсальный шарф для прогулок.", 
         "price": Decimal("6000.00"), "characteristics": {"Материал": "Хлопок", "Цвет": "Синий"}, 
         "category": "Шарфы"},
        {"name": "Шарф «Ручная работа»", "description": "Индивидуальный дизайн и высокое качество.", 
         "price": Decimal("12000.00"), "characteristics": {"Материал": "Шерсть", "Цвет": "Бежевый"}, 
         "category": "Шарфы"},
        {"name": "Шарф «Модный тренд»", "description": "Модный шарф с оригинальным рисунком.", 
         "price": Decimal("9000.00"), "characteristics": {"Материал": "Шелк", "Цвет": "Черный"}, 
         "category": "Шарфы"},
    ]

    # Создание продуктов
    for product_data in products:
        category = Category.objects.get(name=product_data["category"])
        Product.objects.get_or_create(
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            characteristics=product_data["characteristics"],
            category=category,
        )

    print("Категории и продукты успешно добавлены!")
