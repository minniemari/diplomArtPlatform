# Generated by Django 5.1.7 on 2025-03-27 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_commission_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='userresponse',
            name='technical_task',
            field=models.TextField(blank=True, null=True),
        ),
    ]
