import sys

sys.path.append("..")

import json
from pathlib import Path
import plistlib
from logger import logger
from device_manager import DeviceManager, collapse_path


REMOTE_APP_DIR = Path("/private/var/mobile/Containers/Data/Application")

LOCAL_SAVE_DIR = Path("STORE/")
LOCAL_SAVE_DIR.mkdir(exist_ok=True)

STRATA_PLIST = "gameclub.strata.plist"
LOCAL_STRATA_PLIST = LOCAL_SAVE_DIR / STRATA_PLIST

dvm = DeviceManager()
device = dvm.get_device()

plist_rel_path = dvm.run(f"find {REMOTE_APP_DIR} -name {STRATA_PLIST}")
REMOTE_PLIST_FILE = REMOTE_APP_DIR / plist_rel_path

logger.info(f"Located Strata Directory at {REMOTE_PLIST_FILE.parents[2]}")

sftp = device.open_sftp()
sftp.get(REMOTE_PLIST_FILE.as_posix().rstrip(), LOCAL_STRATA_PLIST)

logger.info(f"Copied {collapse_path(REMOTE_PLIST_FILE)} to {LOCAL_STRATA_PLIST}")

with open(LOCAL_STRATA_PLIST, "rb") as f:
    data = plistlib.load(f)

with open("levels.json", "r") as f:
    game = json.load(f)


def level_generator(game):
    for set_num, waves in game.items():
        for levels in waves:
            wave_num = levels["Wave"]
            for lattice_num in range(levels["Lattices"]):
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

sftp.put(LOCAL_STRATA_PLIST, REMOTE_PLIST_FILE.as_posix().rstrip())
logger.info(f"Copied {LOCAL_STRATA_PLIST} to {collapse_path(REMOTE_PLIST_FILE)}")

sftp.close()
dvm.release()
