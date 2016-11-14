import argparse
import ConfigParser
import os


def compute_config(config_path, section):
    class Foo:
        def __init__(self):
            pass
    config = ConfigParser.ConfigParser()
    config_path = os.path.abspath(config_path)
    config.read(config_path)
    class_ = Foo()
    for item in config.items(section):
        setattr(class_, item[0], item[1])
    return class_


def parse_arguments():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "-c", "--config",
        help="path to the config file",
        default=os.path.join(
            "\\".join(os.path.abspath(__file__).split("\\")[:-1]),
            "server.cfg"
        )
    )
    return arg_parser


