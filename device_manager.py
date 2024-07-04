import paramiko
import getpass
from logger import logger


class DeviceManager:
    def __init__(self, *, hostname, username="root"):
        self.hostname = hostname
        self.username = username
        self._device = self._connect_ssh()

    @property
    def address(self):
        return f"{self.username}@{self.hostname}"

    def _connect_ssh(self):
        device = paramiko.SSHClient()
        device.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        device.connect(
            hostname=self.hostname,
            username=self.username,
            password=getpass.getpass(
                prompt=f"{self.address}'s password (default is 'alpine'): "
            ),
        )
        logger.info(f"Connected to {self.address}")
        return device

    def get_device(self):
        return self._device

    def respring(self):
        logger.info("Restarting SpringBoard")
        self._device.exec_command("killall SpringBoard")

    def release(self):
        self._device.close()
        logger.info(f"Disconnected from {self.address}")


def collapse_path(path):
    src_path = path.parents[-2]
    dst_path = path.name.rstrip()
    return f"{src_path}/.../{dst_path}"
