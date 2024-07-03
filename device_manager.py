import paramiko
import getpass
from logger import logger


class DeviceManager:
    def __init__(self, *, hostname, username="root"):
        self.hostname = hostname
        self.username = username
        self._device = self._connect_ssh()

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

    @property
    def address(self):
        return f"{self.username}@{self.hostname}"

    def get_device(self):
        return self._device

    def respring(self):
        logger.info("Restarting SpringBoard")
        self._device.exec_command("killall SpringBoard")

    def release(self):
        logger.info(f"Disconnected from {self.address}")
        self._device.close()
