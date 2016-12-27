#!/usr/bin/python
#-*- coding: utf-8 -*-
from stats.models import RefreshBatch, Player
from presentation.models import BatchStatistics

from django.db import transaction

import sys


def build_presentation(incremental=False):
    print >>sys.stderr, "Building presentation, incremental = {0}".format(incremental)
    _BatchStatisticsBuilder().build(incremental)


class _BatchBuilder(object):
    def build(self, incremental):
        if incremental:
            batches = _get_newest_not_stored_batches(
                is_stored_check=self._is_batch_stored)
        else:
            batches = _get_all_batches()
        map(self.__process_batch, batches)

    def _is_batch_stored(self, batch):
        raise NotImplementedError()

    def _build_batch_presentation(self, batch):
        raise NotImplementedError()

    def __process_batch(self, batch):
        print >>sys.stderr, "[{}] Batch: {}".format(type(self).__name__, batch)
        with transaction.atomic():
            if not self._is_batch_stored(batch):
                self._build_batch_presentation(batch)


class _BatchStatisticsBuilder(_BatchBuilder):
    def _is_batch_stored(self, batch):
        return BatchStatistics.objects.filter(batch=batch).exists()

    def _build_batch_presentation(self, batch):
        presentations = self._build(batch)
        _persist(presentations)

    def _build(self, batch):
        engines = {}
        for server in batch.server_set.all():
            engine = server.engine
            if engine.name not in engines:
                presentation = BatchStatistics()
                presentation.batch = batch
                presentation.engine = engine
                engines[engine.name] = presentation
            presentation = engines[engine.name]
            presentation.server_count += 1
            presentation.human_player_count += Player.objects.filter(
                server__server=server,
                is_bot=False).count()
        return engines.values()


def _get_newest_not_stored_batches(is_stored_check):
    batches = RefreshBatch.objects.order_by("-date").all()
    for i, batch in enumerate(batches):
        if is_stored_check(batch):
            batches = list(batches[0:i])
            break
    batches = list(batches)
    batches.reverse()
    return batches


def _get_all_batches():
    return list(RefreshBatch.objects.order_by("date").all())


def _persist(presentations):
    for presentation in presentations:
        print >>sys.stderr, "Saving presentation: {0}".format(presentation)
        presentation.save()
