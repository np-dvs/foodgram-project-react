# Generated by Django 3.2.16 on 2024-03-18 17:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foodgram_backend', '0003_auto_20240202_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favourites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='foodgram_backend.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favourites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
