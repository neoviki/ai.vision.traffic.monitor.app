#!/bin/bash

: '
    Linux Application Installation Utility

    Author	: 	Viki [ V Natarajan ]
	Contact	:	https://viki.design
    Licence :   MIT
'

#PIP Requirements
pip install ultralytics opencv-python pillow numpy

INSTALL_DIR="/usr/bin"

get_installation_directory() {
    local system_name
    system_name=$(uname -s)

    if [[ "$system_name" == "Linux" ]]; then
        INSTALL_DIR="/usr/local/bin"
    elif [[ "$system_name" == "Darwin" ]]; then
        INSTALL_DIR="/usr/local/bin"
    else
        INSTALL_DIR="/usr/bin"
    fi
}

install_util() {
    local util="$1"
    echo "[ status   ] Installing $util to $INSTALL_DIR"

    if [ ! -f "./$util" ]; then
        echo "[ failure  ] $util not found!"
        INSTALL_STATUS["$util"]="FAILED"
        return 1
    fi

    chmod +x "./$util"

    if command -v sudo &> /dev/null; then
        sudo cp "./$util" "$INSTALL_DIR/"
    else
        cp "./$util" "$INSTALL_DIR/"
    fi

    if [ $? -eq 0 ]; then
        echo "[ success  ] $util installed successfully"
        INSTALL_STATUS["$util"]="SUCCESS"
    else
        echo "[ failure  ] Failed to install $util. You may need sudo/root permissions."
        INSTALL_STATUS["$util"]="FAILED"
    fi
}

# Determine config file
CONFIG_FILE="${1:-installation.config}"

# Check if the config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "[ error    ] Config file '$CONFIG_FILE' not found!"
    exit 1
fi

# Read utilities from the config file
mapfile -t UTILS < "$CONFIG_FILE"

declare -A INSTALL_STATUS

# INSTALLATION
get_installation_directory

for util in "${UTILS[@]}"; do
    install_util "$util"
done

# SUMMARY
echo
echo "==================== INSTALLATION SUMMARY ===================="
for util in "${UTILS[@]}"; do
    status=${INSTALL_STATUS[$util]:-"NOT ATTEMPTED"}
    printf " %-35s : %s\n" "$util" "$status"
done
echo "=============================================================="
echo

