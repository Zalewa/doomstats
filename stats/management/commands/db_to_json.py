#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from stats.models import RefreshBatch
from stats.management import serverdatarefinery, storage
import os
import json
import multiprocessing
import shutil
import sys


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'jobs', nargs='?', type=int, default=1,
            help='number of parallel jobs')

    def handle(self, *args, **options):
        num_jobs = options['jobs']
        pool = multiprocessing.Pool(num_jobs)
        try:
            batches = pool.apply(_get_batches)
            sys.stderr.write("{} batches left to move\n".format(len(batches)))
            sys.stderr.flush()

            pool.map(_handle_batch, batches)
            pool.close()
        except BaseException as e:
            pool.terminate()
            if not isinstance(e, KeyboardInterrupt):
                raise
        finally:
            pool.join()


def _get_batches():
    try:
        batches = RefreshBatch.objects.all().order_by('date')
        batches = [batch for batch in batches if not _is_batch_stored(batch)]
        return batches
    except BaseException as e:
        raise Exception(str(e))


def _handle_batch(batch):
    try:
        sys.stderr.write("Moving batch {}\n".format(batch))
        sys.stderr.flush()
        batch_data = serverdatarefinery.get_database_as_data(batch)
        json_data = json.dumps(batch_data)
        if sys.version_info.major >= 3 and isinstance(json_data, str):
            json_data = json_data.encode("utf-8")
        filename = storage.batch_filename(batch.date)
        filepath = os.path.join(storage.batch_dir(), filename)
        with open(filepath + ".tmp", "wb") as f:
            f.write(json_data)
        shutil.move(filepath + ".tmp", filepath)
    except BaseException as e:
        raise Exception(str(e))


def _is_batch_stored(batch):
    batchfile_name = storage.batch_filename(batch.date)
    batchfile_path = os.path.join(storage.batch_dir(), batchfile_name)
    archive_filename = storage.archive_filename(batch.date)
    archive_path = os.path.join(storage.archive_dir(), archive_filename)
    return (os.path.isfile(batchfile_path) or
            os.path.isfile(archive_path))
