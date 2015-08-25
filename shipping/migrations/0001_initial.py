# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Carrier',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('carrier_code', models.CharField(help_text='Carrier Code.', max_length=5)),
                ('carrier_name', models.CharField(help_text='Carrier Name.', max_length=100)),
                ('service_code', models.CharField(help_text='Carrier Service Code.', null=True, max_length=5, blank=True)),
                ('service_code_description', models.CharField(help_text='Service Code Description.', null=True, max_length=100, blank=True)),
                ('enabled', models.BooleanField(help_text='Enable this Carrier.', default=False)),
                ('hide_from_customers', models.BooleanField(help_text='Allow customers to select this carrier as an option.', default=False)),
                ('customer_display_text', models.CharField(help_text='Name with which to override Carrier Name to customers.', null=True, max_length=25, blank=True)),
                ('url_pattern', models.CharField(null=True, max_length=200, blank=True)),
                ('include_tracking_number', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('nickname', models.CharField(help_text='Human readable name to identify account', max_length=255)),
                ('display_label', models.CharField(help_text='The default label displayed to customer if the API does not dynamically determine it.', max_length=255)),
                ('enabled', models.BooleanField(default=False)),
                ('debug', models.BooleanField(help_text='Indicates if these settings are for a test server', default=False)),
            ],
            options={
                'verbose_name_plural': 'ALL RATE SETTINGS',
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('nickname', models.CharField(help_text='Human readable name to identify rate', null=True, max_length=255, blank=True)),
                ('min_value', models.DecimalField(decimal_places=2, help_text='Minimum weight of Cart.', max_digits=10, verbose_name='Minimum weight')),
                ('max_value', models.DecimalField(decimal_places=2, help_text="Maximum weight of Cart. Set to '0' to denote no max weight.", max_digits=10, verbose_name='Maximum weight')),
                ('min_length', models.DecimalField(max_digits=10, help_text='Minimum length of shippable package..', default='0.0', decimal_places=2)),
                ('max_length', models.DecimalField(max_digits=10, help_text="Maximum length of shippable package. Set to '0' to denote no max length.", default='108.0', decimal_places=2)),
                ('min_package_size', models.DecimalField(max_digits=10, help_text='Minimum Package Size. Length + Girth (2 x length + 2 x height).', default='0.0', decimal_places=2)),
                ('max_package_size', models.DecimalField(max_digits=10, help_text="Maximum Package Size. Length + Girth (2 x length + 2 x height). Set to '0' to denote no max package weight.", default='165.0', decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Surcharge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('active', models.BooleanField(default=True)),
                ('percentage', models.BooleanField(help_text='Apply amount as a percentage', default=False, verbose_name='Is Percentage')),
                ('order', models.IntegerField(help_text='Order in which to apply surcharges (0 is applied first, then 1, etc.)', default=0)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='AustraliaPostRateRequest',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shipping.Rate', serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name_plural': 'Australia Post Settings',
                'verbose_name': 'Australia Post Settings',
            },
            bases=('shipping.rate',),
        ),
        migrations.CreateModel(
            name='CanadaPostRateRequest',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shipping.Rate', serialize=False, auto_created=True)),
                ('server', models.URLField(default='http://sellonline.canadapost.ca:30000')),
                ('cpcid', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Canada Post Settings',
                'verbose_name': 'Canada Post Settings',
            },
            bases=('shipping.rate',),
        ),
        migrations.CreateModel(
            name='FedExRateRequest',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shipping.Rate', serialize=False, auto_created=True)),
                ('auth_key', models.CharField(max_length=255, verbose_name='Authentication Key')),
                ('password', models.CharField(max_length=255, verbose_name='API Password')),
                ('account_number', models.CharField(max_length=255, verbose_name='FedEx Account Number')),
                ('meter_number', models.CharField(max_length=255, verbose_name='Meter Number')),
                ('smart_post_hub_id', models.CharField(blank=True, max_length=4, choices=[('5185', 'ALPA Allentown'), ('5303', 'ATGA Atlanta'), ('5281', 'CHNC Charlotte'), ('5602', 'CIIL Chicago'), ('5929', 'COCA Chino'), ('5751', 'DLTX Dallas'), ('5802', 'DNCO Denver'), ('5481', 'DTMI Detroit'), ('5087', 'EDNJ Edison'), ('5431', 'GCOH Grove City'), ('5771', 'HOTX Houston'), ('5465', 'ININ Indianapolis'), ('5648', 'KCKS Kansas City'), ('5902', 'LACA Los Angeles'), ('5254', 'MAWV Martinsburg'), ('5379', 'METN Memphis'), ('5552', 'MPMN Minneapolis'), ('5531', 'NBWI New Berlin'), ('5110', 'NENY Newburgh'), ('5015', 'NOMA Northborough'), ('5327', 'ORFL Orlando'), ('5194', 'PHPA Philadelphia'), ('5854', 'PHAZ Phoenix'), ('5150', 'PTPA Pittsburgh'), ('5958', 'SACA Sacramento'), ('5843', 'SCUT Salt Lake City'), ('5983', 'SEWA Seattle'), ('5631', 'STMO St. Louis')], null=True, verbose_name='FedEx SmartPost HubID')),
                ('smart_post_enable', models.BooleanField(default=False, verbose_name='Enable FedEx SmartPost')),
                ('smart_post_cutoff', models.IntegerField(help_text='Only request FedEx SmartPost rates when cart total weighs less than this amount', default=9, verbose_name='FedEx SmartPost Cutoff')),
                ('lbs_per_pallet', models.IntegerField(default=1500, verbose_name='LBS to ship per pallet')),
            ],
            options={
                'verbose_name_plural': 'FedEx Settings',
                'verbose_name': 'FedEx Settings',
            },
            bases=('shipping.rate',),
        ),
        migrations.CreateModel(
            name='FreightExpressRateRequest',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shipping.Rate', serialize=False, auto_created=True)),
                ('api_user', models.CharField(max_length=255)),
                ('api_key', models.CharField(max_length=255)),
                ('api_url', models.CharField(help_text='The url for the API call. For example: http://internal.againfaster.com/fe/api/v1/rate/cost_ca/', max_length=255)),
                ('send_sku_list', models.BooleanField(help_text='True if the API expects a list of SKUs', default=False)),
            ],
            options={
                'verbose_name_plural': 'Freight Express Settings',
                'verbose_name': 'Freight Express Settings',
            },
            bases=('shipping.rate',),
        ),
        migrations.CreateModel(
            name='ModeRateRequest',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shipping.Rate', serialize=False, auto_created=True)),
                ('userid', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('url', models.URLField()),
            ],
            options={
                'verbose_name_plural': 'Mode Tritan Settings',
                'verbose_name': 'Mode Tritan Settings',
            },
            bases=('shipping.rate',),
        ),
        migrations.CreateModel(
            name='UPSRateRequest',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shipping.Rate', serialize=False, auto_created=True)),
                ('license_number', models.CharField(max_length=255)),
                ('account_name', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('shipper_number', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'UPS Settings',
                'verbose_name': 'UPS Settings',
            },
            bases=('shipping.rate',),
        ),
        migrations.CreateModel(
            name='USPSRateRequest',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shipping.Rate', serialize=False, auto_created=True)),
                ('userid', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('server', models.URLField(default='http://production.shippingapis.com/ShippingAPI.dll')),
            ],
            options={
                'verbose_name_plural': 'USPS Settings',
                'verbose_name': 'USPS Settings',
            },
            bases=('shipping.rate',),
        ),
        migrations.AddField(
            model_name='surcharge',
            name='rate',
            field=models.ForeignKey(to='shipping.Rate'),
        ),
        migrations.AddField(
            model_name='rule',
            name='rate',
            field=models.ForeignKey(to='shipping.Rate'),
        ),
    ]
