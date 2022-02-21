import os
import subprocess
import sys
import requests

from pathlib import Path

def init():
    """Initialize setup"""

    # install oead
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    subprocess.call([python_exe, "-m", "pip", "install", "oead"])

    # make data dir
    path = Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_link_editor')
    if not path.is_dir():
        path.mkdir()

    # download & extract required data files
    files = [ 'actors', 'ignore', 'nodes', 'params' ]
    for file in files:
        data = requests.get(f'https://raw.githubusercontent.com/ArchLeaders/Mubin-Link-Editor/master/dist/{file}.json')
        Path(path, f'{file}.json').write_bytes(data.content)