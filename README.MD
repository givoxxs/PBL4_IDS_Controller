# PBL4: Operating System & Computer Networks  
## Project 505: Exploring Linux OS and Building an Intrusion Detection Application

### Overview  
This project aims to create a user-friendly intrusion detection application for a Linux server, utilizing Snort to monitor and analyze network traffic for signs of unauthorized access. The application assists network administrators in identifying potential intrusions by displaying clear, visualized data related to various network protocols (IP, ICMP, ARP, TCP, UDP).

---

### Project Requirements  
1. **Research**: Learn about Linux OS, Snort configuration, and network protocols (IP, ICMP, ARP, TCP, UDP).
2. **Develop Application**: Build a GUI-based application interfacing with Snort, providing visual statistics to aid in intrusion detection.

---

### Input & Output  
- **Input**: Network intrusion attempts by unauthorized machines.
- **Output**: A user interface displaying collected data and summarizing unusual parameters to assist in identifying potential intrusions.

---

### Project Structure  

```plaintext
ids_application/
├── controller/
│   └── ids_controller.py
├── model/
│   ├── alert.py
│   ├── threat.py
│   └── data_manager.py        # Manages data and database operations
├── view/
│   ├── main_window.py         # Main interface
│   ├── panel_status.py
│   ├── panel_logs.py
│   ├── panel_threats.py
│   └── panel_config.py
├── config/
│   ├── settings.py
├── utils/
│   ├── file_modifier.py
│   ├── alert_reader.py
│   └── plotter.py
├── assets/                    # Folder for external resources or static files
├── logs/                      # Folder for storing log files
├── .gitignore                 # File for excluding unnecessary files from Git
├── config.json                # JSON file for additional configuration options
├── requirements.txt           # Lists project dependencies
├── README.md                  # Project documentation
└── main.py                    # Application entry point

