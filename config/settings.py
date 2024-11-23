import os
from pathlib import Path
from dotenv import load_dotenv
import platform

class Settings:
    APP_TITLE = "Quản trị mạng"
    APP_WIDTH = 600
    APP_HEIGHT = 400
    load_dotenv()
    ROOT_PATH = os.getenv("ROOT_PATH") 

    if ROOT_PATH is None:
        print("Error: ROOT_PATH not found in .env file.")

    LOG_PATH = os.path.join(ROOT_PATH, "alert_csv.txt")
    RULE_PATH = os.path.join(ROOT_PATH, "local.rules")
  
    
    # if os.name == 'nt':  # Windows
    #         LOG_PATH = "assets/alert_csv.txt"
    #         RULE_PATH = "assets/local.rules"
    # else:  # Ubuntu
    #     LOG_PATH = "/var/log/snort/alert_csv.txt"
    #     RULE_PATH = ""  