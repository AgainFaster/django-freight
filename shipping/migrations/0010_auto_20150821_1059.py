# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0009_auto_20150821_1049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='height',
        ),
        migrations.RemoveField(
            model_name='item',
            name='length',
        ),
        migrations.RemoveField(
            model_name='item',
            name='width',
        ),
        migrations.AddField(
            model_name='item',
            name='dimensions',
            field=models.CharField(max_length=255, default={}),
            preserve_default=False,
        ),
    ]
