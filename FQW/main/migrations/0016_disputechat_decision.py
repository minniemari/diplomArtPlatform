# Generated by Django 5.2 on 2025-05-03 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_ordercancellation_other_reason_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='disputechat',
            name='decision',
            field=models.CharField(blank=True, choices=[('accept', 'Принять сторону заказчика'), ('reject', 'Принять сторону художника')], max_length=10, null=True),
        ),
    ]
