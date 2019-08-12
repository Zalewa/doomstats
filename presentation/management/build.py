#!/usr/bin/python
#-*- coding: utf-8 -*-
from stats.management import storage
from stats.models import Engine, GameFile, Iwad, Name, RefreshBatch
from presentation.models import BatchStatistics, GameFileStatistics, \
    IwadPopularity, ServerPopularity

from django.db import transaction

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
        for batch in batches:
            self.__process_batch(batch)

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
        for server in _servers(batch):
            engine = server["engineName"]
            if engine not in engines:
                presentation = BatchStatistics()
                presentation.batch = batch
                presentation.engine = Engine.objects.filter(name__iexact=engine).first()
                engines[engine] = presentation
            presentation = engines[engine]
            presentation.server_count += 1
            presentation.human_player_count += len(_human_players(server))
        return engines.values()


class _GameFileStatisticsBuilder(_BatchBuilder):
    def _is_batch_stored(self, batch):
        return GameFileStatistics.objects.filter(batch=batch).exists()

    def _build_batch_presentation(self, batch):
        engines = {}
        populated_servers = _populated_servers(batch)
        for server in populated_servers:
            players = _human_players(server)
            engine = server["engineName"]
            engines.setdefault(engine, {})
            server_gamefiles = server["pwads"]
            this_server_gamefiles = set()
            for server_gamefile in server_gamefiles:
                gamefile = server_gamefile["name"]
                if gamefile in this_server_gamefiles:
                    # Eliminate cases where one server
                    # reports the same file more than once.
                    continue
                this_server_gamefiles.add(gamefile)
                if gamefile not in engines[engine]:
                    presentation = GameFileStatistics()
                    presentation.batch = batch
                    presentation.engine = Engine.objects.filter(name__iexact=engine).first()
                    presentation.gamefile = GameFile.objects.filter(name__iexact=gamefile).first()
                    engines[engine][gamefile] = presentation
                presentation = engines[engine][gamefile]
                presentation.human_player_count += len(players)
        presentations = []
        for engine in engines.itervalues():
            presentations.extend(engine.values())
        _persist(presentations)


class _ServerPopularityBuilder(_BatchBuilder):
    def _is_batch_stored(self, batch):
        return ServerPopularity.objects.filter(batch=batch).exists()

    def _build_batch_presentation(self, batch):
        engines = {}
        for server in _populated_servers(batch):
            engine = server["engineName"]
            if engine not in engines:
                engines[engine] = Engine.objects.filter(name__iexact=engine).first()

            presentation = ServerPopularity()
            presentation.batch = batch
            presentation.engine = engines[engine]
            presentation.server_name = Name.objects.get_or_create(name=server["name"])[0]
            presentation.human_player_count = len(_human_players(server))
            _persist([presentation])


class _IwadPopularityBuilder(_BatchBuilder):
    def _is_batch_stored(self, batch):
        return IwadPopularity.objects.filter(batch=batch).exists()

    def _build_batch_presentation(self, batch):
        engines = {}
        iwads = {iwad.name.lower(): iwad for iwad in Iwad.objects.all()}
        for server in _populated_servers(batch):
            engine = server["engineName"]
            engines.setdefault(engine, {})
            iwad = iwads[server["iwad"].lower()]
            if iwad.pk not in engines[engine]:
                presentation = IwadPopularity()
                presentation.batch = batch
                presentation.engine = Engine.objects.filter(name__iexact=engine).first()
                presentation.iwad = iwad
                engines[engine][iwad.pk] = presentation
            presentation = engines[engine][iwad.pk]
            presentation.human_player_count += len(_human_players(server))
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


def _populated_servers(batch):
    return [s for s in _servers(batch)
            if s.get("players") and _human_players(s)]


def _human_players(server):
    return [p for p in server.get("players", []) if not p["isBot"]]


def _servers(batch):
    return storage.read_batch(batch.date)["servers"]
