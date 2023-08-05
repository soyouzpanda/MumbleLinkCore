import Ice

from configManager import configManager
from utils import Utils


class MumbleManager:

    murmur = None

    def __init__(self):
        try:
            Ice.loadSlice('', ['-I' + Ice.getSliceDir(), configManager.read("MURMUR", "ice_file", "Murmur.ice")])
            import Murmur
            MumbleManager.murmur = Murmur
        except:
            print("Error during loading ICE slice.")
            Utils.close()

        try:
            self.props = Ice.createProperties()
            self.props.setProperty('Ice.Default.EncodingVersion', '1.0')
            self.idata = Ice.InitializationData()
            self.idata.properties = self.props

            self.communicator = Ice.initialize(self.idata)
            self.base = self.communicator.stringToProxy("Meta:tcp -h " + configManager.read("MURMUR", "ip", "127.0.0.1") + " -p " + configManager.read("MURMUR", "port", "6502"))

            self.meta = Murmur.MetaPrx.checkedCast(self.base)
        except:
            print("Error during ICE connection.")
            self.close()
            Utils.close()

    def clear(self):
        servers = self.meta.getAllServers()
        for currentServer in servers:
            if currentServer.isRunning():
                currentServer.stop()
            currentServer.delete()

    def close(self):
        self.communicator.destroy()

