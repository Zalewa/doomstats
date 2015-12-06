# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchStatistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_count', models.IntegerField(default=0)),
                ('human_player_count', models.IntegerField(default=0)),
                ('batch', models.ForeignKey(to='stats.RefreshBatch')),
                ('engine', models.ForeignKey(to='stats.Engine')),
            ],
        ),
    ]
