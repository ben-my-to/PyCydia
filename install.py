import sys
import re
import getpass
import paramiko
import requests
import logging

logging.CHAR_LEVELS = {
    "DEBUG": "*",
    "INFO": "+",
    "WARNING": "!",
    "ERROR": "X",
    "CRITICAL": "X!",
}


class CharFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in logging.CHAR_LEVELS:
            record.levelname = logging.CHAR_LEVELS[levelname]
        return super().format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = CharFormatter("[%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

repos = [
    "https://repo.chariz.com/",
    "https://havoc.app/",
    "https://isecureos.idevicecentral.com/repo/",
    "https://repo.co.kr/",
    "https://sparkdev.me/",
    "https://tigisoftware.com/cydia/",
]

tweaks = [
    "com.rpgfarm.a-font",
    "me.lau.atria",
    "com.muirey03.cr4shed",
    "com.ryannair05.cylinder",
    "com.cydiageek.doubletaptolock",
    "jp.r-plus.deletecut",
    "com.tigisoftware.filza64bit",
    "com.geosn0w.isecureos",
    "co.shoyu.miso",
    "ws.hbang.newterm2",
    "com.spark.snowboard",
    "fuckyou",
    "vim",
]


def connect_ssh(hostname):
    device = paramiko.SSHClient()
    device.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    device.connect(
        hostname,
        username="root",
        password=getpass.getpass(
            prompt=f"root@{hostname}'s password (default is 'alpine'): "
        ),
    )
    return device


def is_valid_url(repo):
    try:
        response = requests.head(repo, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_packages(device):
    sftp = device.open_sftp()

    with sftp.file("/etc/apt/sources.list.d/cydia.list", "r+") as f:
        installed_packages = f.read().decode().splitlines()

        for repo in repos:
            if not is_valid_url(repo):
                logger.error(f"Package '{repo}' doesn't exist or cannot be reached.")

            repo_name = re.search(r"https?://([^/]+)/", repo).group(1)

            if f"deb {repo} ./" not in installed_packages:
                f.write(f"deb {repo} ./\n")
                logger.info(f"Installed package '{repo_name}'.")
            else:
                logger.warning(f"Package '{repo_name}' is already installed.")

    sftp.close()


def get_tweaks(device):
    for tweak in tweaks:
        _, stdout, _ = device.exec_command(f"dpkg -l | grep -qw {tweak}")
        if not stdout.channel.recv_exit_status():
            logger.warning(f"Tweak '{tweak}' is already installed.")
        else:
            _, stdout, stderr = device.exec_command(
                f"apt install -y {tweak} --allow-unauthenticated"
            )
            stdout.channel.recv_exit_status()
            if stderr.channel.recv_exit_status():
                logger.error(f"Unable to locate tweak: '{tweak}'.")
            else:
                logger.info(f"Installed tweak '{tweak}'.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python install.py <hostname>")
        sys.exit(1)

    device = connect_ssh(hostname=sys.argv[1])

    get_packages(device)
    get_tweaks(device)

    logger.info("Restarting SpringBoard")
    device.exec_command("killall SpringBoard")

    device.close()
