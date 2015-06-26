#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from doomstats.timestuff import parse_rfc3339_stamp
from stats.management import serverdatarefinery
import os
import sys
import datetime
import subprocess
import tempfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        with tempfile.TemporaryFile() as f:
            p = subprocess.Popen(['doomlister'], stdout=f)
            if p.wait() != 0:
                raise Exception('doomlister failed')
            f.seek(0)
            data = f.read()
        serverdatarefinery.put_json_to_database(timezone.now(), data)
