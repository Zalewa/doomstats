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
        return cls.objects.filter(date__range=daterange).datetimes('date', 'day')

    @classmethod
    def hourly(cls, daterange):
        return cls.objects.filter(date__range=daterange).datetimes('date', 'hour')

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


class Address(models.Model):
    host = models.TextField()
    port = models.IntegerField()

    def __str__(self):
        return "{0}:{1}".format(self.host, self.port)


class Engine(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class EngineVersion(models.Model):
    engine = models.ForeignKey(Engine)
    version = models.TextField()

    def __str__(self):
        return self.version


class Cvar(models.Model):
    name = models.TextField()
    command = models.TextField()

    def __str__(self):
        return self.name


class DmflagsGroup(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class ServerResponse(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class ServerData(models.Model):
    name = models.ForeignKey(Name, related_name="%(app_label)s_%(class)s_name")
    mapname = models.ForeignKey(
        Name, related_name="%(app_label)s_%(class)s_mapname")
    game_mode = models.ForeignKey(GameMode)
    engine_version = models.ForeignKey(EngineVersion)
    max_players = models.IntegerField()
    max_clients = models.IntegerField()
    skill = models.ForeignKey(Skill)
    score_limit = models.IntegerField()
    time_limit = models.IntegerField()
    requires_connect_password = models.BooleanField()
    requires_join_password = models.BooleanField()
    is_secure = models.BooleanField()
    iwad = models.ForeignKey(Iwad)

    def __str__(self):
        return str(self.name)


class ServerDmflagsGroup(models.Model):
    server_data = models.ForeignKey(ServerData)
    dmflags = models.ForeignKey(DmflagsGroup)
    value = models.IntegerField()

    def __str__(self):
        return "{0}: {1}".format(self.dmflags, self.value)


class ServerModifier(models.Model):
    server_data = models.ForeignKey(ServerData)
    cvar = models.ForeignKey(Cvar)
    value = models.TextField(null=True)

    def __str__(self):
        return "{0}: {1}".format(self.cvar, self.value)


class ServerGameFile(models.Model):
    gamefile = models.ForeignKey(GameFile)
    server_data = models.ForeignKey(ServerData)
    is_optional = models.BooleanField()

    def __str__(self):
        return str(self.gamefile) + " [OPTIONAL]" if self.is_optional else ""


class Server(models.Model):
    refresh_batch = models.ForeignKey(RefreshBatch)
    address = models.ForeignKey(Address)
    response = models.ForeignKey(ServerResponse)
    engine = models.ForeignKey(Engine)
    data = models.ForeignKey(ServerData, null=True)

    def __str__(self):
        return str(self.address)

    @classmethod
    def count_in_daterange(cls, engine, daterange):
        filters = {
            "refresh_batch__date__range": daterange,
        }
        if engine is not None:
            filters["engine"] = engine
        return Server.objects.filter(**filters).count()


class Player(models.Model):
    name = models.ForeignKey(Name)
    server = models.ForeignKey(ServerData)
    is_spectating = models.BooleanField()
    is_bot = models.BooleanField()
    score = models.IntegerField()
    ping = models.IntegerField()
    team = models.IntegerField()

    def __str__(self):
        return str(self.name)

    @classmethod
    def count_in_daterange(cls, engine, daterange, also_bots=False):
        filters = {
            "server__server__refresh_batch__date__range": daterange,
        }
        if not also_bots:
            filters["is_bot"] = False
        if engine is not None:
            filters["server__server__engine"] = engine
        return Player.objects.filter(**filters).count()
