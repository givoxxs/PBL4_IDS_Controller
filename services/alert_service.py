from models.alert import Alert
from utils.file_modifier import FileModifier
from models.data_manager import DataManager

class AlertService:
    def __init__(self, root):
        self.root = root
        self.file_modifier = FileModifier()
        self.data_manager = DataManager(root)
        
    def safe_alert(self, alert: Alert):
        new_rule = f"pass {alert.protocol.lower()} {alert.src_IP} any -> {alert.dst_IP} any (msg:\"Allowed by user\"; sid:{self.file_modifier.get_sid()};)"
        result = self.file_modifier.add_local_rule(new_rule)
        if "successfully" in result:
            self.file_modifier.update_sid(self.file_modifier.get_sid() + 1)
            self.file_modifier.reload_snort()
            
        alert.action_taken = True
        self.data_manager.update_alert(alert)
        return result
    
    def ignore_alert(self, alert: Alert):
        alert.action_taken = True
        self.data_manager.update_alert(alert)
        return "Ignored"

    def limit_alert(self, alert: Alert):
        command = f"ufw limit proto {alert.protocol.lower()} from {alert.src_IP} to {alert.dst_IP}"
        result = self.file_modifier.execute_ufw_command(command)
    
        self.file_modifier.reload_ufw()
        alert.action_taken = True
        self.data_manager.update_alert(alert)
        
        return result

    def block_alert(self, alert: Alert):
        command = f"ufw deny proto {alert.protocol.lower()} from {alert.src_IP} to {alert.dst_IP}"
        result = self.file_modifier.execute_ufw_command(command)
        
        self.file_modifier.reload_ufw()
        alert.action_taken = True
        self.data_manager.update_alert(alert)
        return result
    
    def safe_threat(self, threat_data: dict):
        sid = self.file_modifier.get_sid()
        new_rule = f"pass {threat_data['protocol'].lower()} {threat_data['src_IP']} any -> {threat_data['dst_IP']} any (msg:\"Allowed by user\"; sid:{sid};)"
        result = self.file_modifier.add_local_rule(new_rule)
        
        print(result)
        print("src_IP: ", threat_data['src_IP'])
        print("dst_IP: ", threat_data['dst_IP'])
        print("protocol: ", threat_data['protocol'])
        filter_criteria = {
            "src_IP": threat_data['src_IP'],
            "dst_IP": threat_data['dst_IP'],
            "protocol": threat_data['protocol']
        }
        alerts = self.data_manager.get_alerts(filter_criteria)
        for alert in alerts:
            alert.action_taken = True
            self.data_manager.update_alert(alert)
        return result

    def ignore_threat(self, threat_data: dict):
        filter_criteria = {
            "src_IP": threat_data['src_IP'],
            "dst_IP": threat_data['dst_IP'],
            "protocol": threat_data['protocol']
        }
        alerts = self.data_manager.get_alerts(filter_criteria)
        for alert in alerts:
            alert.action_taken = True
            self.data_manager.update_alert(alert)
        
        return "Ignored"

    def limit_threat(self, threat_data: dict):
        command = f"ufw limit proto {threat_data['protocol'].lower()} from {threat_data['src_IP']} to {threat_data['dst_IP']}"
        result = self.file_modifier.execute_ufw_command(command)
        self.file_modifier.reload_ufw()
        
        filter_criteria = {
            "src_IP": threat_data['src_IP'],
            "dst_IP": threat_data['dst_IP'],
            "protocol": threat_data['protocol']
        }
        alerts = self.data_manager.get_alerts(filter_criteria)
        for alert in alerts:
            alert.action_taken = True
            self.data_manager.update_alert(alert)
        
        return result

    def block_threat(self, threat_data: dict):
        command = f"ufw deny proto {threat_data['protocol'].lower()} from {threat_data['src_IP']} to {threat_data['dst_IP']}"
        result = self.file_modifier.execute_ufw_command(command)
        self.file_modifier.reload_ufw()
        
        filter_criteria = {
            "src_IP": threat_data['src_IP'],
            "dst_IP": threat_data['dst_IP'],
            "protocol": threat_data['protocol']
        }
        alerts = self.data_manager.get_alerts(filter_criteria)
        for alert in alerts:
            alert.action_taken = True
            self.data_manager.update_alert(alert)
        return result