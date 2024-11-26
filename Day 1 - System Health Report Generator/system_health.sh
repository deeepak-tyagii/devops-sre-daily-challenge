#!/bin/bash

LOG_FILE="/tmp/system_health.log"

bold="\033[1m"
noformat="\033[0m"
greentext="\033[38;5;46m"
yellowtext="\033[38;5;11m"
hotpink="\033[38;5;206m"
redtext="\033[38;5;203m"
aquatext="\033[38;5;86m"

DEBUG=0

# Enable debugging if DEBUG is set to 1
[ "$DEBUG" -eq 1 ] && set -x

# Logging function
log_message() {
    echo -e "${aquatext}$(date '+%Y-%m-%d %H:%M:%S')${noformat} - $1" | tee -a "$LOG_FILE"
}

# Exception handler
exception_handler() {
    log_message "$redtextERROR$noformat: $1"
    exit 1
}

# Check disk usage
check_disk_usage() {
    log_message "$yellowtext Checking disk usage...$noformat"
    df -h | tee -a "$LOG_FILE"
}

# Monitor running services
monitor_services() {
    log_message "$yellowtext Monitoring running services...$noformat"
    systemctl list-units --type=service --state=running | tee -a "$LOG_FILE"
}

# Assess memory usage
assess_memory_usage() {
    log_message "$yellowtext Assessing memory usage...$noformat"
    free -h | tee -a "$LOG_FILE"
}

# Evaluate CPU usage
evaluate_cpu_usage() {
    log_message "$yellowtext Evaluating CPU usage...$noformat"
    top -bn1 | grep "Cpu(s)" | tee -a "$LOG_FILE"
}

# Send a comprehensive report via email
send_report() {
    local EMAIL="$1"
    if [[ "$EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        log_message "$yellowtext Sending comprehensive report to $noformat$EMAIL..."
        mail -s "System Health Report" "$EMAIL" < "$LOG_FILE" || exception_handler "Failed to send the email"
    else
        log_message "$redtext Invalid email address:$noformat $EMAIL"
        return 1
    fi
}

# Add cron job to send email every 4 hours
setup_cron_job() {
    read -p "$(echo -e "${yellowtext}Enter your email address for the cron job: ${noformat}")" EMAIL
    if [[ "$EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        CRON_JOB="0 */4 * * * /bin/bash $(realpath "$0") --email $EMAIL"
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | sort | uniq | crontab -
        log_message "$yellowtext Cron job added to send reports every 4 hours to $EMAIL.$noformat"
    else
        log_message "$redtext Invalid email address. Cron job not created.$noformat"
    fi
}

# Menu
menu() {
    clear
    echo -e "$bold$hotpink================== System Health Check ==================$noformat"
    printf "\t1. Check Disk Usage\n"
    printf "\t2. Monitor Running Services\n"
    printf "\t3. Assess Memory Usage\n"
    printf "\t4. Evaluate CPU Usage\n"
    printf "\t5. Send a Comprehensive Report via Email\n"
    printf "\t6. Setup Cron Job for Report Every 4 Hours\n"
    printf "\t7. Exit\n"
    echo -e "$bold$hotpink=========================================================$noformat"
}

# Main logic
main() {
    while true; do
        menu
        read -p "$(echo -e "${bold}${greentext} Choose an option [1-7]: ${noformat}")" CHOICE
        case "$CHOICE" in
            1) check_disk_usage ;;
            2) monitor_services ;;
            3) assess_memory_usage ;;
            4) evaluate_cpu_usage ;;
            5) 
                 read -p "$(echo -e "${yellowtext}Enter your email address: ${noformat}")" EMAIL
                send_report "$EMAIL"
                ;;
            6) setup_cron_job ;;
            7) log_message "Exiting."; exit 0 ;;
            *) echo -e "${redtext}Invalid option. Please try again.${noformat}" ;;
        esac
        read -p "Press Enter to continue..."  # Pause before showing the menu again
    done
}

# Handle command-line arguments for cron
if [[ "$1" == "--email" && -n "$2" ]]; then
    send_report "$2"
    exit 0
fi

# Run the script interactively
main
