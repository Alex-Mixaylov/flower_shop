# Generated by Django 5.1.2 on 2024-12-10 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_bestseller_options_bestseller_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='combooffer',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Старая цена'),
        ),
    ]
