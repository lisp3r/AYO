#!/bin/bash



RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m' 


banner() {
    echo -e """
$RED 

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

$RESET
    """
}

init() {
    echo -e "[$GREEN+$RESET] Configuring Environment..."
    mkdir ~/Documents/ayo
    cd ~/Documents/ayo 
}

install() {
    echo -e "[$GREEN+$RESET] Downloading AYO..."
    wget https://raw.githubusercontent.com/Trevohack/AYO/main/src/main.py -O ~/Documents/ayo/main.py 
    wget https://raw.githubusercontent.com/Trevohack/AYO/main/src/machine_data.json -O ~/Documents/ayo/machine_data.json

    sudo ~/Documents/ayo/main.py /usr/bin/ayo 
    sudo chmod +x /usr/bin/ayo 
}

end() {
    echo -e "[$GREEN+$RESET] Happy Hacking!" 
}

banner 
init
install 