#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$DIR/tunnel.log"
URL_FILE="$DIR/tunnel_url.txt"

mkdir -p /home/azureuser/.webterminal

/usr/bin/cloudflared tunnel --url http://127.0.0.1:8088 2>&1 | while read -r line; do
    echo "$line" >> "$LOG_FILE"
    if [[ "$line" =~ https://[a-zA-Z0-9-]+\.trycloudflare\.com ]]; then
        url=$(echo "$line" | grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" | head -n 1)
        echo "$url" > "$URL_FILE"
        echo "$url" > "/home/azureuser/.webterminal/windows_explorer_url.txt"
        echo "$url" > "/home/azureuser/windows_explorer_url.txt"
        echo "$url" > "$DIR/../webterminal/windows_explorer_url.txt" 2>/dev/null
        echo "${url}/monitor" > "/home/azureuser/.webterminal/live_monitor_url.txt"
        cat <<EOF > "/home/azureuser/.webterminal/pinned_links.md"
# Live System Pinned Links

- **File Explorer & Web Dashboard:** ${url}/
- **Dedicated CPU & Resource Monitor:** ${url}/monitor
EOF
        echo "LIVE_WINDOWS_11_EXPLORER_URL: $url"
    fi
done
