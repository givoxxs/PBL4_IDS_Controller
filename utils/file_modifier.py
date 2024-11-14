import json
import os
from config.settings import Settings
import subprocess

class FileModifier:
    def __init__(self, rules_path = Settings.RULE_PATH, config_file="config.json"):
        self.rules_path = rules_path
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self):
        """Load config từ file JSON. Trả về dictionary hoặc dictionary rỗng nếu có lỗi."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Lỗi đọc config: {e}. Sử dụng config mặc định.")
            return {}  # Trả về dictionary rỗng nếu có lỗi

    def add_local_rule(self, new_rule):
        """Thêm rule vào file local.rules."""
        sid = self.get_sid()
        new_rule = new_rule.replace("sid:{}", f"sid:{sid};")
        try:
            with open(self.rules_path, 'a') as file:
                file.write(new_rule + '\n')
            
            self.update_sid(sid + 1)
            return "Rule added successfully"
        except (PermissionError, OSError) as e:  # Bắt thêm OSError
            return f"Error adding rule: {e}"
        except Exception as e:
            return f"Error occurred: {str(e)}"
    
    def get_sid(self):
        """Lấy sid từ config."""
        return self._config.get('sid', 10000001)
        
    def update_sid(self, new_sid):
        """Cập nhật sid vào config."""
        self._config['sid'] = new_sid
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
            return "SID updated successfully"
        except Exception as e:
            return f"Error occurred: {str(e)}"
    
    def reload_ufw(self):        
        """Reload UFW (Ubuntu)."""
        try:
            result = subprocess.run(['ufw', 'disable'], capture_output=True, text=True, check=True) # check=True để raise exception nếu lỗi
            print(result.stdout) # In ra output nếu cần
            result = subprocess.run(['ufw', 'enable'], capture_output=True, text=True, check=True)
            print(result.stdout)
            return "UFW reloaded successfully"
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi reload UFW: {e}")
            return f"Error reloading UFW: {e}"
        
    def reload_snort(self, service="snort3-nids"):
        """Reload Snort (Ubuntu)."""
        try:
            result_stop = subprocess.run(['systemctl', 'stop', service], capture_output=True, text=True, check=True)
            output_stop = result_stop.stdout.strip() # Lấy output và loại bỏ whitespace thừa
            result_start = subprocess.run(['systemctl', 'start', service], capture_output=True, text=True, check=True)
            output_start = result_start.stdout.strip() # Lấy output và loại bỏ whitespace thừa

            # Kiểm tra output và trả về kết quả tương ứng
            if "Job has already finished" in output_start or "Active: active" in output_start:
                return f"Snort reloaded successfully.\nStop Output: {output_stop}\nStart Output: {output_start}"
            else:
                return f"Error reloading Snort. Start Output: {output_start}" # Trả về output nếu có lỗi
            
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi reload Snort: {e}")
            return f"Error reloading Snort: {e}\nOutput: {e.stdout}\nError: {e.stderr}" # Thông báo lỗi chi tiết
        except Exception as e:
            return f"Error occurred: {str(e)}"
        
    def execute_ufw_command(self, command):
        """Thực thi command UFW (Ubuntu)."""
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            return f"Command executed successfully. Output:\n{output}"
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi thực thi UFW command: {e}")
            return f"Error executing command: {e}\nOutput: {e.stdout}\nError: {e.stderr}"
        except Exception as e:
            return f"Error occurred: {str(e)}"