from django.db import models
from django.utils import timezone


class Name(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class RefreshBatch(models.Model):
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.date)

    @classmethod
    def daily(cls, daterange):
        return cls.slice(daterange, 'day')

    @classmethod
    def hourly(cls, daterange):
        return cls.slice(daterange, 'hour')

    @classmethod
    def slice(cls, daterange, resolution):
        return cls.objects.filter(date__range=daterange).datetimes(
            'date', resolution)


class GameMode(models.Model):
    name = models.TextField(unique=True)
    is_team_game = models.BooleanField()

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class GameFile(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Iwad(models.Model):
    name = models.TextField(unique=True)
    game = models.ForeignKey(Game)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.TextField()
    level = models.IntegerField()
    game = models.ManyToManyField(Game)

    def __str__(self):
        return "{0} - {1}".format(self.level, self.name)


class Engine(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class EngineVersion(models.Model):
    engine = models.ForeignKey(Engine)
    version = models.TextField()

    def __str__(self):
        return self.version
