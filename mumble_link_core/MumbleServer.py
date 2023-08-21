from configManager import configManager
from mumbleManager import MumbleManager
import uuid

from utils import Utils


class MumbleServer:
    servers = {}

    @staticmethod
    def getServers():
        return MumbleServer.servers

    def __init__(self, Murmur):
        self.server = Murmur.newServer()
        self.server.start()
        self.id = str(uuid.uuid4())
        self.creationDo()
        self.mumbleid = len(MumbleServer.servers)
        self.port = self.mumbleid + int(configManager.read("MUMBLE", "first_port", 64738))
        self.users = {}
        self.usersbyname = {}
        self.usergrouplist = []
        self.admingrouplist = []
        MumbleServer.servers[self.id] = self

    def creationDo(self):
        if configManager.read("LOG", "create", "true") == "true":
            print("> Request creating server.")
        self.usergroup = MumbleManager.murmur.Group()
        self.usergroup.name = "PlayerMC"
        self.usergroup.add = []
        self.usergroup.remove = []
        self.useracl = MumbleManager.murmur.ACL()
        self.useracl.applyHere = True
        self.useracl.applySubs = True
        self.useracl.group = "PlayerMC"
        self.useracl.allow = MumbleManager.murmur.PermissionSpeak
        self.useracl.deny = MumbleManager.murmur.PermissionWrite | MumbleManager.murmur.PermissionEnter

        self.admingroup = MumbleManager.murmur.Group()
        self.admingroup.name = "AdminMC"
        self.admingroup.add = []
        self.admingroup.remove = []
        self.adminacl = MumbleManager.murmur.ACL()
        self.adminacl.applyHere = True
        self.adminacl.applySubs = True
        self.adminacl.group = "AdminMC"
        self.adminacl.allow = MumbleManager.murmur.PermissionSpeak | MumbleManager.murmur.PermissionMuteDeafen | MumbleManager.murmur.PermissionEnter | MumbleManager.murmur.PermissionKick | MumbleManager.murmur.PermissionTextMessage
        self.adminacl.deny = MumbleManager.murmur.PermissionWrite

        self.outacl = MumbleManager.murmur.ACL()
        self.outacl.applyHere = True
        self.outacl.applySubs = True
        self.outacl.group = "out"
        self.outacl.deny = MumbleManager.murmur.PermissionSpeak

        self.game_channel = self.server.addChannel("Game", 0)
        self.spectator_channel = self.server.addChannel("Spectateur", 0)

        gamestate = self.server.getChannelState(self.game_channel)
        gamestate.links = [self.spectator_channel]
        self.server.setChannelState(gamestate)

        self.server.setConf("registername", configManager.read("MUMBLE", "default_name", "MumbleLink par EliottBvl."))
        self.server.setConf("serverpassword", configManager.read("MUMBLE", "server_password", "CHANGEMENOWINCONFIGINI"))
        self.server.setSuperuserPassword(configManager.read("MUMBLE", "superuser_password", "CHANGEMENOWINCONFIGINI"))

        if configManager.read("LOG", "create", "true") == "true":
            print("> Creating server " + self.id + ".")

    def setTitle(self, text):
        self.server.setConf("registername", text)

    def createUser(self, username):
        if configManager.read("LOG", "create-user", "true") == "true":
            print("> Request create user " + username + " on server " + self.id + ".")
        if username in self.usersbyname.keys():
            return self.usersbyname[username]
        id = str(uuid.uuid4())
        password = str(uuid.uuid4())
        mumbleid = self.server.registerUser({
            MumbleManager.murmur.UserInfo.UserName: username,
            MumbleManager.murmur.UserInfo.UserPassword: password
        })

        self.users[id] = {
            "id": mumbleid,
            "username": username,
            "password": password
        }
        self.usersbyname[username] = id

        self.setUserPlayer(id)
        print("> Create user " + username + "( " + id + ")" + " on server " + self.id + ".")

        return id

    def setUserAdmin(self, userid):
        if configManager.read("LOG", "set-admin-perms", "true") == "true":
            print("> Request set administrator permissions to user " + userid + " on server " + self.id + ".")
        self.admingrouplist.append(self.users[userid]['id'])
        self.admingroup.add = self.admingrouplist
        if self.users[userid]['id'] in self.admingroup.remove:
            self.admingroup.remove.remove(self.users[userid]['id'])
        if self.users[userid]['id'] in self.usergrouplist:
            self.usergrouplist.remove(self.users[userid]['id'])
            self.usergroup.remove.append(self.users[userid]['id'])
            self.usergroup.add = self.usergrouplist
        for channel in self.server.getChannels():
            self.server.setACL(channel, [self.adminacl, self.useracl, self.outacl], [self.admingroup, self.usergroup], True)

    def setUserPlayer(self, userid):
        if configManager.read("LOG", "set-player-perms", "true") == "true":
            print("> Request set player permissions to user " + userid + " on server " + self.id + ".")
        self.usergrouplist.append(self.users[userid]['id'])
        self.usergroup.add = self.usergrouplist
        if self.users[userid]['id'] in self.usergroup.remove:
            self.usergroup.remove.remove(self.users[userid]['id'])
        if self.users[userid]['id'] in self.admingrouplist:
            self.admingrouplist.remove(self.users[userid]['id'])
            self.admingroup.remove.append(self.users[userid]['id'])
            self.admingroup.add = self.admingrouplist
        for channel in self.server.getChannels():
            if channel == 1:
                self.server.setACL(channel, [self.adminacl, self.useracl, self.outacl], [self.admingroup, self.usergroup], True)
            else:
                self.server.setACL(channel, [self.adminacl, self.useracl], [self.admingroup, self.usergroup], True)

    def mute(self, userid):
        if configManager.read("LOG", "mute", "true") == "true":
            print("> Request mute user " + userid + " on server " + self.id + ".")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        if user is None:
            return
        state = self.server.getState(user.session)
        state.mute = True
        state.suppress = True

        self.server.setState(state)

    def unmute(self, userid):
        if configManager.read("LOG", "unmute", "true") == "true":
            print("> Request unmute user " + userid + " on server " + self.id + ".")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        if user is None:
            return
        state = self.server.getState(user.session)
        state.mute = False
        state.suppress = False

        self.server.setState(state)

    def move(self, userid, channel):
        if configManager.read("LOG", "move", "true") == "true":
            print("> Request move user " + str(userid) + " to channel " + str(channel) + " on server " + str(self.id) + ".")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        if user is None:
            return
        state = self.server.getState(user.session)
        state.channel = channel

        self.server.setState(state)

    def muteall(self):
        if configManager.read("LOG", "mute-all", "true") == "true":
            print("> Request mute all users on server " + self.id + ".")
        for id in self.users.keys():
            self.mute(id)

    def unmuteall(self):
        if configManager.read("LOG", "unmute-all", "true") == "true":
            print("> Request unmute all users on server " + self.id + ".")
        for id in self.users.keys():
            self.unmute(id)

    def moveall(self, channel):
        if configManager.read("LOG", "move-all", "true") == "true":
            print("> Request move all users to channel " + str(channel) + " on server " + str(self.id) + ".")
        for id in self.users.keys():
            self.move(id, channel)

    def getuserinfo(self, userid, log=True):
        if log and configManager.read("LOG", "get-user-info", "true") == "true":
            print("> Request user " + userid + " information on server " + self.id + ".")
        user = Utils.get_user(self.server, self.users[userid]["id"])
        info = {}
        info["id"] = userid
        info["username"] = self.users[userid]["username"]
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

    def getusersinfo(self):
        if configManager.read("LOG", "get-users-info", "true") == "true":
            print("> Request users information on server " + self.id + ".")
        infos = []
        for id in self.usersbyname.values():
            infos.append(self.getuserinfo(id, False))
        return infos

    def delete(self):
        if configManager.read("LOG", "delete", "true") == "true":
            print("> Deleting server " + self.id + ".")
        if self.server.isRunning():
            self.server.stop()
        self.server.delete()
        MumbleServer.servers.pop(self.id)
        del self
