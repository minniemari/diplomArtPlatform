# Generated by Django 5.1.7 on 2025-05-01 15:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_message_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivers',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivers', to='main.orders'),
        ),
    ]
