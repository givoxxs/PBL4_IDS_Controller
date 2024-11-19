import subprocess
import logging

logger = logging.getLogger(__name__)

def check_service_status():
    """Kiểm tra trạng thái của UFW và Snort."""
    ufw_status = ""
    snort_status = ""
    try: 
        # Kiểm tra trạng thái UFW
        ufw_status = subprocess.run(["sudo","systemctl", "status", "ufw"], capture_output=True, text=True)
        ufw_status = ufw_status.stdout
    except subprocess.CalledProcessError as e:
        # ufw_status = f"Error checking UFW status: {e.stderr}" # Lỗi nếu command trả về code != 0
        logger.error(f"Error checking UFW status: {e.stderr}", exc_info=True)
    
    try:
        # Kiểm tra trạng thái Snort
        snort_status = subprocess.run(["sudo","systemctl", "status", "snort3-nids"], capture_output=True, text=True)
        snort_status = snort_status.stdout
    except subprocess.CalledProcessError as e:
        snort_status = f"Error checking Snort status: {e.stderr}"
    
    return ufw_status, snort_status
    