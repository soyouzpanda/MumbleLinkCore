import logging
import Ice
import Murmur
import config_manager


class MumbleManager:
    def __init__(self, config: config_manager.ConfigManager):
        self.config = config

        try:
            self.props = Ice.createProperties()
            self.props.setProperty('Ice.Default.EncodingVersion', '1.0')
            self.idata = Ice.InitializationData()
            self.idata.properties = self.props

            self.communicator = Ice.initialize(self.idata)
            self.base = self.communicator.stringToProxy(
                f"Meta:tcp -h {self.config.read('MURMUR', 'ip', '127.0.0.1')} -p {self.config.read('MURMUR', 'port', '6502')}")

            self.meta = Murmur.MetaPrx.checkedCast(self.base)
        except Ice.Exception:
            logging.critical("Cannot open connection with Murmur server")
            self.close()
            raise RuntimeError

    def clear(self):
        servers = self.meta.getAllServers()
        for currentServer in servers:
            if currentServer.isRunning():
                currentServer.stop()
            currentServer.delete()

    def close(self):
        self.communicator.destroy()
