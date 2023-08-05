import configparser

from utils import Utils


class configManager:
    config = None

    @classmethod
    def load(cls):
        cls.config = configparser.ConfigParser()
        cls.config.read("config.ini")

    @classmethod
    def close(cls):
        cls.config.close()

    @classmethod
    def read(cls, section, key, default=None):
        if cls.config is None:
            print("Error: no config loaded.")
            Utils.close()
        try:
            return cls.config.get(section, key)
        except:
            return default


