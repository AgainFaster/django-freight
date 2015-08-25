# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('sku', models.CharField(max_length=50)),
                ('weight', models.DecimalField(max_digits=12, decimal_places=2)),
                ('unit', models.CharField(max_length=10)),
                ('flat_rate', models.DecimalField(max_digits=12, decimal_places=2)),
                ('ships_free', models.BooleanField(default=False)),
                ('quantity', models.IntegerField()),
                ('length', models.DecimalField(max_digits=12, decimal_places=2)),
                ('width', models.DecimalField(max_digits=12, decimal_places=2)),
                ('height', models.DecimalField(max_digits=12, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('warehouse', models.IntegerField()),
                ('origin', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ShippingRequest',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('raw_request', models.TextField()),
                ('destination', models.TextField()),
                ('received', models.DateTimeField(editable=False)),
                ('carrier_request', models.TextField()),
                ('carrier_response', models.TextField()),
                ('response', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='shipment',
            name='request',
            field=models.ForeignKey(related_name='shipments', to='shipping.ShippingRequest'),
        ),
        migrations.AddField(
            model_name='item',
            name='shipment',
            field=models.ForeignKey(related_name='items', to='shipping.Shipment'),
        ),
    ]
