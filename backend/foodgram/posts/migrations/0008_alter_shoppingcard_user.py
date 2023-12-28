# Generated by Django 3.2.13 on 2023-11-17 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0007_alter_shoppingcard_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcard',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_card', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
