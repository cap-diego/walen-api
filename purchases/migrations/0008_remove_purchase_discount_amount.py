# Generated by Django 3.1.7 on 2021-03-02 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0007_auto_20210302_0045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='discount_amount',
        ),
    ]