import logging
import logging.handlers
import os
import sys

def create_rotating_file_handler(log_file_path, max_bytes=10*1024*1024, backup_count=5):
        """Tạo RotatingFileHandler với UTF-8 encoding."""
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8" # Thêm encoding ở đây
        )
        return file_handler

def setup_logging(log_level=logging.INFO, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', log_file = "ids.log"):
    """Cấu hình logging."""

    # Tạo logger root
    logger = logging.getLogger() # root logger
    logger.setLevel(log_level)
    
    # tạo console handler cho error và info
    console_handler = logging.StreamHandler(sys.stdout) # Ghi log ra console
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    console_handler.setLevel(logging.INFO) # set level cho handler
    console_handler.setLevel(logging.ERROR) # set level cho handler

    # Tạo RotatingFileHandler (nếu log_file được cung cấp)
    if log_file:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True) # tạo log_dir nếu chưa tồn tại
        log_file_path = os.path.join(log_dir, log_file)

        if not any(isinstance(handler, logging.handlers.RotatingFileHandler) and handler.baseFilename == log_file_path for handler in logger.handlers): # check file handler đã tồn tại chưa
            file_handler = create_rotating_file_handler(log_file_path) #  RotatingFileHandler
            file_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(file_handler)