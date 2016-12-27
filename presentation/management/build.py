#!/usr/bin/python
#-*- coding: utf-8 -*-
from stats.models import RefreshBatch, Player, Server
from presentation.models import BatchStatistics, GameFileStatistics, \
    IwadPopularity, ServerPopularity

from django.db import transaction
from django.db.models import Count

import sys


def build_presentation(incremental=False):
    print >>sys.stderr, "Building presentation, incremental = {0}".format(incremental)
    _BatchStatisticsBuilder().build(incremental)
    _GameFileStatisticsBuilder().build(incremental)
    _ServerPopularityBuilder().build(incremental)
    _IwadPopularityBuilder().build(incremental)


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
            if engine.pk not in engines:
                presentation = BatchStatistics()
                presentation.batch = batch
                presentation.engine = engine
                engines[engine.pk] = presentation
            presentation = engines[engine.pk]
            presentation.server_count += 1
            presentation.human_player_count += Player.objects.filter(
                server__server=server,
                is_bot=False).count()
        return engines.values()


class _GameFileStatisticsBuilder(_BatchBuilder):
    def _is_batch_stored(self, batch):
        return GameFileStatistics.objects.filter(batch=batch).exists()

    def _build_batch_presentation(self, batch):
        engines = {}
        populated_servers = _populated_servers_query(batch).distinct()
        for server in populated_servers:
            players = server.data.player_set.filter(is_bot=False)
            engine = server.engine
            engines.setdefault(engine.pk, {})
            server_gamefiles = server.data.servergamefile_set
            this_server_gamefiles = set()
            for server_gamefile in server_gamefiles.all():
                gamefile = server_gamefile.gamefile
                if gamefile.pk in this_server_gamefiles:
                    # Eliminate cases where one server
                    # reports the same file more than once.
                    continue
                this_server_gamefiles.add(gamefile.pk)
                if gamefile.pk not in engines[engine.pk]:
                    presentation = GameFileStatistics()
                    presentation.batch = batch
                    presentation.engine = engine
                    presentation.gamefile = gamefile
                    engines[engine.pk][gamefile.pk] = presentation
                presentation = engines[engine.pk][gamefile.pk]
                presentation.human_player_count += players.count()
        presentations = []
        for engine in engines.itervalues():
            presentations.extend(engine.values())
        _persist(presentations)


class _ServerPopularityBuilder(_BatchBuilder):
    def _is_batch_stored(self, batch):
        return ServerPopularity.objects.filter(batch=batch).exists()

    def _build_batch_presentation(self, batch):
        # This filter already returns 1 server entry per each player.
        populated_servers = _populated_servers_query(batch)
        # All we need to do is count server entries grouped
        # by servers.
        server_population = populated_servers.values("pk").annotate(
            total=Count('pk'))
        for server in server_population:
            presentation = ServerPopularity()
            presentation.batch = batch
            presentation.server = Server.objects.get(pk=server["pk"])
            presentation.human_player_count = server["total"]
            _persist([presentation])


class _IwadPopularityBuilder(_BatchBuilder):
    def _is_batch_stored(self, batch):
        return IwadPopularity.objects.filter(batch=batch).exists()

    def _build_batch_presentation(self, batch):
        engines = {}
        populated_servers = _populated_servers_query(batch).distinct()
        for server in populated_servers:
            engine = server.engine
            engines.setdefault(engine.pk, {})
            iwad = server.data.iwad
            if iwad.pk not in engines[engine.pk]:
                presentation = IwadPopularity()
                presentation.batch = batch
                presentation.engine = engine
                presentation.iwad = iwad
                engines[engine.pk][iwad.pk] = presentation
            presentation = engines[engine.pk][iwad.pk]
            human_players = server.data.player_set.filter(is_bot=False).count()
            presentation.human_player_count += human_players
        for engine in engines.values():
            _persist(engine.values())


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


def _populated_servers_query(batch):
    return batch.server_set.filter(
        data__player__isnull=False,
        data__player__is_bot=False)
