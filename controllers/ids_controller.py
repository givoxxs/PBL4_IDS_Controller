from models.data_manager import DataManager
from models.alert import Alert
from services.alert_service import AlertService
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import os

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

    def _apply_pagination(self, page, per_page):
        if page < 1:
            raise ValueError("Page must be 1 or greater.")
        if per_page <= 0:
            raise ValueError("Per_page must be a positive integer.")

        offset = (page - 1) * per_page
        return offset

    def update_alerts_from_file(self):
        return self.data_manager.update_alerts_from_file()

    def get_alerts(self, filter_criteria=None, page=1, per_page=100):
        offset = self._apply_pagination(page, per_page)
        return self.data_manager.get_alerts(filter_criteria, limit=per_page, offset=offset)

    def get_alerts_by_action_taken(self, filter_criteria=None, page=1, per_page=100):
        offset = self._apply_pagination(page, per_page)
        try:
            alerts = self.data_manager.get_alerts_by_action_taken(limit=per_page, offset=offset)
            return alerts
        except Exception as e:
            logger.error(f"Error fetching alerts by action taken: {e}", exc_info=True)
            raise

    def get_total_alerts(self, filter_criteria=None):
        return len(self.data_manager.get_alerts(filter_criteria))

    def _update_alert_action(self, alert, action):
        if IDSController.SUCCESS_MESSAGE in action or action == IDSController.IGNORE_MESSAGE:
            alert.action_taken = 1
            self.data_manager.update_alert(alert)

    async def _async_handle_action(self, alert, action):
        if action == IDSController.SAFE_ACTION:
            result = self.alert_service.safe_threat(alert.to_dict())
        elif action == IDSController.IGNORE_ACTION:
            result = self.alert_service.ignore_threat(alert.to_dict())
        elif action == IDSController.LIMIT_ACTION:
            result = self.alert_service.limit_threat(alert.to_dict())
        elif action == IDSController.BLOCK_ACTION:
            result = self.alert_service.block_threat(alert.to_dict())
        else:
            result = IDSController.INVALID_ACTION
        return result

    def handle_alert_action(self, alert: Alert, action: str):
        try:
            result = asyncio.run(self._async_handle_action(alert, action))
            self._update_alert_action(alert, result)
            return result
        except Exception as e:
            logger.error(f"Error in IDSController.handle_alert_action: {e}", exc_info=True)
            return f"An error occurred: {e}"

    def get_threats(self, limit=None, offset=None, priority=None):
        try:
            threats = self.data_manager.get_threats(limit, offset, priority)
            return threats
        except Exception as e:
            logger.error(f"Error fetching threats: {e}", exc_info=True)
            return []

    def get_total_threats(self):
        threats = self.data_manager.get_threats()
        return len(threats)

    def _process_threat_action(self, threat_data, action):
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
        return result

    def handle_threat_action(self, threat_data: dict, action: str):
        try:
            result = self._process_threat_action(threat_data, action)
            filter_criteria = {
                "src_IP": threat_data['src_IP'],
                "dst_IP": threat_data['dst_IP'],
                "protocol": threat_data['protocol'],
            }
            alerts = self.data_manager.get_alerts(filter_criteria=filter_criteria)

            batch_size = 1000
            for batch in self._batch_process(alerts, batch_size):
                futures = [
                    self.thread_pool_executor.submit(self._update_alert_action, alert, result)
                    for alert in batch
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error updating alert: {e}", exc_info=True)
            return result

        except Exception as e:
            logger.error(f"Error in IDSController.handle_threat_action: {e}", exc_info=True)
            return f"An error occurred: {e}"

    def _batch_process(self, data, batch_size):
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    def search_alerts(self, search_term, page=1, per_page=100):
        filter_criteria = {'msg': f"%{search_term}%"}
        offset = self._apply_pagination(page, per_page)
        return self.data_manager.search_alerts(filter_criteria, limit=per_page, offset=offset)

    def get_total_search_result(self, search_term):
        filter_criteria = {'msg': f"%{search_term}%"}
        return len(self.data_manager.search_alerts(filter_criteria))

    def collect_data_for_dashboard(self):
        logger.info("Collecting data for dashboard")
        alerts = self.get_alerts()
        return alerts

    def get_all_protocols(self):
        all_alerts = self.data_manager.get_alerts()
        protocols = set(alert.protocol for alert in all_alerts)
        return list(protocols)

    def load_config(self, config_path="dashboard_config.json"):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading config: {e}")

    def save_config(self, config_path="dashboard_config.json"):
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
