import os
import sys
from pathlib import Path
from logger import logger
from device_manager import DeviceManager


REMOTE_APP_DIR = Path("/private/var/mobile/Containers/Data/Application")

LOCAL_SAVE_DIR = Path("STORE/")
LOCAL_SAVE_DIR.mkdir(exist_ok=True)

PLIST_NAME = "gameclub.strata.plist"
LOCAL_PLIST_FILE = LOCAL_SAVE_DIR / PLIST_NAME

if len(sys.argv) != 2:
    print("python IB_save_manager.py <hostname>")
    sys.exit(1)


def collapse_file_path(path: Path):
    root_path = path.parents[-2]
    filename = path.name.rstrip()
    return f"{root_path}/.../{filename}"


dvm = DeviceManager(hostname=sys.argv[1])
device = dvm.get_device()

_, stdout, _ = device.exec_command(f"find {REMOTE_APP_DIR} -name {PLIST_NAME}")
plist_rel_path = stdout.read().decode()

REMOTE_PLIST_FILE = REMOTE_APP_DIR / plist_rel_path
logger.info(f"Located gameclub.strata.plist at {REMOTE_PLIST_FILE.as_posix().rstrip()}")

sftp = device.open_sftp()

sftp.get(REMOTE_PLIST_FILE.as_posix().rstrip(), LOCAL_PLIST_FILE)
logger.info(f"Copied {collapse_file_path(REMOTE_PLIST_FILE)} to {LOCAL_PLIST_FILE}")

os.system(f"plutil -replace timedTrialDuration -integer 0 {LOCAL_PLIST_FILE}")
logger.info("Resetted timedTrialDuration=0.")

os.system(f"plutil -replace timedTrialExpired -bool NO {LOCAL_PLIST_FILE}")
logger.info("Resetted timedTrialExpired=NO.")

sftp.put(LOCAL_PLIST_FILE, REMOTE_PLIST_FILE.as_posix().rstrip())
logger.info(f"Copied {LOCAL_PLIST_FILE} to {collapse_file_path(REMOTE_PLIST_FILE)}")

sftp.close()
dvm.release()
