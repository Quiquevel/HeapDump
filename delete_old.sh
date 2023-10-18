#!/bin/bash

download_folder="/app/downloads"
crontab_log="/app/log_crontab.txt"

if [ ! -e "$crontab_log" ]; then
    touch "$crontab_log"
fi

echo "Start of execution: $(date)" >> "$crontab_log"

# Delete older seven days files.
find "$download_folder" -type f -mtime +7 -exec rm -f {} \; >> "$crontab_log" 2>&1

# Delete empty folders.
find "$download_folder" -type d -empty -delete >> "$crontab_log" 2>&1

echo "End of execution: $(date)" >> "$crontab_log"