import logging
import socketserver
import threading
import functools

from mumble_server import MumbleServer
import config_manager
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse


class WebManager:
    def __init__(self, config: config_manager.ConfigManager):
        self.config = config
        try:
            self.thread = threading.Thread(
                target=WebManager.thread, args=(self, ))
            self.thread.start()
        except RuntimeError:
            logging.critical("Error during web listening")
            raise RuntimeError

    def join(self):
        self.thread.join()

    def thread(self):
        host = self.config.read("WEB", "ip", "127.0.0.1")
        port = self.config.read("WEB", "port", 80)
        handler = functools.partial(WebManager.Handler, self.config)
        server = HTTPServer((host, port), handler)
        server.serve_forever()

    class Handler(BaseHTTPRequestHandler):
        def __init__(self,
                     config: config_manager.ConfigManager,
                     request: bytes,
                     client_address: tuple[str, int],
                     server: socketserver.BaseServer):
            self.config = config

            super().__init__(request, client_address, server)

        def log_message(self, format, *args):
            logging.info(
                f"Web connection from {self.address_string()}, request: {self.path}")

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
                    data = {
                        'ip': self.config.read(
                            "MUMBLE",
                            "public_ip",
                            "127.0.0.1"),
                        'port': srv.port,
                        'username': usr["username"],
                        'password': usr["password"]}
                self.wfile.write(json.dumps(data).encode())
            elif self.path.startswith('/text'):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()

                if error:
                    text = "error"
                else:
                    text = f"mumble://{usr['username']}:{usr['password']}@{self.config.read('MUMBLE', 'public_ip', '127.0.0.1')}:{srv.port}/"

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
                        html_content = html_content.replace(
                            '{ip}', self.config.read(
                                "MUMBLE", "public_ip", "127.0.0.1")) .replace(
                            '{port}', str(
                                srv.port)) .replace(
                            '{username}', usr["username"]) .replace(
                            '{password}', usr["password"]) .replace(
                            '{link}', f"mumble://{usr['username']}:{usr['password']}@{self.config.read('MUMBLE', 'public_ip', '127.0.0.1')}:{str(srv.port)}/")
                    self.wfile.write(html_content.encode())
