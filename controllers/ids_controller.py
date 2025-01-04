import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Dict, List, Optional
from models.data_manager import DataManager
from models.alert import Alert
from services.alert_service import AlertService


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
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=os.cpu_count() * 2)

    def _apply_pagination(self, page: int, per_page: int) -> int:
        """Calculate the offset based on the current page and number of items per page."""
        if page < 1:
            raise ValueError("Page must be 1 or greater.")
        if per_page <= 0:
            raise ValueError("Per_page must be a positive integer.")
        return (page - 1) * per_page

    def update_alerts_from_file(self):
       """Update alerts from log file using DataManager."""
       return self.data_manager.update_alerts_from_file()

    def get_alerts(self, filter_criteria: Optional[Dict] = None, page: int = 1, per_page: int = 100) -> List[Alert]:
        """Get alerts from the database with pagination."""
        offset = self._apply_pagination(page, per_page)
        return self.data_manager.get_alerts(filter_criteria=filter_criteria, limit=per_page, offset=offset)

    def get_total_alerts(self, filter_criteria: Optional[Dict] = None) -> int:
        """Get the total number of alerts matching the filter criteria."""
        return len(self.data_manager.get_alerts(filter_criteria))
    
    async def _async_handle_action(self, alert_dict: Dict, action: str) -> str:
        """Handles alert actions asynchronously."""
        if action == IDSController.SAFE_ACTION:
            result = await asyncio.to_thread(self.alert_service.safe_threat, action, alert_dict)
        elif action == IDSController.IGNORE_ACTION:
            result = await asyncio.to_thread(self.alert_service.ignore_threat, action, alert_dict)
        elif action == IDSController.LIMIT_ACTION:
            result = await asyncio.to_thread(self.alert_service.limit_threat, action, alert_dict)
        elif action == IDSController.BLOCK_ACTION:
            result = await asyncio.to_thread(self.alert_service.block_threat, action, alert_dict)
        else:
            result = IDSController.INVALID_ACTION
        return result

    def handle_alert_action(self, alert: Alert, action: str) -> str:
        """Handles actions for a single alert."""
        try:
            # Convert the Alert object to a dict before calling _async_handle_action
            alert_dict = alert.to_dict()
            result = asyncio.run(self._async_handle_action(alert_dict, action))
           
            # Update the alert in memory and database
            self._update_alert_action(alert, result)
            return result
        except Exception as e:
            logger.error(f"Error in IDSController.handle_alert_action: {e}", exc_info=True)
            return f"An error occurred: {e}"

    def _update_alert_action(self, alert: Alert, action: str):
        """Update alert action and action_taken fields."""
        if IDSController.SUCCESS_MESSAGE in action or action == IDSController.IGNORE_MESSAGE:
            alert.action_taken = 1  # True
            alert.action = action.title()
            self.data_manager.update_alert(alert)

    def handle_threat_action(self, threat_data: Dict, action: str) -> str:
        """Handles actions for a group of alerts based on threat data."""
        try:
            result = self._process_threat_action(action, threat_data)
            filter_criteria = {
                "src_IP": threat_data['src_IP'],
                "dst_IP": threat_data['dst_IP'],
                "protocol": threat_data['protocol'],
            }
            alerts = self.data_manager.get_alerts(filter_criteria=filter_criteria)
            for alert in alerts:
               self._update_alert_action(alert, result)
            return result
        except Exception as e:
            logger.error(f"Error in IDSController.handle_threat_action: {e}", exc_info=True)
            return f"An error occurred: {e}"
    
    def _process_threat_action(self, action: str, threat_data: Dict) -> str:
        """Processes threat actions and returns result."""
        if action == IDSController.SAFE_ACTION:
            result = self.alert_service.safe_threat(action, threat_data)
        elif action == IDSController.IGNORE_ACTION:
            result = self.alert_service.ignore_threat(action, threat_data)
        elif action == IDSController.LIMIT_ACTION:
            result = self.alert_service.limit_threat(action, threat_data)
        elif action == IDSController.BLOCK_ACTION:
            result = self.alert_service.block_threat(action, threat_data)
        else:
           result = IDSController.INVALID_ACTION
        return result

    def get_threats(self, limit: Optional[int] = None, offset: Optional[int] = None, priority: Optional[int] = None) -> List[Dict]:
       """Retrieves distinct threats from DataManager."""
       try:
           threats = self.data_manager.get_threats(limit, offset, priority)
           return threats
       except Exception as e:
           logger.error(f"Error fetching threats: {e}", exc_info=True)
           return []

    def get_total_threats(self) -> int:
        """Retrieves total number of threats from DataManager."""
        threats = self.data_manager.get_threats()
        return len(threats)