# Generated by Django 3.2.3 on 2023-07-31 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20230730_1138'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'shopping_cart'), name='unique_shopping_cart'),
        ),
    ]