import datetime
import pathlib

import typer
import yaml
from rich import print, print_json

from artifactdb.client.excavator import Excavator


class MissingArgument(Exception): pass


def get_client(url, *args, **kwargs):
    return Excavator(url,*args,**kwargs)


def get_config_directory():
    return typer.get_app_dir("artifactdb-cli")

def get_config_path():
    cfg_folder = get_config_directory()
    cfg_file = "config"  # TODO: we could have multiple config files
    cfg_path = pathlib.Path(cfg_folder,cfg_file)

    return cfg_path

def load_config():
    cfg_path = get_config_path()
    try:
        cfg = yaml.safe_load(open(cfg_path))
    except  FileNotFoundError:
        print(f"No existing configuration file found at '{cfg_path}', creating one")
        cfg = {"contexts": [],"last-modification": datetime.datetime.now().isoformat()}
        cfg_path.parent.mkdir(parents=True,exist_ok=True)
        yaml.dump(cfg,open(cfg_path,"w"))

    return cfg


def save_config(cfg):
    cfg_path = get_config_path()
    yaml.dump(cfg,open(cfg_path,"w"))
