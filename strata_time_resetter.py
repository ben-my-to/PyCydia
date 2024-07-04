import os
import sys
from pathlib import Path
from logger import logger
from device_manager import DeviceManager, collapse_path


REMOTE_APP_DIR = Path("/private/var/mobile/Containers/Data/Application")

LOCAL_SAVE_DIR = Path("STORE/")
LOCAL_SAVE_DIR.mkdir(exist_ok=True)

STRATA_PLIST = "gameclub.strata.plist"
LOCAL_STRATA_PLIST = LOCAL_SAVE_DIR / STRATA_PLIST

if len(sys.argv) != 2:
    print("python strata_time_resetter.py <hostname>")
    sys.exit(1)


dvm = DeviceManager(hostname=sys.argv[1])
device = dvm.get_device()

_, stdout, _ = device.exec_command(f"find {REMOTE_APP_DIR} -name {STRATA_PLIST}")
plist_rel_path = stdout.read().decode()

REMOTE_PLIST_FILE = REMOTE_APP_DIR / plist_rel_path
logger.info(f"Located Strata Directory at {REMOTE_PLIST_FILE.parents[2]}")

sftp = device.open_sftp()

sftp.get(REMOTE_PLIST_FILE.as_posix().rstrip(), LOCAL_STRATA_PLIST)
logger.info(f"Copied {collapse_path(REMOTE_PLIST_FILE)} to {LOCAL_STRATA_PLIST}")

os.system(f"plutil -replace timedTrialDuration -integer 0 {LOCAL_STRATA_PLIST}")
logger.info("Set timedTrialDuration=0")

os.system(f"plutil -replace timedTrialExpired -bool NO {LOCAL_STRATA_PLIST}")
logger.info("Set timedTrialExpired=NO")

sftp.put(LOCAL_STRATA_PLIST, REMOTE_PLIST_FILE.as_posix().rstrip())
logger.info(f"Copied {LOCAL_STRATA_PLIST} to {collapse_path(REMOTE_PLIST_FILE)}")

sftp.close()
dvm.release()
