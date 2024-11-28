import os
from pathlib import Path
from dotenv import load_dotenv
import platform

class Settings:
    APP_TITLE = "Quản trị mạng"
    APP_WIDTH = 600
    APP_HEIGHT = 400
    LOG_PATH = "/var/log/snort/alert_csv.txt"
    RULE_PATH = "/etc/snort/rules/local.rules"
    
    if os.name == 'nt':  # Windows
            LOG_PATH = "assets/alert_csv.txt"
            RULE_PATH = "assets/local.rules"
    else:  # Ubuntu
        LOG_PATH = "/var/log/snort/alert_csv.txt"
        RULE_PATH = "/usr/local/etc/rules/local.rules"  