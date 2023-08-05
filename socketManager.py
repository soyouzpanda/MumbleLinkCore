import json
import socket, threading

from MumbleServer import MumbleServer
from configManager import configManager
from utils import Utils


class SocketManager:

    def __init__(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(
                (configManager.read("SOCKET", "ip", "127.0.0.1"), int(configManager.read("SOCKET", "port", "751"))))
            self.server.listen(512)
        except:
            print("Error during socket starting.")
            Utils.close()

        try:
            self.print_lock = threading.Lock()
            self.thread = threading.Thread(target=SocketManager.thread, args=(self,))
            self.thread.start()
        except:
            print("Error during socket listening.")

    def join(self):
        self.thread.join()

    def thread(self):
        while True:
            c, addr = self.server.accept()
            length_of_message = int.from_bytes(c.recv(2), byteorder='big')
            data = c.recv(length_of_message)
            if not data:
                continue

            reponse = {
                "code": 200
            }
            try:
                jdata = json.loads(data.decode('utf-8'))
            except:
                print("> Error during decode request. IP: " + str(addr[0]) + ':' + str(addr[1]))
                reponse["code"] = 500
                reponse["error"] = "Error during decode request."
                c.send(bytes(json.dumps(reponse), 'utf-8'))
                continue

            if str(configManager.read("AUTH", "api-key", "CHANGEMETOO")) == "CHANGEMETOO" or "api-key" not in jdata.keys() or str(jdata["api-key"]) != str(configManager.read("AUTH", "api-key", "CHANGEMETOO")):
                reponse["code"] = 403
                reponse["error"] = "Erreur d'Authentification."
                print("> Socket authentification failed. IP: " + str(addr[0]) + ':' + str(addr[1]))
                c.send(bytes(json.dumps(reponse), 'utf-8'))
                continue

            if "action" not in jdata.keys():
                reponse["code"] = 500
                reponse["error"] = "Aucune action précisée."
                c.send(bytes(json.dumps(reponse), 'utf-8'))
                continue

            if "server" not in jdata.keys() and jdata["action"] != "create":
                reponse["code"] = 500
                reponse["error"] = "Aucun serveur précisé."
                c.send(bytes(json.dumps(reponse), 'utf-8'))
                continue

            if "server" in jdata.keys() and jdata["action"] != "create" and jdata[
                "server"] not in MumbleServer.servers.keys():
                reponse["code"] = 500
                reponse["error"] = "Serveur inexistant."
                c.send(bytes(json.dumps(reponse), 'utf-8'))
                continue
            if jdata["action"] == "create":
                server = MumbleServer(Utils.mumbleManager.meta)
                uuid = server.id
                if "title" in jdata.keys():
                    server.setTitle(str(jdata["title"]))
                reponse["id"] = uuid
            elif jdata["action"] == "check-server":
                reponse["message"] = "Ce serveur existe bien."
            elif jdata["action"] == "delete":
                server = MumbleServer.servers[jdata["server"]]
                server.delete()
            elif jdata["action"] == "create-user":
                if "username" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = MumbleServer.servers[jdata["server"]]
                if username in server.usersbyname.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur déjà existant."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue

                uuid = server.createUser(username)
                reponse["id"] = uuid
            elif jdata["action"] == "mute":
                if "username" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                server.mute(username)
            elif jdata["action"] == "unmute":
                if "username" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                server.unmute(username)
            elif jdata["action"] == "mute-all":
                server = MumbleServer.servers[jdata["server"]]
                server.muteall()
            elif jdata["action"] == "unmute-all":
                server = MumbleServer.servers[jdata["server"]]
                server.unmuteall()
            elif jdata["action"] == "set-admin-perms":
                if "username" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                server.setUserAdmin(username)
            elif jdata["action"] == "set-player-perms":
                if "username" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                server.setUserPlayer(username)
            elif jdata["action"] == "get-user-info":
                if "username" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                reponse["data"] = server.getuserinfo(username)
            elif jdata["action"] == "get-users-info":
                server = MumbleServer.servers[jdata["server"]]
                reponse["data"] = server.getusersinfo()
            elif jdata["action"] == "move":
                if "username" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                if "channel" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Channel non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                username = str(jdata["username"])
                try:
                    channel = int(jdata["channel"])
                except:
                    reponse["code"] = 500
                    reponse["error"] = "Channel non valide."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                server = MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                server.move(username, channel)
            elif jdata["action"] == "move-all":
                if "channel" not in jdata.keys():
                    reponse["code"] = 500
                    reponse["error"] = "Channel non précisé."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                try:
                    channel = int(jdata["channel"])
                except:
                    reponse["code"] = 500
                    reponse["error"] = "Channel non valide."
                    c.send(bytes(json.dumps(reponse), 'utf-8'))
                    continue
                server = MumbleServer.servers[jdata["server"]]
                server.moveall(channel)
            else:
                reponse["code"] = 404
                reponse["error"] = "Action non valide."

            message_to_send = json.dumps(reponse).encode("UTF-8")
            c.send(len(message_to_send).to_bytes(2, byteorder='big'))
            c.send(message_to_send)
