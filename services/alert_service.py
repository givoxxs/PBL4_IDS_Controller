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
    
    def _handle_alert_action(self, alert: Alert, action_result: str = None):
        """
        Helper function to update an alert's action status and update the db
        """
        alert.action_taken = True
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
        print("COMMAnD - ", command)
        self.file_modifier.reload_ufw()
        return result

    def _execute_iptables_command(self, command):
        """
        Helper function to execute the iptables command and save the rules
        """
        result = self.file_modifier.execute_iptables_command(command)
        print("COMMAnD iptables - ", command)
        # self.file_modifier.save_iptables_rules()
        return result

    def safe_alert(self, alert: Alert):
        """Adds a snort rule to allow traffic specified in alert."""
        new_rule = self._build_snort_rule(alert.protocol, alert.src_IP, alert.dst_IP, self.file_modifier.get_sid())
        result = self.file_modifier.add_local_rule(new_rule)

        if AlertService.SUCCESS_MESSAGE in result:
            self.file_modifier.update_sid(self.file_modifier.get_sid() + 1)
            self.file_modifier.reload_snort()
        
        return self._handle_alert_action(alert, result)
        
    def ignore_alert(self, alert: Alert):
        """Marks an alert as ignored without taking any specific action."""
        return self._handle_alert_action(alert, AlertService.IGNORE_MESSAGE)

    def limit_alert(self, alert: Alert):
        """Limits traffic specified in alert using UFW or iptables."""
        if alert.protocol.lower() == 'icmp':
            # For ICMP, use iptables to specify the type (e.g., echo-request)
            command = f"sudo iptables -A INPUT -s {alert.src_IP} -d {alert.dst_IP} -p icmp --icmp-type echo-request -j DROP"
        elif alert.protocol.lower() in ['tcp', 'udp']:
            # For TCP and UDP, use ufw or iptables directly
            command = f"sudo ufw limit proto {alert.protocol.lower()} from {alert.src_IP} to {alert.dst_IP}"
        elif alert.protocol.lower() == 'ip':
            # For IP, limit the traffic from src_ip to dst_ip (all protocols)
            command = f"sudo iptables -A INPUT -s {alert.src_IP} -d {alert.dst_IP} -j DROP"
        else:
            return "Unsupported protocol"
        
        if alert.protocol.lower() in ['ip', 'icmp']:
            result = self._execute_iptables_command(command)  # Execute iptables or ufw command
        else:
            result = self._execute_ufw_command(command)
        return self._handle_alert_action(alert, result)
    
    def block_alert(self, alert: Alert):
        print("BLOCK THREAT - protocol: ", alert.protocol.lower)
        """Blocks traffic specified in alert using UFW or iptables."""
        if alert.protocol.lower() == 'icmp':
            # For ICMP, use iptables to specify the type (e.g., echo-request)
            command = f"sudo iptables -A INPUT -s {alert.src_IP} -d {alert.dst_IP} -p icmp --icmp-type echo-request -j DROP"
        elif alert.protocol.lower() in ['tcp', 'udp']:
            # For TCP and UDP, use ufw or iptables directly
            command = f"sudo ufw deny proto {alert.protocol.lower()} from {alert.src_IP} to {alert.dst_IP}"
        elif alert.protocol.lower() == 'ip':
            # For IP, block the traffic from src_ip to dst_ip (all protocols)
            command = f"sudo iptables -A INPUT -s {alert.src_IP} -d {alert.dst_IP} -j DROP"
        else:
            return "Unsupported protocol"
        
        # result = self._execute_iptables_command(command)  # Execute iptables or ufw command
        if alert.protocol.lower() in ['ip', 'icmp']:
            result = self._execute_iptables_command(command)  # Execute iptables or ufw command
        else:
            result = self._execute_ufw_command(command)
        return self._handle_alert_action(alert, result)
    
    def safe_threat(self, threat_data: dict):
        """Adds a snort rule to allow traffic specified in threat_data."""
        sid = self.file_modifier.get_sid()
        new_rule = self._build_snort_rule(threat_data['protocol'], threat_data['src_IP'], threat_data['dst_IP'], sid)
        result = self.file_modifier.add_local_rule(new_rule)

        if AlertService.SUCCESS_MESSAGE in result:
            self.file_modifier.update_sid(self.file_modifier.get_sid() + 1)
            self.file_modifier.reload_snort()
        
        self._mark_threat_alerts_actioned(threat_data)  # Mark alerts as handled
        return result
    
    def ignore_threat(self, threat_data: dict):
        """Marks all alerts related to the threat as ignored."""
        
        self._mark_threat_alerts_actioned(threat_data, AlertService.IGNORE_MESSAGE)
        
        return AlertService.IGNORE_MESSAGE
    
    def limit_threat(self, threat_data: dict):
        """Limits traffic related to the threat using UFW or iptables."""
        if threat_data['protocol'].lower() == 'icmp':
            # For ICMP, use iptables to specify the type (e.g., echo-request)
            command = f"sudo iptables -A INPUT -s {threat_data['src_IP']} -d {threat_data['dst_IP']} -p icmp --icmp-type echo-request -j DROP"
        elif threat_data['protocol'].lower() in ['tcp', 'udp']:
            # For TCP and UDP, use ufw or iptables directly
            command = f"sudo ufw limit proto {threat_data['protocol'].lower()} from {threat_data['src_IP']} to {threat_data['dst_IP']}"
        elif threat_data['protocol'].lower() == 'ip':
            # For IP, limit the traffic from src_ip to dst_ip (all protocols)
            command = f"sudo iptables -A INPUT -s {threat_data['src_IP']} -d {threat_data['dst_IP']} -j DROP"
        else:
            return "Unsupported protocol"
        
        # result = self._execute_iptables_command(command)  # Execute iptables or ufw command
        if alert.protocol.lower() in ['ip', 'icmp']:
            result = self._execute_iptables_command(command)  # Execute iptables or ufw command
        else:
            result = self._execute_ufw_command(command)
        self._mark_threat_alerts_actioned(threat_data, result)
        
        return result

    def block_threat(self, threat_data: dict):
        """Blocks traffic related to the threat using UFW or iptables."""
        if threat_data['protocol'].lower() == 'icmp':
            # For ICMP, use iptables to specify the type (e.g., echo-request)
            command = f"sudo iptables -A INPUT -s {threat_data['src_IP']} -d {threat_data['dst_IP']} -p icmp --icmp-type echo-request -j DROP"
        elif threat_data['protocol'].lower() in ['tcp', 'udp']:
            # For TCP and UDP, use ufw or iptables directly
            command = f"sudo ufw deny proto {threat_data['protocol'].lower()} from {threat_data['src_IP']} to {threat_data['dst_IP']}"
        elif threat_data['protocol'].lower() == 'ip':
            # For IP, block the traffic from src_ip to dst_ip (all protocols)
            command = f"sudo iptables -A INPUT -s {threat_data['src_IP']} -d {threat_data['dst_IP']} -j DROP"
        else:
            return "Unsupported protocol"
        
        # result = self._execute_iptables_command(command)  # Execute iptables or ufw command
        if alert.protocol.lower() in ['ip', 'icmp']:
            result = self._execute_iptables_command(command)  # Execute iptables or ufw command
        else:
            result = self._execute_ufw_command(command)
        self._mark_threat_alerts_actioned(threat_data, result)
        return result

    def _mark_threat_alerts_actioned(self, threat_data: dict, action_result:str=None):
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
            self._handle_alert_action(alert, action_result)
