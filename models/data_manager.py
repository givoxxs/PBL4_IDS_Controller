import os
import sqlite3
from models.alert import Alert
from utils.alert_reader import AlertReader
from config.settings import Settings

class DataManager:
    def __init__(self):
        self.db_path = os.path.join("data", "ids_data.db") 
        self.alert_reader = AlertReader(Settings.LOG_PATH)
        self.create_tables()
        self.init_db_from_file()
        
    def create_tables(self):
        '''
        Tạo bảng nếu chưa tồn tại
        '''
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(""" 
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action TEXT,
                    protocol TEXT,
                    gid INTEGER,
                    sid INTEGER,
                    rev INTEGER,
                    msg TEXT,
                    service TEXT,
                    src_IP TEXT,
                    src_Port INTEGER,
                    dst_IP TEXT,
                    dst_Port INTEGER,
                    occur INTEGER,
                    action_taken INTEGER
                )             
            """)
    def init_db_from_file(self):
        '''
        Đọc dữ liệu từ file log và thêm vào db
        '''
        try:
            alerts = self.alert_reader.read_alerts()
            self.insert_alerts(alerts)
        except FileNotFoundError:
            print(f"File {Settings.LOG_PATH} không tồn tại. Bỏ qua khởi tạo.")
        except Exception as e:  # Bắt lỗi chung chung khác
            print(f"Lỗi khi khởi tạo database từ file: {e}")
    
    def insert_alerts(self, alerts):
        '''
        Thêm danh sách alert vào db
        '''
        with sqlite3.connect(self.db_path) as conn:
            for alert in alerts:
                conn.execute("""
                    INSERT INTO alerts (
                        timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, occur, action_taken
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, alert.to_tuple())
    
    def get_alerts(self, filter_criteria=None):
        """Lấy danh sách các Alert từ database (có thể lọc)."""
        print("GET_ALERTS")
        print("filter_criteria: ", filter_criteria)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row # Cho phép truy cập dữ liệu bằng tên cột
            cursor = conn.cursor()
                
            if filter_criteria:
                where_clause = "WHERE " + " AND ".join([f"{key} = ?" for key in filter_criteria.keys()])
                values = tuple(filter_criteria.values())
                cursor.execute(f"SELECT * FROM alerts {where_clause}", values)
            else:
                 cursor.execute("SELECT * FROM alerts")

            rows = cursor.fetchall()
            return [Alert(*row) for row in rows]  # Trả về danh sách Alert
        
        """Lấy danh sách các threat từ database (sử dụng yield)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT src_IP, dst_IP, protocol, COUNT(*) AS occur, MAX(timestamp) as last_seen
                FROM alerts
                WHERE action_taken = 0
                GROUP BY src_IP, dst_IP, protocol
            """)
            for row in cursor:  # Sử dụng yield
                yield dict(row)
        
    def update_alert(self, alert):
        """Cập nhật alert trong database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE alerts SET action_taken = ? WHERE id = ?
            """, (alert.action_taken, alert.id))
            conn.commit()
            
    def get_threats(self):
        """Lấy danh sách các threat từ database (nhóm các alert)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT src_IP, dst_IP, protocol, COUNT(*) AS occur, MAX(timestamp) as last_seen  -- Thêm last_seen
                FROM alerts
                WHERE action_taken = 0
                GROUP BY src_IP, dst_IP, protocol
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
    def search_alerts(self, filter_criteria):
        """Tìm kiếm alert theo filter_criteria."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            where_clause = "WHERE " + " AND ".join([f"{key} LIKE ?" for key in filter_criteria.keys()]) # Dùng LIKE cho tìm kiếm
            values = tuple(['%' + value + '%' for value in filter_criteria.values()]) # Dùng wildcard %

            cursor.execute(f"SELECT * FROM alerts {where_clause}", values)
            rows = cursor.fetchall()
            return [Alert(**row) for row in rows]