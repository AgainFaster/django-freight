# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shipping', '0010_auto_20150821_1059'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'get_latest_by': 'id'},
        ),
        migrations.AddField(
            model_name='shippingrequest',
            name='ip',
            field=models.IPAddressField(default='127.0.0.1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shippingrequest',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=1),
            preserve_default=False,
        ),
    ]
