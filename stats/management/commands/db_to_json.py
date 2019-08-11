#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from stats.models import RefreshBatch
from stats.management import serverdatarefinery, storage
import os
import json
import shutil
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        for batch in RefreshBatch.objects.all().order_by('date'):
            self._handle_batch(batch)

    def _handle_batch(self, batch):
        if self._is_batch_stored(batch):
            return
        sys.stderr.write("Moving batch {}\n".format(batch))
        sys.stderr.flush()
        filename = storage.batch_filename(batch.date)
        filepath = os.path.join(storage.batch_dir(), filename)
        if not os.path.exists(filepath):
            batch_data = serverdatarefinery.get_database_as_data(batch)
            json_data = json.dumps(batch_data)
            if sys.version_info.major >= 3 and isinstance(json_data, str):
                json_data = json_data.encode("utf-8")
            with open(filepath + ".tmp", "wb") as f:
                f.write(json_data)
            shutil.move(filepath + ".tmp", filepath)

    @staticmethod
    def _is_batch_stored(batch):
        return os.path.isfile(os.path.join(
            storage.archive_dir(), storage.store_filename(batch.date)))
