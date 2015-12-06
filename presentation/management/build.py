#!/usr/bin/python
#-*- coding: utf-8 -*-
from stats.models import RefreshBatch, Player
from presentation.models import BatchStatistics

from django.db import transaction

import sys


def build_presentation(incremental=False):
    print >>sys.stderr, "Building presentation, incremental = {0}".format(incremental)
    batches = _get_batches(incremental)
    map(_process_batch, batches)


def _get_batches(incremental):
    if incremental:
        batches = RefreshBatch.objects.order_by("-date").all()
        for i, batch in enumerate(batches):
            if _is_present(batch):
                batches = list(batches[0:i])
                batches.reverse()
                return batches
    else:
        return list(RefreshBatch.objects.order_by("date").all())


def _process_batch(batch):
    print >>sys.stderr, "Batch: {}".format(batch)
    _build_batch_statistics(batch)


def _is_present(batch):
    return _has_batch_statistics(batch)


@transaction.atomic
def _build_batch_statistics(batch):
    if _has_batch_statistics(batch):
        return
    engines = {}
    for server in batch.server_set.all():
        engine = server.engine
        if not engine.name in engines:
            e = BatchStatistics()
            e.batch = batch
            e.engine = engine
            engines[engine.name] = e
        e = engines[engine.name]
        e.server_count += 1
        e.human_player_count += Player.objects.filter(server__server=server, is_bot=False).count()
    for batchstats in engines.itervalues():
        print >>sys.stderr, "Saving batch stats: {0}".format(batchstats)
        batchstats.save()


def _has_batch_statistics(batch):
    return BatchStatistics.objects.filter(batch=batch).exists()
