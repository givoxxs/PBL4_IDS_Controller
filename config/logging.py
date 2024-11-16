

import logging
import logging.handlers
import os

# Định dạng log
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def create_file_logger(logger_name, log_file_path, level=logging.DEBUG):
    """Tạo một file logger."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB, 5 file backup
    )
    # file_handler.setFormatter(logging.Formatter(log_format,encoding='utf-8'))
    file_handler.setFormatter(logging.Formatter(log_format)) 
    logger.addHandler(file_handler)
    return logger


def setup_logging():
    """Cấu hình logging."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Danh sách các logger cần tạo. Tên và đường dẫn log file:
    loggers_config = [
        ("root", os.path.join(log_dir, "ids.log")),
        ("data_manager", os.path.join(log_dir, "data_manager.log")),
        ("ids_controller", os.path.join(log_dir, "ids_controller.log")),
        ("alert_reader", os.path.join(log_dir, "alert_reader.log")),
        ("check_services_status", os.path.join(log_dir, "check_services_status.log")),
        ("panel_dashboard", os.path.join(log_dir, "panel_dashboard.log")),
        # ...thêm các logger khác nếu cần
    ]
    
    # Tạo từng logger, đặt mức độ log theo requirement
    for logger_name, log_file in loggers_config:
         create_file_logger(logger_name, log_file)