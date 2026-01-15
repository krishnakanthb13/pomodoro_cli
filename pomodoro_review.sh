#!/bin/bash

# Pomodoro Reviewer - Linux/macOS Edition
# Launcher for the web-based Pomodoro Reviewer

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Define Colors
CYAN='\033[0;36m'
GREEN='\033[0;92m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

HTML_FILE="pomodoro_review.html"
NOTES_FILE="pomodoro.txt"
PORT=8080

separator="════════════════════════════════════════════════════════════"

echo -e "${CYAN}$separator${NC}"
echo -e "${CYAN}           POMODORO REVIEWER SERVER${NC}"
echo -e "${CYAN}$separator${NC}"
echo

if [ ! -f "$HTML_FILE" ]; then
    echo -e "${RED}[ERROR] $HTML_FILE not found!${NC}"
    read -p "Press Enter to exit"
    exit 1
fi

if [ ! -f "$NOTES_FILE" ]; then
    echo -e "${RED}[ERROR] $NOTES_FILE not found!${NC}"
    read -p "Press Enter to exit"
    exit 1
fi

echo -e "${CYAN}Starting server and browser...${NC}"

# Function to open URL
open_url() {
    sleep 2
    local url="http://localhost:$PORT/pomodoro_review.html"
    
    if command -v open &> /dev/null; then
        # macOS
        open "$url"
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open "$url"
    elif command -v python3 &> /dev/null; then
         # Try python webbrowser module
         python3 -m webbrowser "$url"
    else
        echo -e "${YELLOW}[WARN] Could not automatically open browser.${NC}"
        echo -e "Please open: $url"
    fi
}

# Run open_url in background
open_url &

echo -e "${GRAY}[INFO] Attempting to start server on port $PORT...${NC}"
echo -e "${YELLOW}[TIP] If the browser loads too fast, just REFRESH (F5).${NC}"
echo

# Detect and run server
if command -v http-server &> /dev/null; then
    echo -e "${GREEN}[OK] Using http-server (Node.js)${NC}"
    http-server -p $PORT -c-1
elif command -v python3 &> /dev/null; then
    echo -e "${GREEN}[OK] Using Python3 server${NC}"
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    # Check version to be safe, but usually python m http.server works for 3, SimpleHTTPServer for 2
    echo -e "${GREEN}[OK] Using Python server${NC}"
    python -m http.server $PORT
else
    echo -e "${RED}[ERROR] Neither http-server nor Python found!${NC}"
    echo "Please install Python (python.org) or Node.js (nodejs.org)."
    read -p "Press Enter to exit"
    exit 1
fi

echo
echo "Server stopped."
read -p "Press Enter to close this window"
