import os
import sqlite3
from models.alert import Alert
from utils.alert_reader import AlertReader
from config.settings import Settings
import logging
import json

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, root):
        self.root = root
        self.db_path = os.path.join("data", "ids_data.db") 
        self._config = self._load_config()
        
        self.update_interval = self._config.get("update_interval", 60) * 1000  # milliseconds
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row # dùng để đọc dữ liệu bằng key
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            # print(f"Lỗi kết nối database: {e}")
            logger.error(f"Lỗi kết nối database: {e}", exc_info=True)
            self.conn = None
            self.cursor = None
            
        self.alert_reader = AlertReader(Settings.LOG_PATH)
        self.max_alerts = self._config.get("max_alerts", 5000)
        self.alerts = []
        self.create_tables()
        self.init_db_from_file()
        self.last_update_time = 0  # Thờai điểm cập nhật lần cuối (timestamp)
        
    def update_alerts_from_file(self):
        """Cập nhật alert từ file log."""
        try:
            current_time = os.path.getmtime(Settings.LOG_PATH) # lấy thời gian cập nhật cuối
            if current_time > self.last_update_time:
                # new_alerts = self.alert_reader.read_alerts(self.last_update_time)
                new_alerts = self.alert_reader.read_alerts(last_update_time=self.last_update_time)
                if new_alerts:
                    self.insert_alerts(new_alerts)
                    self.last_update_time = current_time # update last_update_time sau khi insert alert thành công
                    logger.info(f"Đã cập nhật {len(new_alerts)} alerts từ file log. ")
        except FileNotFoundError:
            logger.error(f"File {Settings.LOG_PATH} không tồn tại.", exc_info=True)
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật alerts từ file: {e}", exc_info=True)
        
        self.root.after(self.update_interval, self.update_alerts_from_file)
        
    def _load_config(self):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Lỗi đọc config: {e}. Sử dụng config mặc định.")
            logger.error(f"Lỗi đọc config: {e}. Sử dụng config mặc định.", exc_info=True)
            return {}
        
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
                    priority INTEGER,
                    occur INTEGER,
                    action_taken INTEGER,
                    UNIQUE (timestamp, src_IP, dst_IP, protocol)
                )             
            """)
            print("Tạo bảng thành công")
            self.create_indices()
            self.conn.commit() #
            logger.info("Tạo bảng thành công")
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi tạo bảng: {e}", exc_info=True)
            
    def create_indices(self):
        """Tạo index cho database."""
        try:
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_src_ip ON alerts (src_IP)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_dst_ip ON alerts (dst_IP)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_protocol ON alerts (protocol)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON alerts (timestamp)")
            self.conn.commit()
            logger.info("Tạo index thành công")
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi tạo index: {e}", exc_info=True)

        
            
    def init_db_from_file(self):
        """Khởi tạo database từ file."""
        try:
            alerts = self.alert_reader.read_alerts()
            if alerts: # Nếu đọc được alert từ file
                self.insert_alerts(alerts) # chèn vào db
                self.last_update_time = os.path.getmtime(Settings.LOG_PATH) # cập nhật thời gian update cuối

            logger.info("Khởi tạo database từ file thành công.")
        except FileNotFoundError:
            logger.error(f"File {Settings.LOG_PATH} không tồn tại. Bỏ qua khởi tạo.", exc_info=True)
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo database từ file: {e}", exc_info=True)
            
    def insert_alerts(self, alerts):
        """Thêm danh sách alert vào db và cập nhật cache."""
        try:
            self.cursor.executemany("""
                INSERT OR IGNORE INTO alerts (timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, priority, occur, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [alert.to_tuple() for alert in alerts])
            self.conn.commit()

            # Cập nhật cache (giới hạn số lượng alert)
            if len(self.alerts) + len(alerts) > self.max_alerts:
                self.alerts = self.alerts[-(self.max_alerts - len(alerts)):] + alerts
            else:
                self.alerts.extend(alerts)

            logger.info(f"Đã thêm {len(alerts)} alerts vào database.")
            
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi chèn alerts: {e}", exc_info=True)
        
    def get_alerts(self, filter_criteria=None, limit=None, offset=None):
        
        logger.debug(f"get_alerts called with filter_criteria: {filter_criteria}, limit: {limit}, offset: {offset}") # logging debug
        # thêm đoạn code này để get_alert nhanh hơn
        if filter_criteria == None: # không cần lọc
            if limit and offset: # có phân trang
                return self.alerts[offset:offset+limit]  # Trả về một phần của cache
            else:
                return self.alerts[:]
        print("filter_criteria: ", filter_criteria)
        # Lọc alerts theo filter_criteria
        filtered_alerts = []
        for alert in self.alerts:
            match = True
            for key, value in filter_criteria.items():
                if getattr(alert, key) != value: # so sánh giá trị của thuộc tính alert
                    match = False
                    break
            if match:
                filtered_alerts.append(alert)
                
            if limit and offset: # Có phân trang
                return filtered_alerts[offset:offset+limit]
            else:
                return filtered_alerts

        return filtered_alerts
        
    def update_alert(self, alert):
        """Cập nhật alert trong database."""
        try:
            self.cursor.execute("""
                UPDATE alerts SET action_taken = ? WHERE id = ?
            """, (alert.action_taken, alert.id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi cập nhật alert: {e}", exc_info=True)
            
        for i, cached_alert in enumerate(self.alerts):
            if cached_alert.id == alert.id:
                self.alerts[i] = alert # update alert trong cache
                break
    
    def get_threats(self, limit=None, offset=None, min_priority = 3):  # Thêm tham số min_priority
        """Lấy danh sách các threat có priority cao từ database (nhóm các alert) và phân trang."""
        try:
            query = """
                SELECT src_IP, dst_IP, protocol, priority, COUNT(*) AS occur, MAX(timestamp) as last_seen
                FROM alerts
                WHERE action_taken = 0 AND priority <= ?
                GROUP BY src_IP, dst_IP, protocol
                ORDER BY priority DESC;

            """
            
            if limit and offset:
                query += f" LIMIT {limit} OFFSET {offset}"

            # Thực thi câu lệnh với điều kiện min_priority
            self.cursor.execute(query, (min_priority,))
            rows = self.cursor.fetchall()
            
            # Trả về danh sách từ điển với thông tin priority
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Lỗi khi lấy threats: {e}", exc_info=True)
            return []

        
    def search_alerts(self, filter_criteria, limit=None, offset=None):  # Thêm limit và offset
        """Tìm kiếm alert theo filter_criteria và phân trang."""
        try:
            where_clause = "WHERE " + " AND ".join([f"{key} LIKE ?" for key in filter_criteria.keys()])
            values = tuple(['%' + value + '%' for value in filter_criteria.values()])
            query = f"SELECT * FROM alerts {where_clause}"
            if limit and offset:
                query += f" LIMIT {limit} OFFSET {offset}" # Thêm limit và offset vào truy vấn
            self.cursor.execute(query, values)
            rows = self.cursor.fetchall()
            return [Alert(**row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"The error when finding alerts: {e}", exc_info=True)
            return []
        
    def __del__(self):
        """Đóng kết nối database khi DataManager bị hủy."""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.commit()  # Commit trước khi đóng
                self.conn.close()
            except sqlite3.Error as e:
                logger.error(f"The error when closing database: {e}", exc_info=True)