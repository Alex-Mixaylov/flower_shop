# Generated by Django 5.1.2 on 2024-12-09 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_product_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('main_image', models.ImageField(upload_to='slides/', verbose_name='Основное изображение')),
                ('background_image', models.ImageField(blank=True, null=True, upload_to='slides/', verbose_name='Фоновое изображение')),
                ('additional_image', models.ImageField(blank=True, null=True, upload_to='slides/', verbose_name='Дополнительное изображение')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Слайд',
                'verbose_name_plural': 'Слайды',
                'ordering': ['order'],
            },
        ),
    ]