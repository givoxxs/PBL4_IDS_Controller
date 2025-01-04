from models.alert import Alert
import logging
import os
from utils.file_modifier import FileModifier

logger = logging.getLogger(__name__)

class AlertReader:
    """
    Đọc file CSV chứa thông tin alert và tạo đối tượng Alert.
    """
    def __init__(self, file_path, separator=","):
        """
        Khởi tạo đối tượng AlertReader.

        Args:
            file_path (str): Đường dẫn đến file CSV.
            separator (str, optional): Ký tự phân tách giữa các trường trong file CSV. Mặc định là ','.
        """
        self.file_path = file_path
        self.separator = separator  # Gán giá trị separator vào đối tượng
        self.file_modifier = FileModifier()

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

                            # if alert.priority == '1' or alert.priority == '2':
                            #     existing_alerts = {(a.src_IP, a.dst_IP, a.protocol) for a in alerts if a.action_taken}
                            #     alert_key = (alert.src_IP, alert.dst_IP, alert.protocol)

                            #     if alert_key in existing_alerts:
                            #         alert.action_taken = True
                            #     else:
                            #         self.file_modifier.block_fastest(alert)
                            #         alert.action_taken = True    

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
        data = line.split(self.separator)
        if len(data) < 13:
            logger.error(f"Invalid alert line: {line}. Số trường ({len(data)}) < 13")
            return None

        timestamp = data[0].strip()
        action = data[1].strip()
        protocol = data[2].strip()
        gid = int(data[3].strip()) if data[3].strip() else -1
        sid = int(data[4].strip()) if data[4].strip() else -1
        rev = int(data[5].strip()) if data[5].strip() else -1
        msg = data[6].strip('"')
        service = data[7].strip()
        src_IP = data[8].strip()
        src_Port = int(data[9].strip()) if data[9].strip() else -1
        dst_IP = data[10].strip()
        dst_Port = int(data[11].strip()) if data[11].strip() else -1

        # Lấy giá trị priority từ chỉ mục 12
        priority = data[12].strip()

        valid_priorities = ["0", "1", "2", "3"]

        if priority not in valid_priorities:
            logger.warning(f"Invalid priority: {priority}, using default '3'")
            priority = "3"

        occur = 1
        action_taken = 0
        last_seen = None

        return (timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, priority, occur, action_taken, last_seen)