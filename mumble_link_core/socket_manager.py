import json
import logging
import socket
import threading
import mumble_server
import mumble_manager
import config_manager


class SocketManager:
    def __init__(self, config: config_manager.ConfigManager,
                 mmanager: mumble_manager.MumbleManager):
        self.config = config
        self.mmanager = mmanager
        try:
            self.ip = self.config.read("SOCKET", "ip", "127.0.0.1")
            self.port = self.config.read("SOCKET", "port", 751)
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.ip, self.port))
            self.server.listen(512)
        except socket.error:
            logging.critical(f"Cannot bind socket on {self.ip}:{self.port}")
            raise RuntimeError

        try:
            self.thread = threading.Thread(
                target=SocketManager.thread, args=(self,))
            self.thread.start()
        except RuntimeError:
            logging.error("Error while listening socket")
            raise RuntimeError

    def join(self):
        self.thread.join()

    def thread(self):
        while True:
            c, addr = self.server.accept()
            length_of_message = int.from_bytes(c.recv(2), byteorder='big')
            data = c.recv(length_of_message)
            if not data:
                continue

            response = {
                "code": 200
            }
            try:
                jdata = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                logging.warning(
                    f"Error during decode request from {addr[0]}:{addr[1]}")
                response["code"] = 500
                response["error"] = "Error during decode request."
                c.send(bytes(json.dumps(response), 'utf-8'))
                continue

            if str(
                self.config.read(
                    "AUTH",
                    "api-key",
                    "CHANGEMETOO")) == "CHANGEMETOO" or "api-key" not in jdata.keys() or str(
                jdata["api-key"]) != str(
                self.config.read(
                    "AUTH",
                    "api-key",
                    "CHANGEMETOO")):
                response["code"] = 403
                response["error"] = "Erreur d'Authentification."
                logging.warning(
                    f"Socket authentication failed from {addr[0]}:{addr[1]}")
                c.send(bytes(json.dumps(response), 'utf-8'))
                continue

            if "action" not in jdata.keys():
                response["code"] = 500
                response["error"] = "Aucune action précisée."
                c.send(bytes(json.dumps(response), 'utf-8'))
                continue

            if "server" not in jdata.keys() and jdata["action"] != "create":
                response["code"] = 500
                response["error"] = "Aucun serveur précisé."
                c.send(bytes(json.dumps(response), 'utf-8'))
                continue

            if "server" in jdata.keys() and jdata["action"] != "create" and jdata[
                    "server"] not in mumble_server.MumbleServer.servers.keys():
                response["code"] = 500
                response["error"] = "Serveur inexistant."
                c.send(bytes(json.dumps(response), 'utf-8'))
                continue
            if jdata["action"] == "create":
                server = mumble_server.MumbleServer(self.mmanager.meta, self.config)
                uuid = server.id
                if "title" in jdata.keys():
                    server.set_title(str(jdata["title"]))
                response["id"] = uuid
            elif jdata["action"] == "check-server":
                response["message"] = "Ce serveur existe bien."
            elif jdata["action"] == "delete":
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                server.delete()
            elif jdata["action"] == "create-user":
                if "username" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                if username in server.users_by_name.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur déjà existant."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue

                uuid = server.create_user(username)
                response["id"] = uuid
            elif jdata["action"] == "mute":
                if "username" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                server.mute(username)
            elif jdata["action"] == "unmute":
                if "username" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                server.unmute(username)
            elif jdata["action"] == "mute-all":
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                server.mute_all()
            elif jdata["action"] == "unmute-all":
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                server.unmute_all()
            elif jdata["action"] == "set-admin-perms":
                if "username" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                server.set_user_admin(username)
            elif jdata["action"] == "set-player-perms":
                if "username" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                server.set_user_player(username)
            elif jdata["action"] == "get-user-info":
                if "username" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                username = str(jdata["username"])
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                response["data"] = server.get_user_info(username)
            elif jdata["action"] == "get-users-info":
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                response["data"] = server.get_users_info()
            elif jdata["action"] == "move":
                if "username" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                if "channel" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Channel non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                username = str(jdata["username"])
                try:
                    channel = int(jdata["channel"])
                except ValueError:
                    response["code"] = 500
                    response["error"] = "Channel non valide."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                if username not in server.users.keys():
                    response["code"] = 500
                    response["error"] = "Nom d'utilisateur inexistant."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                server.move(username, channel)
            elif jdata["action"] == "move-all":
                if "channel" not in jdata.keys():
                    response["code"] = 500
                    response["error"] = "Channel non précisé."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                try:
                    channel = int(jdata["channel"])
                except ValueError:
                    response["code"] = 500
                    response["error"] = "Channel non valide."
                    c.send(bytes(json.dumps(response), 'utf-8'))
                    continue
                server = mumble_server.MumbleServer.servers[jdata["server"]]
                server.move_all(channel)
            else:
                response["code"] = 404
                response["error"] = "Action non valide."

            message_to_send = json.dumps(response).encode("UTF-8")
            c.send(len(message_to_send).to_bytes(2, byteorder='big'))
            c.send(message_to_send)
