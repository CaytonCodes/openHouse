#!/usr/bin/env sh

# check if user root
if [ "$(id -u)" != "0" ]; then echo "Please re-run as sudo."; exit 1; fi

# execute the installation script using interpreter in the shebang
./interface/lcd/setup.sh
./setup.sh

exit 0