# Generated by Django 3.1.7 on 2021-03-01 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0005_auto_20210301_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='vendor_payment_id',
            field=models.PositiveBigIntegerField(null=True),
        ),
    ]
