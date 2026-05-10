#!/bin/bash

CONFIG_FILE="config.py"

echo "Bot Configuration Initialization Script"
echo "This script will generate a new configuration file for your Bale Telegram forwarder Bot."
echo "----------------------------------------"

read -p "Please enter your Bale bot token: " BALE_TOKEN

read -p "Please enter the channel/group UID for message reception and sending: " CHNL_UID

read -p "Please enter the channel/group UID for message forwarding: " DATAS_UID

declare -a CHANNELS_ARRAY

echo "----------------------------------------"
echo "Channel Configuration"
echo "Enter channel usernames and their corresponding message limits."
echo "To finalize channel entries, press Enter without typing any input."
echo "Required format: <channel_username>:<limit>"
echo "Example: bbcpersian:1"

while true; do
    read -p "Enter channel configuration (or press Enter to finalize): " CHANNEL_INPUT
    if [[ -z "$CHANNEL_INPUT" ]]; then
        break
    fi
    if [[ "$CHANNEL_INPUT" =~ ^[^:]+:[0-9]+$ ]]; then
        CHANNELS_ARRAY+=("$CHANNEL_INPUT")
    else
        echo "Invalid input format. Please adhere to the '<channel_username>:<limit>' format or press Enter to finalize."
    fi
done

CONFIG_CONTENT+="BALE_TOKEN = \"$BALE_TOKEN\"\n"
CONFIG_CONTENT+="CHNL_UID = $CHNL_UID\n"
CONFIG_CONTENT+="DATAS_UID = $DATAS_UID\n\n"

CONFIG_CONTENT+="CHANNELS = {\n"

if [ ${#CHANNELS_ARRAY[@]} -gt 0 ]; then
    for item in "${CHANNELS_ARRAY[@]}"; do
        IFS=':' read -r channel_username limit <<< "$item"
        CONFIG_CONTENT+="    \"$channel_username\": $limit,\n"
    done
    CONFIG_CONTENT=$(echo "$CONFIG_CONTENT" | sed '$ s/,$//')
fi
CONFIG_CONTENT+="}\n"

echo -e "$CONFIG_CONTENT" > "$CONFIG_FILE"

echo "----------------------------------------"
echo "Configuration file '$CONFIG_FILE' has been generated successfully."
echo "Proceed with running your bot."

exit 0
