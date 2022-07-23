# Root level app configurations

import ctypes
import json
import os
import subprocess as sp
import sys
import requests

from pathlib import Path
from typing import Any


DATA_DIR = Path(f"{os.environ['LOCALAPPDATA']}\\MubinLinkEditor")
PYTHON_EXE = os.path.join(sys.prefix, "bin", "python.exe")
CONFIG_FILES = ["actors", "ignore", "nodes", "params"]


def message_box(msg: str, title="Error"):
    ctypes.windll.user32.MessageBoxW(0, msg, title, 0x0 | 0x10)


def load_data(name: str) -> Any:
    return (
        json.loads(f"{DATA_DIR}\\{name}.json")
        if Path(f"{DATA_DIR}\\{name}.json").is_file()
        else None
    )


def set_data(name: str, data=None) -> Any:
    return (
        Path(f"{DATA_DIR}\\{name}.json").write_text(json.dumps(data, indent=4))
        if data
        else None
    )


def is_admin() -> bool:
    temp = Path(f"{os.environ['PROGRAMFILES']}\\temp.admin")
    try:
        temp.write_bytes(b"temp.admin")
        temp.unlink()
        return True
    except:
        return False


def run_configure():

    # Install oead if blender is run as admin (and it's not installed)
    try:
        import oead as _
    except:
        if is_admin():
            sp.run(f"{PYTHON_EXE} -m pip install oead")
        else:
            msg = (
                "Could not install model 'oead', functions of this addon will not work correctly without it.\n"
                + "Please run blender as admin before enabling this addon."
            )
            message_box(msg)
            raise Exception(msg)

    # Create data dir
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    # Download any missing data files (some may not be required)
    for file in CONFIG_FILES:
        path = Path(f"{DATA_DIR}\\{file}.json")
        if not path.is_file():
            path.write_bytes(
                data=requests.get(
                    f"https://raw.githubusercontent.com/ArchLeaders/Mubin-Link-Editor/master/dist/{file}.json"
                ).content
            )


# Initialize the addon
run_configure()
