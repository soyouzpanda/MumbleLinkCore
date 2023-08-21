import config_manager
import logging
import Murmur
import uuid
from utils import Utils


class MumbleServer:
    servers: dict = {}

    @staticmethod
    def get_servers():
        return MumbleServer.servers

    def __init__(self, murmur, config: config_manager.ConfigManager):
        self.config = config
        self.server = murmur.newServer()
        self.server.start()
        self.id = str(uuid.uuid4())
        self.create()
        self.mumble_id = len(MumbleServer.servers)
        self.port = self.mumble_id + \
            self.config.read("MUMBLE", "first_port", 64738)
        self.users = {}
        self.users_by_name = {}
        self.user_group_list = []
        self.admin_group_list = []
        MumbleServer.servers[self.id] = self

    def create(self):
        if self.config.read("LOG", "create", True):
            logging.info(f"Create server")
        self.usergroup = Murmur.Group()
        self.usergroup.name = "PlayerMC"
        self.usergroup.add = []
        self.usergroup.remove = []
        self.useracl = Murmur.ACL()
        self.useracl.applyHere = True
        self.useracl.applySubs = True
        self.useracl.group = "PlayerMC"
        self.useracl.allow = Murmur.PermissionSpeak
        self.useracl.deny = Murmur.PermissionWrite | Murmur.PermissionEnter

        self.admingroup = Murmur.Group()
        self.admingroup.name = "AdminMC"
        self.admingroup.add = []
        self.admingroup.remove = []
        self.adminacl = Murmur.ACL()
        self.adminacl.applyHere = True
        self.adminacl.applySubs = True
        self.adminacl.group = "AdminMC"
        self.adminacl.allow = Murmur.PermissionSpeak | Murmur.PermissionMuteDeafen | Murmur.PermissionEnter | Murmur.PermissionKick | Murmur.PermissionTextMessage
        self.adminacl.deny = Murmur.PermissionWrite

        self.outacl = Murmur.ACL()
        self.outacl.applyHere = True
        self.outacl.applySubs = True
        self.outacl.group = "out"
        self.outacl.deny = Murmur.PermissionSpeak

        self.game_channel = self.server.addChannel("Game", 0)
        self.spectator_channel = self.server.addChannel("Spectateur", 0)

        gamestate = self.server.getChannelState(self.game_channel)
        gamestate.links = [self.spectator_channel]
        self.server.setChannelState(gamestate)

        self.server.setConf(
            "registername",
            self.config.read(
                "MUMBLE",
                "default_name",
                "MumbleLink par EliottBvl."))
        self.server.setConf(
            "serverpassword",
            self.config.read(
                "MUMBLE",
                "server_password",
                "CHANGEMENOWINCONFIGINI"))
        self.server.setSuperuserPassword(
            self.config.read(
                "MUMBLE",
                "superuser_password",
                "CHANGEMENOWINCONFIGINI"))

        if self.config.read("LOG", "create", True):
            print("> Creating server " + self.id + ".")

    def set_title(self, text):
        self.server.setConf("registername", text)

    def create_user(self, username):
        if username in self.users_by_name.keys():
            return self.users_by_name[username]
        id = str(uuid.uuid4())
        password = str(uuid.uuid4())
        mumbleid = self.server.registerUser({
            Murmur.UserInfo.UserName: username,
            Murmur.UserInfo.UserPassword: password
        })

        self.users[id] = {
            "id": mumbleid,
            "username": username,
            "password": password
        }
        self.users_by_name[username] = id

        self.set_user_player(id)

        if self.config.read("LOG", "create-user", True):
            logging.info(f"Create user {username}({id}) on server {self.id}")

        return id

    def set_user_admin(self, userid):
        if self.config.read("LOG", "set-admin-perms", True):
            logging.info(
                f"Set admin permissions to user {userid} on server {self.id}")
        self.admin_group_list.append(self.users[userid]['id'])
        self.admingroup.add = self.admin_group_list
        if self.users[userid]['id'] in self.admingroup.remove:
            self.admingroup.remove.remove(self.users[userid]['id'])
        if self.users[userid]['id'] in self.user_group_list:
            self.user_group_list.remove(self.users[userid]['id'])
            self.usergroup.remove.append(self.users[userid]['id'])
            self.usergroup.add = self.user_group_list
        for channel in self.server.getChannels():
            self.server.setACL(
                channel, [
                    self.adminacl, self.useracl, self.outacl], [
                    self.admingroup, self.usergroup], True)

    def set_user_player(self, userid):
        if self.config.read("LOG", "set-player-perms", True):
            logging.info(
                f"Set player permissions to user {userid} on server {self.id}")
        self.user_group_list.append(self.users[userid]['id'])
        self.usergroup.add = self.user_group_list
        if self.users[userid]['id'] in self.usergroup.remove:
            self.usergroup.remove.remove(self.users[userid]['id'])
        if self.users[userid]['id'] in self.admin_group_list:
            self.admin_group_list.remove(self.users[userid]['id'])
            self.admingroup.remove.append(self.users[userid]['id'])
            self.admingroup.add = self.admin_group_list
        for channel in self.server.getChannels():
            if channel == 1:
                self.server.setACL(
                    channel, [
                        self.adminacl, self.useracl, self.outacl], [
                        self.admingroup, self.usergroup], True)
            else:
                self.server.setACL(
                    channel, [
                        self.adminacl, self.useracl], [
                        self.admingroup, self.usergroup], True)

    def mute(self, userid):
        if self.config.read("LOG", "mute", True):
            logging.info(f"Mute user {userid} on server {self.id}")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        if user is None:
            return
        state = self.server.getState(user.session)
        state.mute = True
        state.suppress = True

        self.server.setState(state)

    def unmute(self, userid):
        if self.config.read("LOG", "unmute", True):
            logging.info(f"Unmute user {userid} on server {self.id}")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        if user is None:
            return
        state = self.server.getState(user.session)
        state.mute = False
        state.suppress = False

        self.server.setState(state)

    def move(self, userid, channel):
        if self.config.read("LOG", "move", True):
            logging.info(
                f"Move user {userid} to channel {channel} on server {self.id}")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        if user is None:
            return
        state = self.server.getState(user.session)
        state.channel = channel

        self.server.setState(state)

    def mute_all(self):
        if self.config.read("LOG", "mute-all", True):
            logging.info(f"Mute all users on server {self.id}")
        for id in self.users.keys():
            self.mute(id)

    def unmute_all(self):
        if self.config.read("LOG", "unmute-all", True):
            logging.info(f"Unmute all users on server {self.id}")
        for id in self.users.keys():
            self.unmute(id)

    def move_all(self, channel):
        if self.config.read("LOG", "move-all", True):
            logging.info(
                f"Move all users to channel {channel} on server {self.id}")
        for id in self.users.keys():
            self.move(id, channel)

    def get_user_info(self, userid, log=True):
        if log and self.config.read(
                "LOG", "get-user-info", True):
            logging.info(f"Request user {userid} info on server {self.id}")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        info = {"id": userid, "username": self.users[userid]["username"]}
        if user is not None:
            info["connected"] = True
            info["channel"] = user.channel
            info["mute"] = user.mute
            info["selfMute"] = user.selfMute
            info["selfDeaf"] = user.selfDeaf
            info["link"] = user.identity != ""
        else:
            info["connected"] = False
            info["channel"] = -1
            info["mute"] = False
            info["selfMute"] = False
            info["selfDeaf"] = False
            info["link"] = False
        return info

    def get_users_info(self):
        if self.config.read("LOG", "get-users-info", True):
            logging.info(f"Request users information on server {self.id}")
        infos = []
        for id in self.users_by_name.values():
            infos.append(self.get_user_info(id, False))
        return infos

    def delete(self):
        if self.config.read("LOG", "delete", True):
            logging.info(f"Deleting server {self.id}")
        if self.server.isRunning():
            self.server.stop()
        self.server.delete()
        MumbleServer.servers.pop(self.id)
        del self
