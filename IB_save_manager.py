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

dvm = DeviceManager(hostname=sys.argv[1])
device = dvm.get_device()

_, stdout, _ = device.exec_command(f"find {REMOTE_APP_DIR} -name SwordSave.bin")
save_rel_path = stdout.read().decode()

REMOTE_SAVE_DIR = (REMOTE_APP_DIR / save_rel_path).parents[0]

sftp = device.open_sftp()
for filename in IB_SAVE_FILES:
    local_save_file = LOCAL_SAVE_DIR / Path(filename).name
    remote_save_file = (REMOTE_SAVE_DIR / filename).as_posix()
    sftp.get(remote_save_file, local_save_file)
    logger.info(f"Saved {remote_save_file} to {local_save_file}")
sftp.close()

dvm.release()
