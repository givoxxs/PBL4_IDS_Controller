from models.data_manager import DataManager
from models.alert import Alert
from services.alert_service import AlertService

class IDSController:
    def __init__(self):
        self.data_manager = DataManager()
        self.alert_service = AlertService()

    def get_alerts(self, filter_criteria=None):
        """Lấy danh sách alerts, có thể lọc theo tiêu chí."""
        return self.data_manager.get_alerts(filter_criteria)

    def handle_alert_action(self, alert: Alert, action: str):
        """Xử lý hành động trên alert (safe, ignore, limit, block)."""
        try:
            if action == "safe":
                result = self.alert_service.safe_alert(alert)
            elif action == "ignore":
                result = self.alert_service.ignore_alert(alert)
            elif action == "limit":
                result = self.alert_service.limit_alert(alert)
            elif action == "block":
                result = self.alert_service.block_alert(alert)
            else:
                result = "Invalid action."

            if alert.action_taken: # Chỉ update database nếu action được thực hiện thành công
                self.data_manager.update_alert(alert) # Cập nhật model sau khi xử lý
            
            return result # Trả về kết quả để hiển thị cho người dùng
        except Exception as e: # Bắt lỗi toàn cục
            print(f"Lỗi trong IDSController.handle_alert_action: {e}")
            return f"An error occurred: {e}"

    def get_threats(self):
        """Lấy danh sách threats từ DataManager."""
        return self.data_manager.get_threats()
    
    def handle_threat_action(self, threat_data: dict, action: str):
        """Xử lý hành động trên threat (safe, ignore, limit, block)."""
        try:
            if action == "safe":
                result = self.alert_service.safe_threat(threat_data)
            elif action == "ignore":
                result = self.alert_service.ignore_threat(threat_data)
            elif action == "limit":
                result = self.alert_service.limit_threat(threat_data)
            elif action == "block":
                result = self.alert_service.block_threat(threat_data)
            else:
                result = "Invalid action."

            # Lấy danh sách alert thuộc threat để cập nhật action_taken
            if "successfully" in result or result == "Ignored": # Chỉ khi thực hiện action thành công hoặc ignore thì mới update database
                filter_criteria = {
                    "src_IP": threat_data['src_IP'],
                    "dst_IP": threat_data['dst_IP'],
                    "protocol": threat_data['protocol']
                }
                
                alerts = self.data_manager.get_alerts(filter_criteria=filter_criteria) # Truyền filter_criteria dưới dạng dict
                for alert in alerts:
                    alert.action_taken = True
                    self.data_manager.update_alert(alert)

            return result
        except Exception as e:
            print(f"Lỗi trong IDSController.handle_threat_action: {e}")
            return f"An error occurred: {e}"
    
    def search_alerts(self, search_term):
        """Tìm kiếm alert theo search_term."""
        filter_criteria = { # Tìm kiếm theo msg
                'msg': f"%{search_term}%",
                }
        return self.data_manager.search_alerts(filter_criteria)
    