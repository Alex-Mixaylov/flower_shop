import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery_project.settings')
django.setup()

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from orders.models import Category, Product, Collection
from orders.forms import ReviewForm
from django.contrib.auth import get_user_model
from orders.context_processors import category_context

# Тест для моделей
class CategoryModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Flowers")
        self.collection = Collection.objects.create(
            name="Test Collection",
            slug="test-collection",
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Flowers")

    def test_product_creation_in_category(self):
        product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=100.00,
            collection=self.collection
        )
        self.assertIn(product, self.category.products.all())

# Тест для представления
class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Test Category")
        self.collection = Collection.objects.create(
            name="Test Collection",
            slug="test-collection",
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )

    def test_collection_detail_view(self):
        response = self.client.get(reverse('collection_detail', kwargs={'slug': self.collection.slug}))
        self.assertEqual(response.status_code, 200)


# Тест для  Формы
CustomUser = get_user_model()
class ReviewFormTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='123pass')

        category = Category.objects.create(name="Test Category")
        collection = Collection.objects.create(
            name="Test Collection",
            slug="test-collection",
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )
        self.product = Product.objects.create(
            name="Test Product",
            category=category,
            price=100.00,
            collection=collection
        )

    def test_review_form_valid(self):
        # Те данные, которые пользователь заполняет сам в форме
        form_data = {
            'rating': 4,
            'text': "Great product!",
        }
        form = ReviewForm(data=form_data)

        # Имитируем логику из product_details:
        form.instance.product = self.product
        form.instance.author = self.user

        # Теперь модель уже имеет все обязательные поля:
        self.assertTrue(form.is_valid(), "Форма должна быть валидной, если вручную задать product/author.")

        # Проверим сохранение:
        review = form.save()
        self.assertIsNotNone(review.pk, "Отзыв должен успешно сохраниться в БД.")
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.text, "Great product!")
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.author, self.user)

# Тест контекстного процессора
class CategoryContextProcessorTestCase(TestCase):
    def setUp(self):
        Category.objects.all().delete()  # Стираем все категории

        self.factory = RequestFactory()
        Category.objects.create(name="Flowers")
        Category.objects.create(name="Plants")

    def test_category_context_returns_categories_with_counts(self):
        request = self.factory.get('/')
        context = category_context(request)
        self.assertIn('categories', context)

        categories = context['categories']
        self.assertEqual(categories.count(), 2, "Должно вернуться 2 категории.")

        for cat in categories:
            self.assertTrue(hasattr(cat, 'product_count'))
