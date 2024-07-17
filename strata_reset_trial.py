import sys

sys.path.append("..")

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

data["timedTrialDuration"] = 0
logger.info("Set timedTrialDuration=0")

data["timedTrialExpired"] = False
logger.info("Set timedTrialExpired=NO")

with open(LOCAL_STRATA_PLIST, "wb") as f:
    plistlib.dump(data, f)

sftp.put(LOCAL_STRATA_PLIST, REMOTE_FILE_PATH.as_posix().rstrip())
logger.info(f"Copied {LOCAL_STRATA_PLIST} to {collapse_path(REMOTE_FILE_PATH)}")

sftp.close()
dvm.release()