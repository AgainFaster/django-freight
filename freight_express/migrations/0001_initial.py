# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AUFee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(null=True, help_text='Name by which to identify the fee', max_length=255)),
                ('fee', models.FloatField(help_text='Fee to add to the returned rate')),
                ('enabled', models.BooleanField(default=False, help_text='Fee is currently active and being applied to the rate')),
                ('percentage', models.BooleanField(default=False, help_text='Enable if fee is to be calculated as a percentage of the rate')),
            ],
            options={
                'verbose_name': 'AU Fee',
            },
        ),
        migrations.CreateModel(
            name='AUSurchargeTier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('surcharge', models.FloatField()),
            ],
            options={
                'verbose_name': 'AU Surcharge Tier',
            },
        ),
        migrations.CreateModel(
            name='AUZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=5, unique=True)),
                ('long_name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'AU Zone',
            },
        ),
        migrations.CreateModel(
            name='CAFreightMultiplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, null=True, max_length=100)),
                ('from_province', models.CharField(max_length=2)),
                ('sku_list', models.TextField()),
                ('multiplier', models.FloatField()),
            ],
            options={
                'verbose_name': 'CA Freight Multiplier',
            },
        ),
        migrations.CreateModel(
            name='CAFreightRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('from_province', models.CharField(max_length=2)),
                ('to_province', models.CharField(max_length=2)),
                ('to_city', models.CharField(blank=True, null=True, max_length=100)),
                ('rate', models.FloatField()),
            ],
            options={
                'verbose_name': 'CA Freight Rate',
            },
        ),
        migrations.CreateModel(
            name='CAFreightSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('from_province', models.CharField(max_length=2, unique=True)),
                ('skid_weight', models.FloatField(default=50.0)),
                ('minimum_weight', models.FloatField(default=640.0)),
                ('default_multiplier', models.FloatField(default=1.2)),
                ('surcharge', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name': 'CA Freight Setting',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('postcode', models.CharField(max_length=4, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='NZCourierRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('max_weight', models.IntegerField(default=5)),
                ('cubic_conversion', models.FloatField()),
                ('rate', models.FloatField()),
            ],
            options={
                'verbose_name': 'NZ Courier Rate',
            },
        ),
        migrations.CreateModel(
            name='NZDistanceFactor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('number', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('default_freight_tonne_rate', models.FloatField(blank=True, null=True)),
                ('default_freight_cubic_rate', models.FloatField(blank=True, null=True)),
                ('minimum_freight_cost', models.FloatField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'NZ Distance Factor',
            },
        ),
        migrations.CreateModel(
            name='NZFreightRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('destination_group', models.CharField(max_length=100)),
                ('tonne_rate', models.FloatField()),
                ('cubic_rate', models.FloatField()),
            ],
            options={
                'verbose_name': 'NZ Freight Rate',
            },
        ),
        migrations.CreateModel(
            name='NZLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('postcode', models.CharField(max_length=4)),
                ('location_name', models.CharField(max_length=100)),
                ('area', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('is_rural', models.BooleanField()),
                ('town_code', models.CharField(max_length=3)),
                ('delivery_depot', models.CharField(max_length=100)),
                ('distance_factor', models.ForeignKey(to='freight_express.NZDistanceFactor')),
            ],
            options={
                'verbose_name': 'NZ Location',
            },
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('service', models.CharField(blank=True, null=True, default='EXP', max_length=25)),
                ('basic_charge', models.FloatField()),
                ('rate', models.FloatField()),
                ('type', models.CharField(blank=True, null=True, default='KG', choices=[('KG', 'KG'), ('LB', 'LB')], max_length=25)),
                ('min_charge', models.FloatField()),
                ('cubic_conv', models.FloatField(default=250.0)),
                ('from_zone', models.ForeignKey(blank=True, null=True, to='freight_express.AUZone', related_name='origin_rates')),
                ('to_zone', models.ForeignKey(blank=True, null=True, to='freight_express.AUZone', related_name='destination_rates')),
            ],
            options={
                'verbose_name': 'AU Rate',
            },
        ),
        migrations.CreateModel(
            name='UKRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('from_country_code', models.CharField(max_length=2)),
                ('to_country_code', models.CharField(max_length=2)),
                ('to_region', models.CharField(blank=True, null=True, max_length=100)),
                ('max_weight', models.FloatField(default=0)),
                ('initial_rate', models.FloatField(default=0)),
                ('weight_multiplier_rate', models.FloatField(default=0)),
                ('weight_offset', models.FloatField(default=0)),
            ],
            options={
                'ordering': ('-max_weight',),
                'verbose_name': 'UK Rate',
            },
        ),
        migrations.CreateModel(
            name='UKShippingProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'UK Shipping Provider',
            },
        ),
        migrations.CreateModel(
            name='AUPostCode',
            fields=[
                ('location_ptr', models.OneToOneField(auto_created=True, to='freight_express.Location', parent_link=True, primary_key=True, serialize=False)),
                ('surcharge', models.ForeignKey(blank=True, null=True, to='freight_express.AUSurchargeTier')),
                ('zone', models.ForeignKey(related_name='postcodes', to='freight_express.AUZone')),
            ],
            options={
                'verbose_name': 'AU Post Code',
            },
            bases=('freight_express.location',),
        ),
        migrations.AddField(
            model_name='ukrate',
            name='shipping_provider',
            field=models.ForeignKey(to='freight_express.UKShippingProvider', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='nzfreightrate',
            name='destinations',
            field=models.ManyToManyField(to='freight_express.NZLocation'),
        ),
        migrations.AddField(
            model_name='nzcourierrate',
            name='distance_factor',
            field=models.ForeignKey(to='freight_express.NZDistanceFactor'),
        ),
        migrations.AlterUniqueTogether(
            name='cafreightrate',
            unique_together=set([('from_province', 'to_province', 'to_city')]),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('from_zone', 'to_zone')]),
        ),
    ]
