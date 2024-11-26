import os
import re
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess

# Constants for formatting
BOLD = "\033[1m"
NOFORMAT = "\033[0m"
GREENTEXT = "\033[38;5;46m"
YELLOWTEXT = "\033[38;5;11m"
HOTPINK = "\033[38;5;206m"
REDTEXT = "\033[38;5;203m"
AQUATEXT = "\033[38;5;86m"

# Log file
LOG_FILE = "/tmp/system_health.log"

# Debug flag
DEBUG = 0

if DEBUG:
    import logging
    logging.basicConfig(level=logging.DEBUG)

# Logging function
def log_message(message: str):
    formatted_message = f"{AQUATEXT}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NOFORMAT} - {message}"
    print(formatted_message)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(formatted_message + "\n")

# Exception handler
def exception_handler(message: str):
    log_message(f"{REDTEXT}ERROR{NOFORMAT}: {message}")
    exit(1)

# Check disk usage
def check_disk_usage():
    log_message(f"{YELLOWTEXT}Checking disk usage...{NOFORMAT}")
    result = subprocess.run(["df", "-h"], capture_output=True, text=True)
    print(result.stdout)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(result.stdout)

# Monitor running services
def monitor_services():
    log_message(f"{YELLOWTEXT}Monitoring running services...{NOFORMAT}")
    result = subprocess.run(['service', '--status-all'], capture_output=True, text=True)
    
    # Print the output
    for line in result.stdout.splitlines():
        if '[ + ]' in line:  # Filtering for running services
            print(line)

    with open(LOG_FILE, "a") as log_file:
        log_file.write(result.stdout)

# Assess memory usage
def assess_memory_usage():
    log_message(f"{YELLOWTEXT}Assessing memory usage...{NOFORMAT}")
    result = subprocess.run(["free", "-h"], capture_output=True, text=True)
    print(result.stdout)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(result.stdout)

# Evaluate CPU usage
def evaluate_cpu_usage():
    log_message(f"{YELLOWTEXT}Evaluating CPU usage...{NOFORMAT}")
    result = subprocess.run(["top", "-bn1"], capture_output=True, text=True)
    cpu_info = [line for line in result.stdout.split("\n") if "Cpu(s)" in line]
    if cpu_info:
        print(cpu_info[0])
        with open(LOG_FILE, "a") as log_file:
            log_file.write(cpu_info[0] + "\n")

# Function to send report via email
def send_report(email: str):
    if re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
        log_message(f"{YELLOWTEXT}Sending comprehensive report to {NOFORMAT}{email}...")

        # Read the log file content
        with open(LOG_FILE, "r") as file:
            report_content = file.read()

        sender_email = "your_email_address"
        sender_password = "your_sender_password"
        smtp_server = "smtp.gmail.com"  
        smtp_port = 587  

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "System Health Report"

        # Create HTML content for the email body
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #333333;
                }}
                h1 {{
                    color: #007BFF;
                }}
                p {{
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .important {{
                    color: red;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <h1>System Health Report</h1>
            <p><strong>Date:</strong> {str(datetime.now())}</p>
            <p><strong>Report Summary:</strong></p>
            <p>{report_content}</p>
            <p class="important">Please take action if needed.</p>
        </body>
        </html>
        """
    
        # Attach the HTML content to the email
        msg.attach(MIMEText(html_content, 'html'))

        try:
            # Set up the server and send the email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()
            log_message(f"{GREENTEXT}Report sent successfully to {NOFORMAT} {email}")
        except Exception as e:
            exception_handler(f"Failed to send email: {str(e)}")
    else:
        log_message(f"{REDTEXT}Invalid email address:{NOFORMAT} {email}")

# Add cron job to send report every 4 hours
def setup_cron_job():
    email = input(f"{YELLOWTEXT}Enter your email address for the cron job: {NOFORMAT}")
    if re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
        cron_job = f"* * * * * python3 {os.path.realpath(__file__)} --email {email}\n"  
        # Check existing cron jobs and append the new one
        existing_cron_jobs = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
        cron_jobs = existing_cron_jobs.stdout.splitlines()
        if f"* * * * * python3 {os.path.realpath(__file__)} --email {email}" not in cron_jobs:
            cron_jobs.append(cron_job)  
            cron_job_command = "\n".join(cron_jobs)  # Join all cron jobs with newlines
            process = subprocess.Popen('crontab', stdin=subprocess.PIPE, text=True)
            process.communicate(input=cron_job_command)
            log_message(f"{YELLOWTEXT}Cron job added to send reports every 4 hours to {email}.{NOFORMAT}")
        else:
            log_message(f"{YELLOWTEXT}Cron job for this email already exists.{NOFORMAT}")
    else:
        log_message(f"{REDTEXT}Invalid email address. Cron job not created.{NOFORMAT}")


# Main logic
def main():
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--email" and len(os.sys.argv) > 2:
        email = os.sys.argv[2]
        send_report(email)
        return
    
    while True:
        # Menu
        print(f"{BOLD}{HOTPINK}================== System Health Check =================={NOFORMAT}")
        print("\t1. Check Disk Usage")
        print("\t2. Monitor Running Services")
        print("\t3. Assess Memory Usage")
        print("\t4. Evaluate CPU Usage")
        print("\t5. Send a Comprehensive Report via Email")
        print("\t6. Setup Cron Job for Report Every 4 Hours")
        print("\t7. Exit")
        print(f"{BOLD}{HOTPINK}========================================================={NOFORMAT}")

        choice = input(f"{BOLD}{GREENTEXT}Choose an option [1-7]: {NOFORMAT}")
        if choice == '1':
            check_disk_usage()
        elif choice == '2':
            monitor_services()
        elif choice == '3':
            assess_memory_usage()
        elif choice == '4':
            evaluate_cpu_usage()
        elif choice == '5':
            email = input(f"{YELLOWTEXT}Enter your email address: {NOFORMAT}")
            send_report(email)
        elif choice == '6':
            setup_cron_job()
        elif choice == '7':
            log_message("Exiting.")
            exit(0)
        else:
            print(f"{REDTEXT}Invalid option. Please try again.{NOFORMAT}")

        input("Press Enter to continue...")  # Pause before showing the menu again

if __name__ == "__main__":
    main()
