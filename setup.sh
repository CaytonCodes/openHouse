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
  echo "[LCD] [$2] $1"
}

############
# Main logic
start

# check again if user is root in case user is calling this script directly
if [[ "$(id -u)" -ne 0 ]]; then message "User is not root." 'ERROR'; end 'Re-run as root or append sudo.' 1; fi

trap "end 'Received a signal to stop.' 1" INT HUP TERM

### perform the installation
message 'Installing dependencies...' 'YAML'; pip install PyYAML

echo "#################################################################"
echo "# All finished! Press any key to REBOOT now or Ctrl+c to abort. #"
echo "#################################################################"

read -n1 -s; reboot now