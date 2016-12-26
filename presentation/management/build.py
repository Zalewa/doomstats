#!/usr/bin/python
#-*- coding: utf-8 -*-
from stats.models import RefreshBatch, Player
from presentation.models import BatchStatistics

from django.db import transaction

import sys


def build_presentation(incremental=False):
    print >>sys.stderr, "Building presentation, incremental = {0}".format(incremental)
    if incremental:
        batches = _get_newest_not_stored_batches()
    else:
        batches = _get_all_batches()
    map(_process_batch, batches)


def _get_newest_not_stored_batches():
    batches = RefreshBatch.objects.order_by("-date").all()
    for i, batch in enumerate(batches):
        if _is_already_stored(batch):
            batches = list(batches[0:i])
            break
    batches = list(batches)
    batches.reverse()
    return batches


def _get_all_batches():
    return list(RefreshBatch.objects.order_by("date").all())


def _process_batch(batch):
    print >>sys.stderr, "Batch: {}".format(batch)
    _build_batch_statistics(batch)


def _is_already_stored(batch):
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
