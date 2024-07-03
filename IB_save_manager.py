import sys
from pathlib import Path
from logger import logger
from device_manager import DeviceManager


REMOTE_APP_DIR = Path("/private/var/mobile/Containers/Data/Application")

LOCAL_SAVE_DIR = Path("STORE/")
LOCAL_SAVE_DIR.mkdir(exist_ok=True)

IB_SAVE_FILES = (
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

if len(sys.argv) != 2:
    print("python IB_save_manager.py <hostname>")
    sys.exit(1)


def collapse_file_path(path: Path):
    root_path = path.parents[-2]
    filename = path.name.rstrip()
    return f"{root_path}/.../{filename}"


dvm = DeviceManager(hostname=sys.argv[1])
device = dvm.get_device()

_, stdout, _ = device.exec_command(f"find {REMOTE_APP_DIR} -name SwordSave.bin")
save_rel_path = stdout.read().decode()

REMOTE_SAVE_DIR = (REMOTE_APP_DIR / save_rel_path).parents[0]
logger.info(f"Located IB Save Directory at {REMOTE_SAVE_DIR}")

logger.info("Replacing IB2 Save Files")

REMOTE_IB2_SAVE_FILES = (
    REMOTE_SAVE_DIR / IB_SAVE_FILES[1],
    REMOTE_SAVE_DIR / IB_SAVE_FILES[2],
)

REMOTE_IB2_BACKUP_SAVES = (
    REMOTE_SAVE_DIR / IB_SAVE_FILES[3],
    REMOTE_SAVE_DIR / IB_SAVE_FILES[4],
)

for backup, save in zip(REMOTE_IB2_BACKUP_SAVES, REMOTE_IB2_SAVE_FILES):
    device.exec_command(f"cp -f {backup} {save}")
    logger.info(f"Copied {collapse_file_path(backup)} to {collapse_file_path(save)}")

logger.info("Backing Up Save Files")

sftp = device.open_sftp()
for filename in IB_SAVE_FILES:
    local_save_file = (
        LOCAL_SAVE_DIR / Path(filename).name
    )  # NOTE: store only the files, not any directories
    remote_save_file = REMOTE_SAVE_DIR / filename
    sftp.get(remote_save_file.as_posix(), local_save_file)
    logger.info(f"Copied {collapse_file_path(remote_save_file)} to {local_save_file}")
sftp.close()

dvm.release()
