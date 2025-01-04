from models.alert import Alert
import logging
import os

logger = logging.getLogger(__name__)

class AlertReader:
    """
    Đọc file CSV chứa thông tin alert và tạo đối tượng Alert.
    """
    def __init__(self, file_path):
        """
        Khởi tạo đối tượng AlertReader.

        Args:
            file_path (str): Đường dẫn đến file CSV.
        """
        self.file_path = file_path

    def read_alerts(self, last_update_time=0, has_header=True):
        """
        Đọc các alert từ file CSV, chỉ đọc nếu file đã được cập nhật.

        Args:
            last_update_time (float, optional): Thời điểm cập nhật cuối cùng. Mặc định là 0.
            has_header (bool, optional): File có header không. Mặc định là True.

        Returns:
            list[Alert]: Danh sách các đối tượng Alert đã đọc, hoặc None nếu có lỗi.
        """
        alerts = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                file_update_time = os.path.getmtime(self.file_path)
                if file_update_time > last_update_time:
                    if has_header:
                        try:
                            header = next(file)
                        except StopIteration:
                            logger.warning("File is empty, no header to skip")
                            return []

                        if not self._validate_header(header):
                            logger.warning("Header is not as expected, continue with line reading")

                    for line in file:
                        alert_data = self._parse_alert_line(line.strip())
                        if alert_data:
                            alert = Alert(*alert_data)
                            alerts.append(alert)
                    logger.info(f"Đọc thành công {len(alerts)} alerts từ {self.file_path}")
                    return alerts
                else:
                    logger.info(f"File {self.file_path} không thay đổi, không đọc")
                    return []
        except FileNotFoundError:
            logger.error(f"File {self.file_path} không tồn tại.", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Lỗi khi đọc file: {e}", exc_info=True)
            return None

    def _validate_header(self, header):
        """
        Kiểm tra header của file CSV.

        Args:
            header (str): Dòng tiêu đề của file CSV.

        Returns:
            bool: True nếu header hợp lệ, False nếu không.
        """
        expected_header = "timestamp,action,protocol,gid,sid,rev,msg,service,src_IP,src_Port,dst_IP,dst_Port,priority"
        return header.strip().lower() == expected_header.lower()

    def _parse_alert_line(self, line):
        """
        Phân tích một dòng trong file alert_csv.txt.

        Args:
            line (str): Dòng dữ liệu cần phân tích.

        Returns:
            tuple: Dữ liệu đã phân tích, hoặc None nếu có lỗi.
        """
        data = line.split(",")

        if len(data) < 13:
            logger.error(f"Invalid alert line: {line}. Số trường ({len(data)}) < 13")
            return None

        timestamp = data[0].strip()
        action = data[1].strip()
        protocol = data[2].strip()
        msg = data[6].strip('"')
        service = data[7].strip()
        src_IP = data[8].strip()
        dst_IP = data[10].strip()

        try:
            gid = int(data[3]) if data[3] else -1
        except ValueError as e:
            logger.error(f"Error parsing gid: {data[3]} - {e}")
            gid = -1

        try:
            sid = int(data[4]) if data[4] else -1
        except ValueError as e:
            logger.error(f"Error parsing sid: {data[4]} - {e}")
            sid = -1

        try:
            rev = int(data[5]) if data[5] else -1
        except ValueError as e:
            logger.error(f"Error parsing rev: {data[5]} - {e}")
            rev = -1

        try:
            src_Port = int(data[9].strip()) if data[9].strip() else -1
        except ValueError as e:
            logger.error(f"Error parsing src_Port: {data[9]} - {e}")
            src_Port = -1

        try:
            dst_Port = int(data[11].strip()) if data[11].strip() else -1
        except ValueError as e:
            logger.error(f"Error parsing dst_Port: {data[11]} - {e}")
            dst_Port = -1

        # Validate priority
        priority = data[12].strip().lower()
        valid_priorities = ["critical", "high", "medium", "low"]
        if priority not in valid_priorities:
            logger.warning(f"Invalid priority: {priority}, using default 'low'")
            priority = "low"

        occur = 1
        action_taken = 0
        return (timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, occur, action_taken, priority)
