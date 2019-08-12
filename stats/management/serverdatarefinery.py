from stats.management import storage
from stats.models import (
    Engine, EngineVersion, Game, GameFile,
    GameMode, Iwad, Name, RefreshBatch, Skill)
from django.db import transaction
import json


def put_json_to_database(batch_date, data):
    put_data_to_database(batch_date, json.loads(data))


def put_data_to_database(batch_date, data):
    with open(storage.batch_file(batch_date), "w") as f:
        json.dump(data, f)
    _Servers(batch_date, data["servers"]).put()


class _Servers(object):
    def __init__(self, batch_date, data):
        self._batch_date = batch_date
        self._data = data

    def put(self):
        with transaction.atomic():
            if len(self._data) > 0:
                batch = RefreshBatch(date=self._batch_date)
                batch.save()
            for server in self._data:
                _Server(batch, server).put()


class _Server(object):
    def __init__(self, batch, data):
        self._batch = batch
        self._data = data

    @property
    def d(self):
        return self._data

    def put(self):
        engine = self._store_engine()
        if self._is_known():
            _ServerData(engine, self._data).put()

    def _is_known(self):
        return self.d["known"]

    def _store_engine(self):
        name = self.d["engineName"]
        return Engine.objects.get_or_create(
            name__iexact=name,
            defaults={"name": name})[0]


class _ServerData(object):
    def __init__(self, engine, data):
        self._engine = engine
        self._data = data

    @property
    def d(self):
        return self._data

    def put(self):
        _store_name(self.d["name"])
        self._store_game_mode()
        self._store_engine_version()
        self._store_skill()
        self._store_iwad()
        self._store_game_files()

    def _store_engine_version(self):
        return EngineVersion.objects.get_or_create(
            engine=self._engine, version=self.d["gameVersion"])[0]

    def _store_skill(self):
        game = self._store_game()
        level = self.d["skill"]
        skill, created = Skill.objects.get_or_create(
            level=level, defaults={"name": str(level)})
        if not skill.game.filter(pk=game.pk).exists():
            skill.game.add(game)
            skill.save()
        return skill

    def _store_game_mode(self):
        gamemode = self.d["gameMode"]
        defaults = {
            "name": gamemode["name"],
            "is_team_game": gamemode["isTeamGame"]
        }
        return GameMode.objects.get_or_create(
            name__iexact=gamemode["name"],
            defaults=defaults)[0]

    def _store_iwad(self):
        iwad = self.d["iwad"].lower()
        try:
            return Iwad.objects.get(name=iwad)
        except Iwad.DoesNotExist:
            return Iwad.objects.create(name=iwad, game=self._store_game())

    def _store_game(self):
        iwadname = self.d["iwad"].lower()
        try:
            iwad = Iwad.objects.get(name=iwadname)
            return iwad.game
        except Iwad.DoesNotExist:
            return Game.objects.get_or_create(name=iwadname)[0]

    def _store_game_files(self):
        for serverfile in self.d["pwads"]:
            GameFile.objects.get_or_create(
                name=serverfile["name"].lower())[0]


def _store_name(name):
    return Name.objects.get_or_create(name=name)[0]
