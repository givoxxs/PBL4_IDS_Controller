import os
import sqlite3
from models.alert import Alert
from utils.alert_reader import AlertReader
from config.settings import Settings
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Custom exception for database connection failures.""" 
    pass

class DataManager:
    def __init__(self, root):
        self.root = root
        self.db_path = os.path.join("data", "ids_data.db")
        self._config = self._load_config()

        self.update_interval = self._config.get("update_interval", 60) * 1000  # milliseconds

        try:
            # Set the database to allow multi-threaded access and use busy_timeout to handle locked DB issues
            self.conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode for better concurrency
            self.cursor.execute("PRAGMA busy_timeout=5000;")  # Set busy timeout to 5 seconds
        except sqlite3.Error as e:
            logger.error(f"Lỗi kết nối database: {e}", exc_info=True)
            self.conn = None
            self.cursor = None

        self.alert_reader = AlertReader(Settings.LOG_PATH)
        self.max_alerts = self._config.get("max_alerts", 5000)
        self.alerts = []
        self.create_tables()
        self.init_db_from_file()
        self.last_update_time = 0

    def _update_alerts_from_file_callback(self):
        """This method is used as a callback that the tkinter `after` will call"""
        self.update_alerts_from_file() # call the original method

    def update_alerts_from_file(self):
        """Cập nhật alert từ file log."""
        try:
            current_time = os.path.getmtime(Settings.LOG_PATH)
            if current_time > self.last_update_time:
                new_alerts = self.alert_reader.read_alerts(last_update_time=self.last_update_time)
                if new_alerts:
                    self.insert_alerts(new_alerts)
                    self.last_update_time = current_time
                    logger.info(f"Đã cập nhật {len(new_alerts)} alerts từ file log.")
        except FileNotFoundError:
            logger.error(f"File {Settings.LOG_PATH} không tồn tại.", exc_info=True)
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật alerts từ file: {e}", exc_info=True)

    def _load_config(self):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Lỗi đọc config: {e}. Sử dụng config mặc định.")
            logger.error(f"Lỗi đọc config: {e}. Sử dụng config mặc định.", exc_info=True)
            return {}

    def create_tables(self):
        """Tạo bảng nếu chưa tồn tại."""
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
            self.conn.commit()
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
            if alerts:
                self.insert_alerts(alerts)
                self.last_update_time = os.path.getmtime(Settings.LOG_PATH)
            logger.info("Khởi tạo database từ file thành công.")
        except FileNotFoundError:
            logger.error(f"File {Settings.LOG_PATH} không tồn tại. Bỏ qua khởi tạo.", exc_info=True)
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo database từ file: {e}", exc_info=True)

    def insert_alerts(self, alerts):
        """Insert alert into the database with proper transaction handling."""
        try:
            # Start an exclusive transaction
            self.conn.execute("BEGIN EXCLUSIVE TRANSACTION;")
            self.cursor.executemany(""" 
                INSERT OR IGNORE INTO alerts (timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, priority, occur, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [alert.to_tuple() for alert in alerts])
            self.conn.commit()  # Commit changes
            logger.info(f"Đã thêm {len(alerts)} alerts vào database.")
        except sqlite3.OperationalError as e:
            logger.error(f"Lỗi khi chèn alerts: {e}", exc_info=True)
            self.conn.rollback()  # Rollback in case of error
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi chèn alerts: {e}", exc_info=True)
            self.conn.rollback()  # Rollback in case of error


    def get_alerts(self, filter_criteria=None, limit=None, offset=None):
        """Retrieves alerts from the data storage, applying filters and pagination.""" 
        query = "SELECT * FROM alerts"
        where_clauses = []

        if filter_criteria:
            for key, value in filter_criteria.items():
                if isinstance(value, str):
                    where_clauses.append(f"{key} = '{value}'")
                else:
                    where_clauses.append(f"{key} = {value}")
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error when getting alerts: {e}", exc_info=True)
            return []

        column_names = [desc[0] for desc in self.cursor.description]
        id_index = column_names.index("id")  if "id" in column_names else -1

        alerts = []
        for row in rows:
            if id_index >= 0:
                row_without_id = list(row)
                row_without_id.pop(id_index)
                alerts.append(Alert(*row_without_id, last_seen=None))
            else:
                alerts.append(Alert(*row, last_seen=None))

        return alerts

    def update_alert(self, alert):
        """Cập nhật alert trong database.""" 
        try:
            self.cursor.execute("""
            UPDATE alerts 
            SET action_taken = ?, action = ? 
            WHERE src_IP = ? AND dst_IP = ? AND protocol = ?
            """, (alert.action_taken, alert.action, alert.src_IP, alert.dst_IP, alert.protocol))
            self.conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Lỗi khi cập nhật alert: {e}", exc_info=True)

        for i, cached_alert in enumerate(self.alerts):
            if cached_alert.id == alert.id:
                self.alerts[i] = alert
                break

    def get_threats(self, limit=None, offset=None, priority=3):
        """Gets all threats using one SQL query and using limit and offset"""
        try:
                query = """
                    SELECT src_IP, dst_IP, protocol, action_taken, priority, COUNT(*) AS occur, MAX(timestamp) as last_seen
                    FROM alerts
                    WHERE action_taken = 0
                """
                if priority is not None:
                    query += f" AND priority <= {priority}"
                    query += """
                        GROUP BY src_IP, dst_IP, protocol
                        ORDER BY priority DESC, occur DESC
                    """
                    if limit is not None and offset is not None:
                        if not isinstance(limit, int) or not isinstance(offset, int):
                            raise TypeError("Limit and offset must be integers when both are provided.")
                        query += f" LIMIT {limit} OFFSET {offset}"

                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
                logger.error(f"Lỗi khi lấy threats: {e}", exc_info=True)
                return []

    def get_alerts_by_action_taken(self, limit=None, offset=None):
        """Lấy tất cả các alert đã xử lý theo action_taken.""" 
        try:
            if limit is not None and (not isinstance(limit, int) or limit <= 0):
                raise ValueError("Limit must be a positive integer.")
            if offset is not None and (not isinstance(offset, int) or offset < 0):
                raise ValueError("Offset must be a non-negative integer.")

            query = """
                SELECT *, COUNT(*) AS occur, MAX(timestamp) AS last_seen
                FROM alerts
                WHERE action_taken = 1
                GROUP BY src_IP, dst_IP, protocol, action_taken, priority
            """ 

            if limit is not None and offset is not None:
                query += f" LIMIT {limit} OFFSET {offset}"

            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            alerts = [Alert(timestamp=row['timestamp'], action=row['action'], protocol=row['protocol'], 
                gid=row['gid'], sid=row['sid'], rev=row['rev'], msg=row['msg'], service=row['service'], 
                src_IP=row['src_IP'], src_Port=row['src_Port'], dst_IP=row['dst_IP'], dst_Port=row['dst_Port'], 
                priority=row['priority'], occur=row['occur'], action_taken=row['action_taken'], last_seen=row['last_seen'])
                for row in rows]
            return alerts

        except sqlite3.Error as e:
            logger.error(f"Lỗi khi lấy alerts đã xử lý: {e}", exc_info=True)
            print(f"SQLite Error: {e}")
            return []
    
    def __del__(self):
        """Đóng kết nối database khi DataManager bị hủy.""" 
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.commit()
                self.conn.close()
            except sqlite3.Error as e:
                logger.error(f"The error when closing database: {e}", exc_info=True)
