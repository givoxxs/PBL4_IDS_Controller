# import modify_files as mf
from utils.file_modifier import FileModifier as mf

class Alert:
    """
    Class Alert represents a specific suspicious traffic,
    which can be blocked with a Snort or firewall rule.
    """
    def __init__(self, timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, occur=1, action_taken=False, id=None):
        self.timestamp = timestamp
        self.action = action
        self.protocol = protocol
        self.gid = gid
        self.sid = sid
        self.rev = rev
        self.msg = msg
        self.service = service
        self.src_IP = src_IP
        self.src_Port = src_Port
        self.dst_IP = dst_IP
        self.dst_Port = dst_Port
        self.occur = occur
        self.action_taken = action_taken
        self.id = id

    def __eq__(self, other):
        return (
            isinstance(other, Alert) and
            self.src_IP == other.src_IP and
            self.dst_IP == other.dst_IP and
            self.protocol == other.protocol
        )
    
    @staticmethod # Thêm @staticmethod
    def get_columns():
       """Trả về danh sách tên cột."""
       return ["timestamp", "action", "protocol", "gid", "sid", "rev", "msg", "service", "src_IP", "src_Port", "dst_IP", "dst_Port", "occur", "action_taken"]

    def to_tuple(self):
        """
        Converts the Alert object to a tuple for easier insertion into the Treeview.
        """
        return (
            self.timestamp, self.action, self.protocol, self.gid, self.sid,
            self.rev, self.msg, self.service, self.src_IP, self.src_Port,
            self.dst_IP, self.dst_Port, self.occur, self.action_taken
        )
        
    def to_dict(self):
        """
        Converts the Alert object to a dictionary for easier insertion into the Treeview.
        """
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "protocol": self.protocol,
            "gid": self.gid,
            "sid": self.sid,
            "rev": self.rev,
            "msg": self.msg,
            "service": self.service,
            "src_IP": self.src_IP,
            "src_Port": self.src_Port,
            "dst_IP": self.dst_IP,
            "dst_Port": self.dst_Port,
            "occur": self.occur,
            "action_taken": self.action_taken,
        }

    def to_csv_form(self):
        return f"{self.src_IP},{self.dst_IP},{self.protocol},{self.occur},{self.action_taken}"