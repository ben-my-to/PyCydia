import sys

sys.path.append("..")

import json
from pathlib import Path
import plistlib
from logger import logger
from device_manager import DeviceManager, collapse_path

dvm = DeviceManager()
device = dvm.get_device()

LOCAL_SAVE_DIR = Path("STORE/")
LOCAL_SAVE_DIR.mkdir(exist_ok=True)

STRATA_PLIST = "gameclub.strata.plist"
LOCAL_STRATA_PLIST = LOCAL_SAVE_DIR / STRATA_PLIST

REMOTE_FILE_PATH = dvm.get_save_path(STRATA_PLIST)
logger.info(f"Located Strata Directory at {REMOTE_FILE_PATH.parents[2]}")

sftp = device.open_sftp()
sftp.get(REMOTE_FILE_PATH.as_posix().rstrip(), LOCAL_STRATA_PLIST)

logger.info(f"Copied {collapse_path(REMOTE_FILE_PATH)} to {LOCAL_STRATA_PLIST}")

with open(LOCAL_STRATA_PLIST, "rb") as f:
    data = plistlib.load(f)

with open("levels.json", "r") as f:
    game = json.load(f)


def level_generator(game):
    for set_num, wave in game.items():
        for wave_num, n_lattices in zip(wave["Waves"], wave["Lattices"]):
            for lattice_num in range(n_lattices):
                yield f"{set_num}_Wave{wave_num}_Lattice{lattice_num}"


for level in level_generator(game):
    if level not in data or data[level] != 3:
        if level not in data:
            logger.info(f"Injecting completed level '{level}'")
        else:
            logger.info(f"Completing level '{level}'")
        data[level] = 3
    else:
        logger.warning(f"'{level}' is already completed")

with open(LOCAL_STRATA_PLIST, "wb") as f:
    plistlib.dump(data, f)

sftp.put(LOCAL_STRATA_PLIST, REMOTE_FILE_PATH.as_posix().rstrip())
logger.info(f"Copied {LOCAL_STRATA_PLIST} to {collapse_path(REMOTE_FILE_PATH)}")

sftp.close()
dvm.release()
