# Generated by Django 5.1.7 on 2025-04-13 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_orders_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='userresponse',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
