# PyCydia

A Simple Cydia Package+Tweak Installer in Python.

## Prerequisites
  - A computer with some terminal application (ex: Microsoft PowerShell).
  - A jailbroken _(rootful)_ device.

## Listed Tweaks
  - A-Font (Merona)
  - Atria (Chariz)
  - Cr4shed (Havoc)
  - Cylinder Reborn (Chariz)
  - DoubleTapToLock (BigBoss)
  - DeleteCut (BigBoss)
  - Filza File Manager 64-bit (TIGI Software)
  - iSecureOS (GeoSn0w)
  - Miso Theme (Havoc)
  - NewTerm 2 (Chariz)
  - SnowBoard (SparkDev)
  - Vim (apt.bingner.com)

## How to Install:
  1. Open Cydia and install OpenSSH _(apt.bingner.com)_.
  2. Clone the repository: `git clone https://github.com/ben-my-to/PyCydia.git && cd PyCydia/`.
  3. Install the requirements in your virtual environment: `pip install -r requirements.txt`.
  4. Run the python script: `python install.py`.
     - Your device IP address can be found in: Settings -> Wi-Fi -> (i) -> IP Address.
     - The default password is `alpine`.
     - _(Optional)_ You should change the default password using the command `passwd`.

## Disclaimer
  - This installer was tested on an iPhone 7 device running iOS 14.6.
  - I highly recommend consulting a compatibility list of the tweak(s) you would like to install as I don't know what device+iOS you are running.

## Author
Jason Duong
