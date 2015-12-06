from django.db import models
from django.db.models import Sum, Avg
from stats.models import RefreshBatch, Engine


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


class _Aggregate(object):
    pass
