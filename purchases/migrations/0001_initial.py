# Generated by Django 3.1.7 on 2021-03-01 13:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualPurchase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Individual purchase id')),
                ('creation_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Payment id')),
                ('status', models.CharField(choices=[('pen', 'pending'), ('fld', 'failed'), ('rsv', 'reserved'), ('cap', 'captured')], default='pen', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Purchase id')),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('aws', 'awaiting-peers'), ('pip', 'pending-initial-payment'), ('cmp', 'completed'), ('cnc', 'cancelled')], default='pip', max_length=3)),
                ('clients_target', models.PositiveSmallIntegerField()),
                ('current_confirmed_clients', models.PositiveSmallIntegerField(default=0)),
                ('discount_amount', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['-creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Shipment id')),
                ('status', models.CharField(choices=[('awp', 'awaiting-payment'), ('pen', 'pending'), ('apc', 'awaiting-purchase-completition'), ('dis', 'dispatched'), ('del', 'del'), ('abr', 'abr')], default='awp', max_length=3)),
            ],
        ),
    ]
