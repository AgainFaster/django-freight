# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0002_auto_20150818_1625'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResponseRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('time_in_transit', models.IntegerField()),
                ('rate', models.DecimalField(max_digits=12, decimal_places=2)),
                ('carrier', models.ForeignKey(to='shipping.Carrier', related_name='rates')),
            ],
        ),
        migrations.CreateModel(
            name='ResponseSurcharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=2)),
                ('ratedrate', models.ForeignKey(to='shipping.ResponseRate', related_name='surcharges')),
                ('surcharge', models.ForeignKey(to='shipping.Surcharge', related_name='rates')),
            ],
        ),
        migrations.RenameField(
            model_name='shipment',
            old_name='request',
            new_name='shipping_request',
        ),
        migrations.RenameField(
            model_name='shippingrequest',
            old_name='response',
            new_name='raw_response',
        ),
        migrations.AddField(
            model_name='responserate',
            name='shipping_request',
            field=models.OneToOneField(to='shipping.ShippingRequest', related_name='response'),
        ),
    ]
