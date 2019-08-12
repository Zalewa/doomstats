from stats.management import storage
from stats.models import (
    Address, Cvar, DmflagsGroup, Engine, EngineVersion, Game, GameFile,
    GameMode, Iwad, Name, Player, RefreshBatch, Server, ServerData,
    ServerDmflagsGroup, ServerGameFile, ServerModifier, ServerResponse,
    Skill)
from django.db import transaction
import base64
import json


def put_json_to_database(batch_date, data):
    put_data_to_database(batch_date, json.loads(data))


def put_data_to_database(batch_date, data):
    with open(storage.batch_file(batch_date), "w") as f:
        json.dump(data, f)
    _Servers(batch_date, data["servers"]).put()


_SERVER_RELATED = [
    'address', 'data', 'engine', 'response',
    'data__game_mode', 'data__engine_version',
    'data__iwad', 'data__mapname', 'data__name',
    'data__skill',
    'data__serverdmflagsgroup_set',
    'data__serverdmflagsgroup_set__dmflags',
    'data__servermodifier_set',
    'data__servermodifier_set__cvar',
    'data__servergamefile_set',
    'data__servergamefile_set__gamefile',
    'data__player_set',
    'data__player_set__name'
]


def get_database_as_data(refresh_batch):
    servers = []
    for server in Server.objects.filter(
            refresh_batch=refresh_batch).prefetch_related(*_SERVER_RELATED):
        sdata = server.data
        sdata_dict = None
        if sdata:
            dmflags = [
                {
                    "name": flags.dmflags.name,
                    "value": flags.value
                } for flags in sdata.serverdmflagsgroup_set.all()
            ]
            modifiers = [
                {
                    "name": mod.cvar.name,
                    "command": mod.cvar.command,
                    "value": mod.value
                } for mod in sdata.servermodifier_set.all()
            ]
            game_files = [
                {
                    "name": gf.gamefile.name,
                    "optional": gf.is_optional
                } for gf in sdata.servergamefile_set.all()
            ]
            players = [
                {
                    "isBot": player.is_bot,
                    "isSpectating": player.is_spectating,
                    "isTeamlessBot": player.is_bot and player.team == 255,
                    "name": base64.b64encode(player.name.name),
                    "nameClean": player.name.name,
                    "ping": player.ping,
                    "score": player.score,
                    "teamNumber": player.team
                } for player in sdata.player_set.all()
            ]
            sdata_dict = {
                "dmflags": dmflags,
                "email": "",
                "gameMode": {
                    "name": sdata.game_mode.name,
                    "isTeamGame": sdata.game_mode.is_team_game
                },
                "gameVersion": sdata.engine_version.version,
                "isSecure": sdata.is_secure,
                "iwad": sdata.iwad.name,
                "map": sdata.mapname.name,
                "maxClients": sdata.max_clients,
                "maxPlayers": sdata.max_players,
                "modifiers": modifiers,
                "name": sdata.name.name,
                "players": players,
                "pwads": game_files,
                "requiresConnectPassword": sdata.requires_connect_password,
                "requiresJoinPassword": sdata.requires_join_password,
                "scoreLimit": sdata.score_limit,
                "skill": sdata.skill.level,
                "timeLimit": sdata.time_limit
            }
        server_dict = {
            "address": server.address.host,
            "engineName": server.engine.name,
            "known": sdata is not None,
            "port": server.address.port,
            "response": server.response.name,
        }
        server_dict.update(sdata_dict or {})
        servers.append(server_dict)
    return {"servers": servers}


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
        response = self._store_response()
        address = self._store_address()
        server = self._put_server(engine, response, address)
        if self._is_known():
            server.data = _ServerData(server, self._data).put()
            server.save()
        return server

    def _is_known(self):
        return self.d["known"]

    def _put_server(self, engine, response, address):
        server = Server.objects.create(
            refresh_batch=self._batch,
            address=address,
            engine=engine,
            response=response)
        return server

    def _store_engine(self):
        name = self.d["engineName"]
        return Engine.objects.get_or_create(
            name__iexact=name,
            defaults={"name": name})[0]

    def _store_response(self):
        return ServerResponse.objects.get_or_create(name=self.d["response"])[0]

    def _store_address(self):
        return Address.objects.get_or_create(
            host=self.d["address"], port=self.d["port"])[0]


class _ServerData(object):
    def __init__(self, server, data):
        self._server = server
        self._data = data

    @property
    def d(self):
        return self._data

    def put(self):
        serverdata = ServerData(
            name=_store_name(self.d["name"]),
            mapname=_store_name(self.d["map"].lower()),
            game_mode=self._store_game_mode(),
            engine_version=self._store_engine_version(),
            max_players=self.d["maxPlayers"],
            max_clients=self.d["maxClients"],
            skill=self._store_skill(),
            score_limit=self.d["scoreLimit"],
            time_limit=self.d["timeLimit"],
            requires_connect_password=self.d["requiresConnectPassword"],
            requires_join_password=self.d["requiresJoinPassword"],
            is_secure=self.d["isSecure"],
            iwad=self._store_iwad()
        )
        serverdata.save()
        self._store_dmflags(serverdata)
        self._store_game_files(serverdata)
        self._store_modifiers(serverdata)
        self._store_players(serverdata)
        return serverdata

    def _store_engine_version(self):
        return EngineVersion.objects.get_or_create(
            engine=self._server.engine, version=self.d["gameVersion"])[0]

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

    def _store_dmflags(self, serverdata):
        for dmflags in self.d["dmflags"]:
            group = DmflagsGroup.objects.get_or_create(
                name__iexact=dmflags["name"],
                defaults={"name": dmflags["name"]}
            )[0]
            ServerDmflagsGroup.objects.create(
                server_data=serverdata,
                dmflags=group,
                value=dmflags["value"])

    def _store_game_files(self, serverdata):
        for serverfile in self.d["pwads"]:
            gamefile = GameFile.objects.get_or_create(
                name=serverfile["name"].lower())[0]
            ServerGameFile.objects.create(
                gamefile=gamefile, server_data=serverdata,
                is_optional=serverfile["optional"])

    def _store_modifiers(self, serverdata):
        for modifier in self.d["modifiers"]:
            cvar = Cvar.objects.get_or_create(
                name=modifier["name"], command=modifier["command"])[0]
            ServerModifier.objects.create(
                server_data=serverdata,
                cvar=cvar,
                value=modifier["value"])

    def _store_players(self, serverdata):
        for playerdata in self.d["players"]:
            _Player(serverdata, playerdata).put()


class _Player(object):
    def __init__(self, serverdata, data):
        self._serverdata = serverdata
        self._data = data

    @property
    def d(self):
        return self._data

    def put(self):
        Player.objects.create(
            server=self._serverdata,
            name=_store_name(self.d["nameClean"]),
            is_spectating=self.d["isSpectating"],
            is_bot=self.d["isBot"],
            score=self.d["score"],
            ping=self.d["ping"],
            team=self.d["teamNumber"])


def _store_name(name):
    return Name.objects.get_or_create(name=name)[0]
