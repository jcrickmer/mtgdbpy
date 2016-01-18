# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0003_auto_20150320_1910'),
    ]

    operations = [
        migrations.RunSQL("UPDATE color SET id = 'C' WHERE id = 'c'"),
        migrations.RunSQL("UPDATE cardcolor SET color_id = 'C' WHERE  color_id = 'c'"),
    ]
