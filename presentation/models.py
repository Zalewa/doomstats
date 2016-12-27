from django.db import models
from django.db.models import Sum, Avg
from stats.models import RefreshBatch, Engine, GameFile, Iwad, Server


class BatchStatistics(models.Model):
    batch = models.ForeignKey(RefreshBatch)
    engine = models.ForeignKey(Engine)
    server_count = models.IntegerField(default=0)
    human_player_count = models.IntegerField(default=0)

    @classmethod
    def sum_in_daterange(cls, engine, daterange):
        return cls.aggregate(engine, daterange, Sum)

    @classmethod
    def avg_in_daterange(cls, engine, daterange):
        return cls.aggregate(engine, daterange, Avg)

    @classmethod
    def aggregate(cls, engine, daterange, method):
        fields = ["server_count", "human_player_count"]
        aggregates = []
        for f in fields:
            aggregates.append(method(f))
        filters = cls._mk_filter(engine, daterange)
        query = cls.objects.filter(**filters)
        if not engine:
            sums = {}
            for f in fields:
                sums[f] = Sum(f)
            query = query.values("batch").annotate(**sums)
        aggregate = query.aggregate(*aggregates)
        return cls._normalize_aggregate(engine, aggregate, method)

    @classmethod
    def _normalize_aggregate(cls, engine, aggregate, method):
        name = method.__name__.lower()
        e = _Aggregate()
        e.engine = engine
        e.server_count = aggregate["server_count__{0}".format(name)]
        e.human_player_count = aggregate["human_player_count__{0}".format(name)]
        return e

    @staticmethod
    def _mk_filter(engine, daterange):
        filters = {
            "batch__date__range": daterange
        }
        if engine is not None:
            filters["engine"] = engine
        return filters

    def __format__(self, format_spec):
        return "engine={0}, server_count={1}, human_player_count={2}".format(
            self.engine, self.server_count, self.human_player_count)


class GameFileStatistics(models.Model):
    batch = models.ForeignKey(RefreshBatch)
    engine = models.ForeignKey(Engine)
    gamefile = models.ForeignKey(GameFile)
    human_player_count = models.IntegerField(default=0)

    @classmethod
    def top(cls, engine, daterange, amount):
        filters = {
            "batch__date__range": daterange,
            "engine": engine,
            "human_player_count__gt": 0
        }
        query = cls.objects.filter(**filters)
        query = query.values("gamefile__name")
        query = query.annotate(human_player_count=Avg("human_player_count"))
        query = query.order_by('-human_player_count')[:amount]
        return query

    def __format__(self, format_spec):
        return ("engine={0.engine}, gamefile={0.gamefile}, "
                "human_player_count={0.human_player_count}").format(self)


class ServerPopularity(models.Model):
    batch = models.ForeignKey(RefreshBatch)
    server = models.ForeignKey(Server)
    human_player_count = models.IntegerField(default=0)

    @classmethod
    def top(cls, engine, daterange, amount):
        filters = {
            "batch__date__range": daterange,
            "server__engine": engine,
            "human_player_count__gt": 0
        }
        query = cls.objects.filter(**filters)
        query = query.values("server__address__host", "server__address__port",
                             "server__data__name__name")
        query = query.annotate(human_player_count=Avg("human_player_count"))
        query = query.order_by('-human_player_count')[:amount]
        return query

    def __format__(self, format_spec):
        return (u"engine={0.server.engine}, name={0.server.data.name}, "
                "human_player_count={0.human_player_count}").format(self).encode("utf-8")


class IwadPopularity(models.Model):
    batch = models.ForeignKey(RefreshBatch)
    engine = models.ForeignKey(Engine)
    iwad = models.ForeignKey(Iwad)
    human_player_count = models.IntegerField(default=0)

    @classmethod
    def top(cls, engine, daterange):
        filters = {
            "batch__date__range": daterange,
            "engine": engine,
            "human_player_count__gt": 0
        }
        query = cls.objects.filter(**filters)
        query = query.values("iwad__name")
        query = query.annotate(human_player_count=Avg("human_player_count"))
        query = query.order_by('-human_player_count')
        return query

    def __format__(self, format_spec):
        return (u"engine={0.engine}, name={0.iwad.name}, "
                "human_player_count={0.human_player_count}").format(self).encode("utf-8")


class _Aggregate(object):
    pass
