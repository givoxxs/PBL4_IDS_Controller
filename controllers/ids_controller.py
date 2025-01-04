import json
from models.data_manager import DataManager
from models.alert import Alert
from services.alert_service import AlertService

class IDSController:
    def __init__(self, root):
        self.root = root
        self.config = {
            "update_interval": 300000,
            "max_listbox_items": 20,
            # ... other default settings
        }
        self.data_manager = DataManager(root)
        self.alert_service = AlertService(root)

    def get_alerts(self, filter_criteria=None, page=1, per_page=100):  # Thêm tham số page và per_page
        """Lấy danh sách alerts, có thể lọc theo tiêu chí và phân trang."""
        offset = (page - 1) * per_page
        return self.data_manager.get_alerts(filter_criteria, limit=per_page, offset=offset)
    
    def get_total_alerts(self, filter_criteria=None): # Hàm lấy tổng số alert sau khi lọc
        """Lấy tổng số alerts, có thể lọc theo tiêu chí."""
        return len(self.data_manager.get_alerts(filter_criteria))

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
            
            if alert.action_taken:
                self.data_manager.update_alert(alert)
                self.alerts = self.get_alerts()
            
            return result # Trả về kết quả để hiển thị cho người dùng
        except Exception as e: # Bắt lỗi toàn cục
            print(f"Lỗi trong IDSController.handle_alert_action: {e}")
            return f"An error occurred: {e}"
    
    def get_threats(self, page=1, per_page=100): # phân trang cho threat
        """Lấy danh sách threats từ DataManager."""

        offset = (page-1) * per_page
        return self.data_manager.get_threats(limit=per_page, offset=offset)
    
    def get_total_threats(self):
        """Lấy tổng số threats từ DataManager."""
        return len(self.data_manager.get_threats())
    
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
    
    def search_alerts(self, search_term, page=1, per_page=100):  # Thêm tham số page và per_page
        """Tìm kiếm alert theo search_term và phân trang."""

        filter_criteria = { # Tìm kiếm theo msg
                'msg': f"%{search_term}%",
                }
        offset = (page - 1) * per_page
        return self.data_manager.search_alerts(filter_criteria, limit=per_page, offset=offset)
    
    def get_total_search_result(self, search_term):
        filter_criteria = {'msg': f"%{search_term}%"}
        return len(self.data_manager.search_alerts(filter_criteria))
    
    def collect_data_for_dashboard(self):
        print("Collecting data for dashboard")
        print("Getting alerts in collect_data_for_dashboard")
        alerts = self.get_alerts()
    
    def load_config(self, config_path="dashboard_config.json"):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f) # Update the config dictionary
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            # Handle error appropriately, e.g., use default config


    def save_config(self, config_path="dashboard_config.json"):
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
