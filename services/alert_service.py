from models.alert import Alert
from utils.file_modifier import FileModifier
from models.data_manager import DataManager

class AlertService:
    SUCCESS_MESSAGE = "successfully"
    IGNORE_MESSAGE = "Ignored"
    
    def __init__(self, root):
        self.root = root
        self.file_modifier = FileModifier()
        self.data_manager = DataManager(root)
    
    def _handle_alert_action(self, action, alert: Alert, action_result: str = None):
        """
        Helper function to update an alert's action status and update the db
        """
        alert.action_taken = 1
        alert.action = action.title()
        self.data_manager.update_alert(alert)
        
        return action_result if action_result else AlertService.SUCCESS_MESSAGE

    def _build_snort_rule(self, protocol, src_ip, dst_ip, sid):
        """
        Helper function to build the snort rule
        """
        return f"pass {protocol.lower()} {src_ip} any -> {dst_ip} any (msg:\"Allowed by user\"; sid:{sid};)"
    
    def _execute_ufw_command(self, command):
        """
        Helper function to execute the ufw command and reload ufw
        """
        result = self.file_modifier.execute_ufw_command(command)
        self.file_modifier.reload_ufw()
        return result

    def safe_alert(self, action, alert: Alert):
        """Adds a snort rule to allow traffic specified in alert."""
        new_rule = self._build_snort_rule(alert.protocol, alert.src_IP, alert.dst_IP, self.file_modifier.get_sid())
        result = self.file_modifier.add_local_rule(new_rule)

        if AlertService.SUCCESS_MESSAGE in result:
            self.file_modifier.update_sid(self.file_modifier.get_sid() + 1)
            self.file_modifier.reload_snort()
        
        return self._handle_alert_action(action, alert, result)
        
    def ignore_alert(self, action, alert: Alert):
        """Marks an alert as ignored without taking any specific action."""
        return self._handle_alert_action(action, alert, AlertService.IGNORE_MESSAGE)

    def limit_alert(self, action, alert: Alert):
        """Limits traffic specified in alert using UFW."""
        command = f"sudo ufw limit proto {alert.protocol.lower()} from {alert.src_IP} to {alert.dst_IP}"
        result = self._execute_ufw_command(command)
        return self._handle_alert_action(action, alert, result)
    
    def block_alert(self, action, alert: Alert):
        """Blocks traffic specified in alert using UFW."""
        command = f"sudo ufw deny proto {alert.protocol.lower()} from {alert.src_IP} to {alert.dst_IP}"
        result = self._execute_ufw_command(command)
        return self._handle_alert_action(action, alert, result)
    
    def safe_threat(self, action, threat_data: dict):
       """Adds a snort rule to allow traffic specified in threat_data."""
       sid = self.file_modifier.get_sid()
       new_rule = self._build_snort_rule(threat_data['protocol'], threat_data['src_IP'], threat_data['dst_IP'], sid)
       result = self.file_modifier.add_local_rule(new_rule)

       if AlertService.SUCCESS_MESSAGE in result:
           self.file_modifier.update_sid(self.file_modifier.get_sid() + 1)
           self.file_modifier.reload_snort()
       
       self._mark_threat_alerts_actioned(action, threat_data) # Mark alerts as handled
       return result
    
    def ignore_threat(self, action,  threat_data: dict):
        """Marks all alerts related to the threat as ignored."""
        
        self._mark_threat_alerts_actioned(action, threat_data, AlertService.IGNORE_MESSAGE)
        
        return AlertService.IGNORE_MESSAGE
    
    def limit_threat(self, action, threat_data: dict):
       """Limits traffic related to the threat using UFW."""
       command = f"sudo ufw limit proto {threat_data['protocol'].lower()} from {threat_data['src_IP']} to {threat_data['dst_IP']}"
       result = self._execute_ufw_command(command)

       self._mark_threat_alerts_actioned(action, threat_data, result)
        
       return result

    def block_threat(self, action, threat_data: dict):
        """Blocks traffic related to the threat using UFW."""
        command = f"sudo ufw deny proto {threat_data['protocol'].lower()} from {threat_data['src_IP']} to {threat_data['dst_IP']}"
        result = self._execute_ufw_command(command)
        self._mark_threat_alerts_actioned(action,threat_data, result)
        return result

    def _mark_threat_alerts_actioned(self, action, threat_data: dict, action_result:str=None):
        """
        Helper function to mark all alerts related to a threat as actioned
        """
        filter_criteria = {
            "src_IP": threat_data['src_IP'],
            "dst_IP": threat_data['dst_IP'],
            "protocol": threat_data['protocol']
        }
        alerts = self.data_manager.get_alerts(filter_criteria)
        for alert in alerts:
            self._handle_alert_action(action, alert, action_result)