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
        


    def _update_alerts_from_file_callback(self):
       """
       This method is used as a callback that the tkinter `after` will call
       """
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
        """Thêm danh sách alert vào db và cập nhật cache."""
        try:
            self.cursor.executemany("""
                INSERT OR IGNORE INTO alerts (timestamp, action, protocol, gid, sid, rev, msg, service, src_IP, src_Port, dst_IP, dst_Port, priority, occur, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [alert.to_tuple() for alert in alerts])
            self.conn.commit()

            logger.info(f"Đã thêm {len(alerts)} alerts vào database.")
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi chèn alerts: {e}", exc_info=True)


    # def get_alerts(self, filter_criteria=None, limit=None, offset=None):
    #     """Lấy danh sách alerts từ cache hoặc với filter_criteria, limit, offset."""
    #     logger.debug(f"get_alerts called with filter_criteria: {filter_criteria}, limit: {limit}, offset: {offset}")

    #     self.cursor.execute("SELECT COUNT(*) FROM alerts")
    #     row = self.cursor.fetchone()
    #     logger.debug(f"Số lượng alerts trong database: {row[0]}")

    #     if filter_criteria is None:
    #         if limit is not None and offset is not None:
    #             if not isinstance(limit, int) or not isinstance(offset, int):
    #                 raise TypeError("Limit and offset must be integers when both are provided.")
    #             return self.alerts[offset:offset + limit]
    #         return self.alerts[:]  # Return all alerts

    #     filtered_alerts = []
    #     for alert in self.alerts:
    #         logger.debug(f"Alert ID {alert.id} has priority: {alert.priority}")  # Debugging giá trị priority khi lấy từ cache
    #         match = True
    #         for key, value in filter_criteria.items():
    #             if hasattr(alert, key) and getattr(alert, key) != value:
    #                 match = False
    #                 break
    #         if match:
    #             filtered_alerts.append(alert)

    #     if limit is not None and offset is not None:
    #         if not isinstance(limit, int) or not isinstance(offset, int):
    #             raise TypeError("Limit and offset must be integers when both are provided.")
    #         return filtered_alerts[offset:offset+limit]

    #     return filtered_alerts

    def get_alerts(self, filter_criteria=None, limit=None, offset=None):
        """Retrieves alerts from the data storage, applying filters and pagination."""
        # 1.  Build a SQL query based on filter_criteria
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

        # 2. Add pagination logic using limit and offset
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        # 3. Execute the query and fetch results
        #   Replace this with your actual SQL execution
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error when getting alerts: {e}", exc_info=True)
            return []
        
        # 4. Convert results to Alert objects
        # Get column names and index of 'id'
        column_names = [desc[0] for desc in self.cursor.description]
        id_index = column_names.index("id")  if "id" in column_names else -1

        alerts = []
        for row in rows:
            if id_index >= 0:
                row_without_id = list(row)
                row_without_id.pop(id_index) # remove the id field from the row
                alerts.append(Alert(*row_without_id, last_seen=None)) # Set last_seen explicitly
            else:
                alerts.append(Alert(*row, last_seen=None)) # Set last_seen explicitly


        return alerts
    def get_alert_by_criteria(self, threat_data):
        try:
            query = """SELECT *
                        FROM alerts
                        WHERE src_IP = ? AND dst_IP = ? AND protocol = ?
                        """
            self.cursor.execute(query, (threat_data['src_IP'], threat_data['dst_IP'], threat_data['protocol']))
            rows = self.cursor.fetchall()
            return [Alert(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting alert by id: {e}", exc_info=True)
            return []

    def update_alert(self, alert):
        """Cập nhật alert trong database."""
        try:
            self.cursor.execute("""
                UPDATE alerts SET action_taken = ? WHERE src_IP = ?
            """, (alert.action_taken, alert.src_IP))
            print(f"Data manager action_taken: ", {alert.action_taken})
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi cập nhật alert: {e}", exc_info=True)

        for i, cached_alert in enumerate(self.alerts):
            if cached_alert.id == alert.id:
                self.alerts[i] = alert
                break

    def get_threats(self, limit=None, offset=None, priority = 3):
      """
      Gets all threats using one SQL query and using limit and offset
      """
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


    def search_alerts(self, filter_criteria, limit=None, offset=None):
        """Tìm kiếm alert theo filter_criteria và phân trang."""
        try:
            where_clause = "WHERE " + " AND ".join([f"{key} LIKE ?" for key in filter_criteria.keys()])
            values = tuple(['%' + value + '%' for value in filter_criteria.values()])
            query = f"SELECT * FROM alerts {where_clause}"
            if limit is not None and offset is not None:
                if not isinstance(limit, int) or not isinstance(offset, int):
                    raise TypeError("Limit and offset must be integers when both are provided.")
                query += f" LIMIT {limit} OFFSET {offset}"
            self.cursor.execute(query, values)
            rows = self.cursor.fetchall()
            return [Alert(**dict(row)) for row in rows]  # Convert to dict first
        except sqlite3.Error as e:
            logger.error(f"The error when finding alerts: {e}", exc_info=True)
            return []

    def delete_alerts(self, filter_criteria=None):
        """Xóa alerts từ database dựa trên các filter criteria."""
        try:
            # Nếu không có filter_criteria, xóa tất cả dữ liệu
            if filter_criteria is None:
                query = "DELETE FROM alerts"
                self.cursor.execute(query)
                logger.info("Đã xóa tất cả các alert từ database.")
            else:
                # Nếu có filter_criteria, xây dựng câu lệnh WHERE để xóa theo điều kiện
                where_clause = "WHERE " + " AND ".join([f"{key} = ?" for key in filter_criteria.keys()])
                values = tuple(filter_criteria.values())
                query = f"DELETE FROM alerts {where_clause}"
                self.cursor.execute(query, values)
                logger.info(f"Đã xóa các alert với điều kiện {filter_criteria} từ database.")
            
            # Commit thay đổi vào cơ sở dữ liệu
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Lỗi khi xóa alerts: {e}", exc_info=True)

    def __del__(self):
        """Đóng kết nối database khi DataManager bị hủy."""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.commit()
                self.conn.close()
            except sqlite3.Error as e:
                logger.error(f"The error when closing database: {e}", exc_info=True)