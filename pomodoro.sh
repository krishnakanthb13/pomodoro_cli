#!/bin/bash

# Pomodoro Timer Launcher for Linux/macOS
# Matches functionality of pomodoro.bat

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Define Colors
CYAN='\033[0;36m'
GREEN='\033[0;92m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
PURPLE='\033[0;95m'
GRAY='\033[0;90m'
WHITE='\033[0;37m' 
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to run pomodoro.py
run_pomodoro() {
    # Check for python3
    if command -v python3 &> /dev/null; then
        python3 "$@"
    elif command -v python &> /dev/null; then
        python "$@"
    else
        echo -e "${RED}Error: Python not found. Please install Python 3.${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi
}

while true; do
    clear
    echo
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🍅 ${BOLD}POMODORO TIMER LAUNCHER${NC}${CYAN} 🍅                    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${WHITE}Select your Pomodoro preset:${NC}"
    echo
    echo -e "${PURPLE}[1] Deep Flow Session    - 90M work │ 10M notes │ 25M break │ x2  ~ aspirational${NC}"
    echo -e "${RED}[2] Deep Work Session    - 50M work │ 10M notes │ 15M break │ x3  ~ deeper work${NC}"
    echo -e "${YELLOW}[3] Extended Focus       - 45M work │ 10M notes │ 10M break │ x4  ~ sweet spot${NC}"
    echo -e "${GREEN}[4] Study Session        - 30M work │ 05M notes │ 10M break │ x5  ~ learning${NC}"
    echo
    echo -e "${CYAN}[5] Classic Pomodoro     - 25M work │ 05M notes │ 05M break │ x4  ~ default${NC}"
    echo -e "${YELLOW}[6] Quick Sprint         - 15M work │ 03M notes │ 05M break │ x6  ~ warm-up${NC}"
    echo -e "${YELLOW}[7] Ultra Sprint         - 10M work │ 02M notes │ 03M break │ x8  ~ momentum${NC}"
    echo
    echo -e "${GRAY}[8] Custom Settings      - Enter your own timings${NC}"
    echo -e "${GRAY}[9] Test Mode            - 01M work │ 01M notes │ 01M break │ x2  ~ testing${NC}"
    echo
    echo -e "${CYAN}[R] Review Sessions      - View session history${NC}"
    echo
    echo -e "${RED}[0] Exit${NC}"
    echo
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo

    read -p "Enter your choice (0-9/R): " choice

    echo
    case $choice in
        1)
            echo -e "${PURPLE}Starting Deep Flow Session...${NC}"
            run_pomodoro pomodoro.py -w 90 -n 10 -b 25 -c 2 --chime mixkit-melodical-flute-music.wav
            ;;
        2)
            echo -e "${RED}Starting Deep Work Session...${NC}"
            run_pomodoro pomodoro.py -w 50 -n 10 -b 15 -c 3 --chime mixkit-melodical-flute-music.wav
            ;;
        3)
            echo -e "${YELLOW}Starting Extended Focus...${NC}"
            run_pomodoro pomodoro.py -w 45 -n 10 -b 10 -c 4 --chime mixkit-melodical-flute-music.wav
            ;;
        4)
            echo -e "${GREEN}Starting Study Session...${NC}"
            run_pomodoro pomodoro.py -w 30 -n 5 -b 10 -c 5 --chime mixkit-melodical-flute-music.wav
            ;;
        5)
            echo -e "${CYAN}Starting Classic Pomodoro...${NC}"
            run_pomodoro pomodoro.py -w 25 -n 5 -b 5 -c 4 --chime mixkit-arabian-mystery-harp.wav
            ;;
        6)
            echo -e "${YELLOW}Starting Quick Sprint...${NC}"
            run_pomodoro pomodoro.py -w 15 -n 3 -b 5 -c 6 --chime mixkit-arabian-mystery-harp.wav
            ;;
        7)
            echo -e "${YELLOW}Starting Ultra Sprint...${NC}"
            run_pomodoro pomodoro.py -w 10 -n 2 -b 3 -c 8 --chime mixkit-arabian-mystery-harp.wav
            ;;
        8)
            echo
            echo -e "${CYAN}═══════════════════════════════════════${NC}"
            echo -e "  ${BOLD}CUSTOM POMODORO SETTINGS${NC}"
            echo -e "${CYAN}═══════════════════════════════════════${NC}"
            echo
            read -p "Work duration (minutes): " work
            read -p "Note-taking duration (minutes): " note
            read -p "Break duration (minutes): " break_time
            read -p "Number of cycles: " cycles
            echo
            echo -e "${GREEN}Starting custom session...${NC}"
            run_pomodoro pomodoro.py -w "$work" -n "$note" -b "$break_time" -c "$cycles" --select-chime
            ;;
        9)
            echo -e "${GRAY}Starting Test Mode (1 min each)...${NC}"
            run_pomodoro pomodoro.py -w 1 -n 1 -b 1 -c 2 --select-chime
            ;;
        [Rr]*)
            echo -e "${CYAN}Launching Reviewer...${NC}"
            # Check if pomodoro_review.sh exists and is executable
            if [ -f "./pomodoro_review.sh" ]; then
                chmod +x ./pomodoro_review.sh
                ./pomodoro_review.sh
            else
                echo -e "${RED}pomodoro_review.sh not found!${NC}"
            fi
            ;;
        0)
            echo
            echo -e "${CYAN}Thank you for using Pomodoro Timer! 🍅${NC}"
            echo
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice! Please try again.${NC}"
            sleep 1
            ;;
    esac

    echo
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo
    read -p "Run another session? (y/n): " again
    echo
    if [[ ! $again =~ ^[Yy] ]]; then
        echo -e "${CYAN}Thank you for using Pomodoro Timer! 🍅${NC}"
        exit 0
    fi
done
