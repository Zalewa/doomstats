# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
        ('presentation', '0003_serverpopularity'),
    ]

    operations = [
        migrations.CreateModel(
            name='IwadPopularity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('human_player_count', models.IntegerField(default=0)),
                ('batch', models.ForeignKey(to='stats.RefreshBatch')),
                ('engine', models.ForeignKey(to='stats.Engine')),
                ('iwad', models.ForeignKey(to='stats.Iwad')),
            ],
        ),
    ]
