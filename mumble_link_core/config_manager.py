import tomllib
import logging


class ConfigManager:
    def __init__(self, config_filename: str):
        with open(config_filename, "rb") as config_file:
            try:
                self.config = tomllib.load(config_file)
            except tomllib.TOMLDecodeError:
                logging.error(f"Can't read config file {config_filename}")
                self.config = {}

    def read(self, section: str, key: str, default=None):
        if section not in self.config:
            return default

        if not isinstance(
                self.config[section],
                dict) or key not in self.config[section]:
            return default

        return self.config[section][key]
