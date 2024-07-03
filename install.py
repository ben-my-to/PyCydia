import sys
import re
import requests
from logger import logger
from device_manager import DeviceManager


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
    "vim",
]


def is_valid_package(repo):
    try:
        response = requests.head(repo, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def install_packages(device):
    logger.info("Installing Packages")
    sftp = device.open_sftp()

    with sftp.file("/etc/apt/sources.list.d/cydia.list", "r+") as f:
        installed_packages = f.read().decode().splitlines()

        for repo in repos:
            if not is_valid_package(repo):
                logger.error(f"Package '{repo}' doesn't exist or cannot be reached.")
            else:
                repo_name = re.search(r"https?://([^/]+)/", repo).group(1)
                if f"deb {repo} ./" not in installed_packages:
                    f.write(f"deb {repo} ./\n")
                    logger.info(f"Installing package '{repo_name}'.")
                else:
                    logger.warning(f"Package '{repo_name}' is already installed.")
    sftp.close()


def update_packages(device):
    logger.info("Updating Packages")
    device.exec_command("apt update")


def install_tweaks(device):
    logger.info("Installing Tweaks")

    def get_tweak_name(tweak):
        _, stdout, _ = device.exec_command(f"dpkg -s {tweak} | sed -n 's/^Name: //p'")
        return stdout.read().decode().strip()

    for tweak in tweaks:
        _, stdout, _ = device.exec_command(f"dpkg -l | grep -qw {tweak}")
        if not stdout.channel.recv_exit_status():
            logger.warning(f"Tweak '{get_tweak_name(tweak)}' is already installed.")
        else:
            _, stdout, stderr = device.exec_command(
                f"apt install -y {tweak} --allow-unauthenticated"
            )
            stdout.channel.recv_exit_status()
            if stderr.channel.recv_exit_status():
                logger.error(f"Unable to locate tweak: '{tweak}'.")
            else:
                logger.info(f"Installing tweak '{get_tweak_name(tweak)}'.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python install.py <hostname>")
        sys.exit(1)

    dvm = DeviceManager(hostname=sys.argv[1])
    device = dvm.get_device()

    install_packages(device)
    update_packages(device)
    install_tweaks(device)

    dvm.respring()
    dvm.release()
