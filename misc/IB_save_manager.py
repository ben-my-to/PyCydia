import sys

sys.path.append("..")

from pathlib import Path
from logger import logger
from device_manager import DeviceManager, collapse_path


REMOTE_APP_DIR = Path("/private/var/mobile/Containers/Data/Application")

LOCAL_SAVE_DIR = Path("STORE/")
LOCAL_SAVE_DIR.mkdir(exist_ok=True)

IB_SAVES = (
    "SwordSave.bin",
    "SAVE/SwordSaveSlotX_2.bin",
    "SAVE/SwordSaveX_2-0.bin",
    "SAVE/BackupSlotX_2.bin",
    "SAVE/BackupX_2-0.bin",
    "SAVE/_SwordSaveSlotX_0.bin",
    "SAVE/_SwordSaveX_0-0.bin",
    "SAVE/_BackupSlotX_0.bin",
    "SAVE/_BackupX_0-0.bin",
)

dvm = DeviceManager()
device = dvm.get_device()

swordsave_rel_path = dvm.run(f"find {REMOTE_APP_DIR} -name SwordSave.bin")
REMOTE_SAVE_DIR, REMOTE_SWORDSAVE_DIR, *_ = (
    REMOTE_APP_DIR / swordsave_rel_path
).parents

logger.info(f"Located SwordSave Directory at {REMOTE_SWORDSAVE_DIR}")
logger.info("Restoring IB2 Save Files")

REMOTE_IB2_SAVES = (
    REMOTE_SAVE_DIR / IB_SAVES[1],
    REMOTE_SAVE_DIR / IB_SAVES[2],
)

REMOTE_IB2_BACKUPS = (
    REMOTE_SAVE_DIR / IB_SAVES[3],
    REMOTE_SAVE_DIR / IB_SAVES[4],
)

for backup, save in zip(REMOTE_IB2_BACKUPS, REMOTE_IB2_SAVES):
    dvm.run(f"cp -f {backup} {save}")
    logger.info(f"Copied {collapse_path(backup)} to {collapse_path(save)}")

logger.info("Backing Up Save Files")

sftp = device.open_sftp()
for filename in IB_SAVES:
    local_save = (
        LOCAL_SAVE_DIR / Path(filename).name
    )  # NOTE: store only the files, not any directories
    remote_save = REMOTE_SAVE_DIR / filename
    sftp.get(remote_save.as_posix(), local_save)
    logger.info(f"Copied {collapse_path(remote_save)} to {local_save}")
sftp.close()

dvm.release()
