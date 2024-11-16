import os
import sqlite3
from models.alert import Alert
from utils.alert_reader import AlertReader
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.db_path = os.path.join("data", "ids_data.db") 
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row # dùng để đọc dữ liệu bằng key
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            # print(f"Lỗi kết nối database: {e}")
            logger.error(f"Lỗi kết nối database: {e}", exc_info=True)
            
        self.alert_reader = AlertReader(Settings.LOG_PATH)
        self.create_tables()
        self.init_db_from_file()
        
            
    def __del__(self):
        """Đóng kết nối database khi DataManager bị hủy."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        
    def create_tables(self):
        '''Tạo bảng nếu chưa tồn tại'''
        try:
            self.cursor.execute(""" 
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
            print("Tạo bảng thành công")
            self.conn.commit() #
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi tạo bảng: {e}", exc_info=True)
            
    def init_db_from_file(self):
        '''
        Đọc dữ liệu từ file log và thêm vào db
        '''
        try:
            alerts = self.alert_reader.read_alerts()
            self.insert_alerts(alerts)
            print("Khởi tạo database từ file thành công")
        except FileNotFoundError:
            logger.error(f"File {Settings.LOG_PATH} không tồn tại. Bỏ qua khởi tạo.", exc_info=True)
        except Exception as e:  # Bắt lỗi chung chung khác
            logger.error(f"Lỗi khi khởi tạo database từ file: {e}", exc_info=True)
    
    def insert_alerts(self, alerts):
        '''
        Thêm danh sách alert vào db
        '''
        try:
            self.cursor.executemany("""
                INSERT INTO alerts (timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, occur, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [alert.to_tuple() for alert in alerts])
            print("Thêm alerts vào db thành công")
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi chèn alerts: {e}", exc_info=True)
    
    def get_alerts(self, filter_criteria=None):
        """Lấy danh sách các Alert từ database (có thể lọc)."""
        print("GET_ALERTS")
        print("filter_criteria: ", filter_criteria)
        
        try:
            if filter_criteria:
                where_clause = "WHERE " + " AND ".join([f"{key} = ?" for key in filter_criteria.keys()])
                values = tuple(filter_criteria.values())
                self.cursor.execute(f"SELECT * FROM alerts {where_clause}", values)
            else:
                self.cursor.execute("SELECT * FROM alerts") # Lấy tất cả alert
            rows = self.cursor.fetchall()
            print("Get alerts successfully")
            return [Alert(**row) for row in rows] # Dùng Alert(**row) để khởi tạo list alert
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi lấy alerts: {e}", exc_info=True)
            return []  # Trả về danh sách rỗng nếu có lỗi
        
    def update_alert(self, alert):
        """Cập nhật alert trong database."""
        try:
            self.cursor.execute("""
                UPDATE alerts SET action_taken = ? WHERE id = ?
            """, (alert.action_taken, alert.id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi cập nhật alert: {e}", exc_info=True)
            
    def get_threats(self):
        """Lấy danh sách các threat từ database (nhóm các alert)."""
        try:
            self.cursor.execute("""
                SELECT src_IP, dst_IP, protocol, COUNT(*) AS occur, MAX(timestamp) as last_seen
                FROM alerts
                WHERE action_taken = 0
                GROUP BY src_IP, dst_IP, protocol
            """)
            rows = self.cursor.fetchall()
            print("Get threats successfully")
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi lấy threats: {e}", exc_info=True)
            return []
        
    def search_alerts(self, filter_criteria):
        """Tìm kiếm alert theo filter_criteria."""
        try:
            where_clause = "WHERE " + " AND ".join([f"{key} LIKE ?" for key in filter_criteria.keys()])
            values = tuple(['%' + value + '%' for value in filter_criteria.values()])
            self.cursor.execute(f"SELECT * FROM alerts {where_clause}", values)
            rows = self.cursor.fetchall()
            return [Alert(**row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi tìm kiếm alerts: {e}", exc_info=True)
            return []