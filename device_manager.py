import paramiko
import getpass
import keyring
from logger import logger


class DeviceManager:
    def __init__(self, *, hostname="192.168.1.33", username="root"):
        self.hostname = hostname
        self.username = username
        self._device = self._connect_ssh()

    @property
    def address(self):
        return f"{self.username}@{self.hostname}"

    def _get_keychain_pass(self):
        try:
            password = keyring.get_password(self.hostname, self.username)
            if password is None:
                raise Exception(f"Keychain password not found for {self.address}")
        except Exception as e:
            logger.warning(e)
            password = getpass.getpass(
                prompt=f"{self.address}'s password (default is 'alpine'): "
            )
        return password

    def _connect_ssh(self):
        device = paramiko.SSHClient()
        device.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        device.connect(
            hostname=self.hostname,
            username=self.username,
            password=self._get_keychain_pass(),
        )
        logger.info(f"Connected to {self.address}")
        return device

    def get_device(self):
        return self._device

    def run(self, command, *, check_out=False, check_errors=False):
        _, stdout, stderr = self._device.exec_command(command)
        stdout.channel.recv_exit_status()
        out = stdout.read().decode().rstrip()
        if check_out:
            return stdout.channel.recv_exit_status()
        if check_errors:
            return stderr.channel.recv_exit_status()
        return out

    def respring(self):
        logger.info("Restarting SpringBoard")
        self.run("killall SpringBoard")

    def release(self):
        self._device.close()
        logger.info(f"Disconnected from {self.address}")


def collapse_path(path):
    src_path = path.parents[-2]
    dst_path = path.name.rstrip()
    return f"{src_path}/.../{dst_path}"
