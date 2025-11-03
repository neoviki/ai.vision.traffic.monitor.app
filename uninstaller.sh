#!/bin/bash

: '
    Linux Application Uninstallation Utility

    Author	: 	Viki [ V Natarajan ]
	Contact	:	https://viki.design
    Licence :   MIT
'


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

remove_util() {
    local util_name="$1"
    local util_path="$INSTALL_DIR/$(basename "$util_name")"

    if [ -f "$util_path" ]; then
        if command -v sudo &> /dev/null; then
            sudo rm -f "$util_path"
        else
            rm -f "$util_path"
        fi

        if [ $? -eq 0 ]; then
            echo "[ success  ] $util_name removed successfully."
            UNINSTALL_STATUS["$util_name"]="SUCCESS"
        else
            echo "[ failure  ] Failed to remove $util_name."
            UNINSTALL_STATUS["$util_name"]="FAILED"
        fi
    else
        echo "[ skipped  ] $util_name not found in $INSTALL_DIR."
        UNINSTALL_STATUS["$util_name"]="NOT FOUND"
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

declare -A UNINSTALL_STATUS

# Main uninstallation loop
get_installation_directory

for util in "${UTILS[@]}"; do
    remove_util "$util"
done

# SUMMARY
echo
echo "==================== UNINSTALLATION SUMMARY ===================="
for util in "${UTILS[@]}"; do
    status=${UNINSTALL_STATUS[$util]:-"NOT ATTEMPTED"}
    printf " %-35s : %s\n" "$util" "$status"
done
echo "=============================================================="
echo

