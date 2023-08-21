import logging
import pathlib

import Ice

import argparse


def close(err: int):
    if mmanager is not None:
        mmanager.close()
    exit(err)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Mumble Link Core')
    parser.add_argument('-i', '--ice', type=pathlib.Path, default='Murmur.ice')
    parser.add_argument(
        '-c',
        '--config',
        type=pathlib.Path,
        default='config.toml')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            format='[%(levelname)s] [%(asctime)s] %(message)s',
            level=logging.DEBUG)
    else:
        logging.basicConfig(
            format='[%(levelname)s] [%(asctime)s] %(message)s',
            level=logging.INFO)

    print("""
    .___  ___.  __    __  .___  ___. .______    __       _______  __       __  .__   __.  __  ___
    |   \\/   | |  |  |  | |   \\/   | |   _  \\  |  |     |   ____||  |     |  | |  \\ |  | |  |/  /
    |  \\  /  | |  |  |  | |  \\  /  | |  |_)  | |  |     |  |__   |  |     |  | |   \\|  | |  '  /
    |  |\\/|  | |  |  |  | |  |\\/|  | |   _  <  |  |     |   __|  |  |     |  | |  . `  | |    <
    |  |  |  | |  `--'  | |  |  |  | |  |_)  | |  `----.|  |____ |  `----.|  | |  |\\   | |  .  \
    |__|  |__|  \\______/  |__|  |__| |______/  |_______||_______||_______||__| |__| \\__| |__|\\__\
                                                                        Par Eliott Bovel

    """)

    try:
        Ice.loadSlice(str(args.ice), ['-I' + Ice.getSliceDir()])
    except RuntimeError:
        logging.critical(f"Cannot load slice {args.ice}")
        close(1)

    import config_manager
    import mumble_manager
    import socket_manager
    import web_manager

    logging.debug(f"Loading configuration from {args.config}...")
    config = config_manager.ConfigManager(args.config)
    logging.debug(f"Loaded configuration from {args.config}")

    logging.debug(f"Loading Mumble manager...")
    try:
        mmanager = mumble_manager.MumbleManager(config)
    except RuntimeError:
        close(1)
    logging.debug(f"Loaded Mumble manager")
    logging.debug(f"Deleting all Mumble servers")
    mmanager.clear()

    logging.info(
        f"Listening socket on port {config.read('SOCKET', 'port', 751)}")
    try:
        socket = socket_manager.SocketManager(config, mmanager)
    except RuntimeError:
        close(1)

    logging.info(f"Listening web on port {config.read('WEB', 'port', 80)}")
    try:
        web = web_manager.WebManager(config)
    except RuntimeError:
        close(1)

    socket.join()
    close(0)
