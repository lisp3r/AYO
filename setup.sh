#!/bin/bash

# Author: Trevohack
# AYO 2.0 


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'
ITALIC='\e[3m'

AYO_DIR="$(xdg-user-dir DOCUMENTS || echo $HOME)/ayo"

banner() {
    echo -e "${RED}
 ▄▄▄     ▓██   ██▓ ▒█████  
▒████▄    ▒██  ██▒▒██▒  ██▒
▒██  ▀█▄   ▒██ ██░▒██░  ██▒
░██▄▄▄▄██  ░ ▐██▓░▒██   ██░
 ▓█   ▓██▒ ░ ██▒▓░░ ████▓▒░
 ▒▒   ▓▒█░  ██▒▒▒ ░ ▒░▒░▒░ 
  ▒   ▒▒ ░▓██ ░▒░   ░ ▒ ▒░ 
  ░   ▒   ▒ ▒ ░░  ░ ░ ░ ▒  
      ░  ░░ ░         ░ ░  
          ░ ░
${RESET}by ${ITALIC}@Trevohack${RESET}"
}


init() {
    echo -e "[${GREEN}+${RESET}] Configuring Environment..."
    mkdir -p "$AYO_DIR"
    cd "$AYO_DIR"

    # pip install rich
    # pip install python-hosts
}

install() {
    echo -e "[${GREEN}+${RESET}] Downloading AYO..."
    wget -q https://raw.githubusercontent.com/lisp3r/AYO/main/src/main.py -O "$AYO_DIR/main.py" || {
      echo -e "[${RED}-${RESET}] Unable to download main.py, exiting..."; exit 1
    }
    wget -q https://raw.githubusercontent.com/lisp3r/AYO/main/machine_data.json -O "$AYO_DIR/machine_data.json" || {
      echo -e "[${RED}-${RESET}] Unable to download machine_data.json, exiting..."; exit 1
    }
    wget -q https://raw.githubusercontent.com/lisp3r/AYO/main/config.json -O "$AYO_DIR/config.json" || {
      echo -e "[${RED}-${RESET}] Unable to download config.json, exiting..."; exit 1
    }

    echo -e "[${GREEN}+${RESET}] Creating a soft link..."
    sudo ln -s "$AYO_DIR/main.py" "/usr/bin/ayo"
    sudo chmod +x /usr/bin/ayo
}

end() {
    echo -e "[${GREEN}+${RESET}] Happy Hacking!"
    echo -e "\nUsage: ayo -h\n"
}

banner
init
install
end
