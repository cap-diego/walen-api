# Generated by Django 3.1.7 on 2021-03-01 01:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0004_auto_20210228_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='expiration_date',
        ),
    ]