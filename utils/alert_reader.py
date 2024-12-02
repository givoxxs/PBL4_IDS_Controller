from models.alert import Alert
import logging
import os

logger = logging.getLogger(__name__)

class AlertReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_alerts(self, last_update_time=0):
        alerts = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as file: # Thêm encoding="utf-8" để xử lý các ký tự đặc biệt
                file_update_time = os.path.getmtime(self.file_path)
                if file_update_time > last_update_time: # chỉ đọc nếu file đã thay đổi
                    next(file) # skip header line
                    for line in file:
                        alert_data = self._parse_alert_line(line.strip())
                        if alert_data:
                            alert = Alert(*alert_data)
                            alerts.append(alert)
            return alerts
        except FileNotFoundError:
            logger.error(f"File {self.file_path} không tồn tại.", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Lỗi khi đọc file: {e}", exc_info=True)
            return None
        
    def _parse_alert_line(self, line):
        """Phân tích một dòng trong file alert_csv.txt."""
        data = line.split(",")

        # Kiểm tra số lượng trường dữ liệu.  Điều chỉnh số 12 nếu file của bạn có số trường khác.
        if len(data) < 12:  # Cho phép số trường ít hơn 12
            print(f"Invalid alert line: {line}. Not enough fields.")
            logger.error(f"Invalid alert line: {line}. Not enough fields.")
            return None

        try:
            # Xử lý các trường có thể bị thiếu hoặc rỗng.  Sử dụng giá trị mặc định nếu cần.
            timestamp = data[0].strip()
            action = data[1].strip()
            protocol = data[2].strip()
            gid = int(data[3]) if data[3] else None
            sid = int(data[4]) if data[4] else None
            rev = int(data[5]) if data[5] else None
            msg = data[6].strip('"') # Loại bỏ dấu ngoặc kép
            service = data[7].strip()
            src_IP = data[8].strip()
            # src_Port = int(data[9]) if data[9] else None
            dst_IP = data[10].strip()
            # dst_Port = int(data[11]) if data[11] else None
            
            src_Port = int(data[9].strip()) if data[9].strip() else None # Strip before checking
            dst_Port = int(data[11].strip()) if data[11].strip() else None # Strip before checking
            priority = 3
            occur = 1
            action_taken = 0
            return (timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, priority, occur, action_taken)


        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing alert line: {line} - {e}")
            return None
