#!/bin/bash
LOG_FILE="/home/azureuser/IrakIroan/azure_file_explorer/tunnel.log"
URL_FILE="/home/azureuser/IrakIroan/azure_file_explorer/tunnel_url.txt"

/usr/bin/cloudflared tunnel --url http://127.0.0.1:8088 2>&1 | while read -r line; do
    echo "$line" >> "$LOG_FILE"
    if [[ "$line" =~ https://[a-zA-Z0-9-]+\.trycloudflare\.com ]]; then
        url=$(echo "$line" | grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" | head -n 1)
        echo "$url" > "$URL_FILE"
        echo "LIVE_WINDOWS_11_EXPLORER_URL: $url"
    fi
done
