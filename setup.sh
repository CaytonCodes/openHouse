#!/usr/bin/env bash

start () {
  echo "############################################"
  echo "#Automated installer for open house project#"
  echo "############################################"
  echo ""
}

# takes msg ($1) and status ($2) as args
end () {
  echo ""
  echo "############################################"
  echo "# Finished the setup script"
  echo "# Message: $1"
  echo "############################################"
  exit "$2"
}

# takes message ($1) and level ($2) as args
message () {
  echo "[OpenGrow] [$2] $1"
}

# takes package name ($1) and error warning ($2).
install_package() {
  message "Installing $1" "INFO"
  if ! pip install $1; then
    message "Unable to install pkg $1. $2" "WARNING"
  fi
}

# takes a package name ($1), success message ($2), and error message ($3) as args.
check_pkg_install() {
  message "Checking if package $1 is installed" "INFO"
  if dpkg -l "$1" > /dev/null 2>&1; then
    message "Package $1 is not installed. $3" "WARNING"
    return 0;
  else
    message "Package $1 is installed. $2" "INFO"
    return 1;
  fi
}

# takes a package name ($1), success message ($2), and error message ($3) as args.
standard_package() {
  install_package "$1" "$3"
  check_pkg_install "$1" "$2" "$3"
}

############
# Main logic
start

# check again if user is root in case user is calling this script directly
if [[ "$(id -u)" -ne 0 ]]; then message "User is not root." 'ERROR'; end 'Re-run as root or append sudo.' 1; fi

trap "end 'Received a signal to stop.' 1" INT HUP TERM

### perform the installation
message 'Installing dependencies...' 'TOP'; # pip install PyYAML
standard_package 'PyYAML' 'Done installing PyYAML.' 'Unable to install PyYAML.'
standard_package 'pytz' 'Done installing pytz.' 'Unable to install pytz.'
standard_package 'smbus2' 'Done installing smbus2.' 'Unable to install smbus2.'

echo "#################################################################"
echo "# All finished! Press any key to REBOOT now or Ctrl+c to abort. #"
echo "#################################################################"

read -n1 -s; reboot now