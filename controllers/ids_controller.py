from models.data_manager import DataManager
from models.alert import Alert
from services.alert_service import AlertService
import logging
import os
import json
logger = logging.getLogger(__name__)

class IDSController:
    SAFE_ACTION = "safe"
    IGNORE_ACTION = "ignore"
    LIMIT_ACTION = "limit"
    BLOCK_ACTION = "block"
    INVALID_ACTION = "Invalid action."
    SUCCESS_MESSAGE = "successfully"
    IGNORE_MESSAGE = "Ignored"

    def __init__(self, root):
        self.root = root
        self.data_manager = DataManager(root)
        self.alert_service = AlertService(root)


    def _apply_pagination(self, page, per_page):
        """Helper to calculate offset based on page and per_page"""
        if page < 1:
            raise ValueError("Page must be 1 or greater.")
        if per_page <= 0:
            raise ValueError("Per_page must be a positive integer.")

        offset = (page - 1) * per_page
        return offset
    def update_alerts_from_file(self):
        return self.data_manager.update_alerts_from_file()
    def get_alerts(self, filter_criteria=None, page=1, per_page=100):
        """Lấy danh sách alerts, có thể lọc theo tiêu chí và phân trang."""
        offset = self._apply_pagination(page, per_page)
        return self.data_manager.get_alerts(filter_criteria, limit=per_page, offset=offset)

    def get_alerts_by_action_taken(self, filter_criteria=None, page=1, per_page=100):
        """Lấy danh sách alerts đã xử lý và phân trang"""
        offset = self._apply_pagination(page, per_page)
        try:
             alerts = self.data_manager.get_alerts_by_action_taken(limit=per_page, offset=offset)
             return alerts
        except Exception as e:
            logger.error(f"Error fetching alerts by action taken: {e}", exc_info = True)
            raise

    def get_total_alerts(self, filter_criteria=None):
        """Lấy tổng số alerts, có thể lọc theo tiêu chí."""
        return len(self.data_manager.get_alerts(filter_criteria))
    
    def _handle_alert_action_logic(self, alert, action):
         """Common logic for handling alert action """
         if action == IDSController.SAFE_ACTION:
              result = self.alert_service.safe_alert(alert)
         elif action == IDSController.IGNORE_ACTION:
             result = self.alert_service.ignore_alert(alert)
         elif action == IDSController.LIMIT_ACTION:
            result = self.alert_service.limit_alert(alert)
         elif action == IDSController.BLOCK_ACTION:
             result = self.alert_service.block_alert(alert)
         else:
            result = IDSController.INVALID_ACTION
         
         if alert.action_taken:
              self.data_manager.update_alert(alert)
         
         return result

    def handle_alert_action(self, alert: Alert, action: str):
         """Xử lý hành động trên alert (safe, ignore, limit, block)."""
         try:
            result = self._handle_alert_action_logic(alert, action)
            return result  # Trả về kết quả để hiển thị cho người dùng
         except Exception as e:  # Bắt lỗi toàn cục
            logger.error(f"Error in IDSController.handle_alert_action: {e}", exc_info = True)
            return f"An error occurred: {e}"
        
    def get_threats(self, limit=None, offset=None, priority = None):
        """Lấy danh sách các threat có priority cao từ database (nhóm các alert) và phân trang."""
        logger.info("Loading data manager get threats")
        try:
            threats = self.data_manager.get_threats(limit,offset, priority)
            return threats

        except Exception as e:
            logger.error(f"Lỗi khi lấy threats: {e}", exc_info=True)
            return []

    def get_total_threats(self):
        """
        Get the total number of threats.
        """
        threats = self.data_manager.get_threats()  # Get all threats using the corrected method
        return len(threats)  # get the length of the array
    
    def _handle_threat_action_logic(self, threat_data, action):
        """Common logic to handle threat actions"""
        if action == IDSController.SAFE_ACTION:
             result = self.alert_service.safe_threat(threat_data)
        elif action == IDSController.IGNORE_ACTION:
              result = self.alert_service.ignore_threat(threat_data)
        elif action == IDSController.LIMIT_ACTION:
            result = self.alert_service.limit_threat(threat_data)
        elif action == IDSController.BLOCK_ACTION:
             result = self.alert_service.block_threat(threat_data)
        else:
            result = IDSController.INVALID_ACTION
        
        if IDSController.SUCCESS_MESSAGE in result or result == IDSController.IGNORE_MESSAGE:
            filter_criteria = {
                 "src_IP": threat_data['src_IP'],
                 "dst_IP": threat_data['dst_IP'],
                 "protocol": threat_data['protocol'],
            }

            alerts = self.data_manager.get_alerts(filter_criteria=filter_criteria)
            for alert in alerts:
               alert.action_taken = 1
               self.data_manager.update_alert(alert)
        return result

    def handle_threat_action(self, threat_data: dict, action: str):
        """Xử lý hành động trên threat (safe, ignore, limit, block)."""
        try:
             result = self._handle_threat_action_logic(threat_data, action)
             return result
        except Exception as e:
             logger.error(f"Error in IDSController.handle_threat_action: {e}", exc_info=True)
             return f"An error occurred: {e}"
            
    def search_alerts(self, search_term, page=1, per_page=100):
        """Tìm kiếm alert theo search_term và phân trang."""
        filter_criteria = {'msg': f"%{search_term}%"}
        offset = self._apply_pagination(page, per_page)
        return self.data_manager.search_alerts(filter_criteria, limit=per_page, offset=offset)

    def get_total_search_result(self, search_term):
        """Get the total search result for search term"""
        filter_criteria = {'msg': f"%{search_term}%"}
        return len(self.data_manager.search_alerts(filter_criteria))

    def collect_data_for_dashboard(self):
        """Collects data for dashboard"""
        logger.info("Collecting data for dashboard")
        logger.info("Getting alerts in collect_data_for_dashboard")
        alerts = self.get_alerts()
        return alerts
    
    def get_all_protocols(self):
         """Lấy danh sách tất cả các giao thức từ alerts."""
         all_alerts = self.data_manager.get_alerts()  # Get all alerts from the DataManager
         protocols = set(alert.protocol for alert in all_alerts)
         return list(protocols) # return distinct list of protocols
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