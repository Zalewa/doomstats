#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from stats.management import storage
import datetime
import os
import shutil
import sys
import tarfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.now = datetime.datetime.now()
        batches = self._collect_batches_to_archive()
        for name, filenames in batches.items():
            self._archive_batch(name, filenames)

    def _collect_batches_to_archive(self):
        """Batches are collected per year and month, which also becomes
        their names.
        """
        sys.stderr.write("Collecting batches\n")
        sys.stderr.flush()
        batch_filenames = os.listdir(storage.batch_dir())
        months = {}
        for batch in batch_filenames:
            batch_date = storage.date_from_filename(batch)
            # Batches from current month will still grow
            # se we cannot collect them.
            if not self._is_current_month(batch_date):
                month = batch_date.strftime("%Y-%m")
                months.setdefault(month, [])
                months[month].append(batch)
        return months

    def _archive_batch(self, name, filenames):
        sys.stderr.write("Archiving {}\n".format(name))
        sys.stderr.flush()
        tmp_dir = os.path.join(storage.archive_dir(), ".tmp")
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

        # Copy all individual batch files to a directory to be tarballed.
        tmp_tar_dir = os.path.join(tmp_dir, name)
        os.makedirs(tmp_tar_dir)
        for filename in filenames:
            shutil.copy(os.path.join(storage.batch_dir(), filename),
                        os.path.join(tmp_tar_dir, filename))

        # Pack the directory in a temporary tarball.
        tar_filename = "{}.tar.bz2".format(name)
        tmp_tar_file = os.path.join(tmp_dir, tar_filename)
        with tarfile.open(tmp_tar_file, "w:bz2") as tar:
            tar.add(tmp_tar_dir, arcname=name)

        # Move the temporary tarball to its final destination.
        dest_tar_file = os.path.join(storage.archive_dir(), tar_filename)
        shutil.move(tmp_tar_file, dest_tar_file)

        # Remove the files from the batch dir and the temps - disk clean up.
        for filename in filenames:
            os.unlink(os.path.join(storage.batch_dir(), filename))
        shutil.rmtree(tmp_dir)

    def _is_current_month(self, batch_date):
        return (self.now.year == batch_date.year and
                self.now.month == batch_date.month)
