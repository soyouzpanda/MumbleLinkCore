from MumbleServer import MumbleServer
from configManager import configManager
from mumbleManager import MumbleManager
from socketManager import SocketManager
from utils import Utils
from webManager import WebManager

print("""
.___  ___.  __    __  .___  ___. .______    __       _______  __       __  .__   __.  __  ___ 
|   \/   | |  |  |  | |   \/   | |   _  \  |  |     |   ____||  |     |  | |  \ |  | |  |/  / 
|  \  /  | |  |  |  | |  \  /  | |  |_)  | |  |     |  |__   |  |     |  | |   \|  | |  '  /  
|  |\/|  | |  |  |  | |  |\/|  | |   _  <  |  |     |   __|  |  |     |  | |  . `  | |    <   
|  |  |  | |  `--'  | |  |  |  | |  |_)  | |  `----.|  |____ |  `----.|  | |  |\   | |  .  \  
|__|  |__|  \______/  |__|  |__| |______/  |_______||_______||_______||__| |__| \__| |__|\__\ 
                                                                    Par Eliott Bovel      
                                                                                                                                                 
""")

print("Load configuration.")
configManager.load()
print("Configuration loaded !")

print("load Mumble Manager.")
Utils.mumbleManager = MumbleManager()
print("load Mumble Manager loaded and ICE connection successful!")

print("Delete all mumble servers.")
Utils.mumbleManager.clear()

print("start socket server on port : " + configManager.read("SOCKET", "port", "751"))
socket = SocketManager()
print("Socket started successful!")

print("Load web server on port : " + configManager.read("WEB", "port", "80"))
web = WebManager()
print("Web started successful!")

socket.join()
print("Close ICE connection.")
Utils.close()
