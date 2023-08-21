import threading

from MumbleServer import MumbleServer
from configManager import configManager
from utils import Utils
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse


class WebManager:
    def __init__(self):

        try:
            self.print_lock = threading.Lock()
            self.thread = threading.Thread(target=WebManager.thread, args=(self, ))
            self.thread.start()
        except:
            print("Error during web listening.")
            Utils.close()

    def join(self):
        self.thread.join()
    def thread(self):
        host = configManager.read("WEB", "ip", "127.0.0.1")
        port = int(configManager.read("WEB", "port", "80"))
        server = HTTPServer((host, port), WebManager.Handler)
        server.serve_forever()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            print("> Web connection from " + self.address_string() + ", request: " + self.path)

        def do_GET(self):
            url_parts = urlparse(self.path)
            query = parse_qs(url_parts.query)
            server = query.get('server', [''])[0]
            user = query.get('user', [''])[0]
            error = False
            srv = None
            usr = None
            if server not in MumbleServer.servers.keys():
                error = True
            else:
                srv = MumbleServer.servers[server]
            if not error and user not in srv.users.keys():
                error = True
            elif not error:
                usr = srv.users[user]

            if self.path.startswith('/json'):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                if error:
                    data = {"error": True}
                else:
                    data = {'ip': configManager.read("MUMBLE", "public_ip", "127.0.0.1"), 'port': srv.port, 'username': usr["username"], 'password': usr["password"]}
                self.wfile.write(json.dumps(data).encode())
            elif self.path.startswith('/text'):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()

                if error:
                    text = "error"
                else:
                    text = "mumble://" + usr["username"] + ":" + usr["password"] + "@" + configManager.read("MUMBLE", "public_ip", "127.0.0.1") + ":" + str(srv.port) + "/"

                self.wfile.write(text.encode())
            else:

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                link = 'web/index.html'
                if error:
                    link = 'web/error.html'

                with open(link, 'r') as file:
                    html_content = file.read()
                    if not error:
                        html_content = html_content.replace('{ip}', configManager.read("MUMBLE", "public_ip", "127.0.0.1")).replace('{port}', str(srv.port)).replace('{username}', usr["username"]).replace('{password}', usr["password"]).replace('{link}', "mumble://" + usr["username"] + ":" + usr["password"] + "@" + configManager.read("MUMBLE", "public_ip", "127.0.0.1") + ":" + str(srv.port) + "/")
                    self.wfile.write(html_content.encode())
