# Generated by Django 5.1.4 on 2025-01-08 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_order_payment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.JSONField(default=dict),
        ),
    ]
