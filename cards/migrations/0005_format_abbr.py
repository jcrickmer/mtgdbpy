# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0004_auto_20160118_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='format',
            name='abbr',
            field=models.CharField(max_length=6, null=True),
            preserve_default=True,
        ),
        migrations.RunSQL("UPDATE format SET abbr = 'EDH' WHERE formatname = 'Commander'"),
        migrations.RunSQL("UPDATE format SET abbr = 'Mod' WHERE formatname = 'Modern'"),
        migrations.RunSQL("UPDATE format SET abbr = 'Std' WHERE formatname = 'Standard'"),
        migrations.RunSQL("UPDATE format SET abbr = 'TL' WHERE formatname = 'TinyLeaders'"),
        migrations.RunSQL("UPDATE format SET abbr = 'BFZ' WHERE formatname = 'BattleforZendikar'"),
    ]
