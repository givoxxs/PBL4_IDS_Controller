import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter
import logging

class Plotter:
    @staticmethod
    def plot_alerts_over_time(ax, alerts):
        """Vẽ biểu đồ số lượng alert theo thời gian."""
        # lấy 1000 alert gần nhất
        alerts = alerts[-100    :]
        dates = []
        for alert in alerts:
            try:
                if alert.timestamp:
                    date = mdates.datestr2num(str(alert.timestamp))
                    dates.append(date)
            except (ValueError, TypeError) as e:
                logging.error(f"Invalid timestamp: {alert.timestamp} - {alert.src_IP} - {alert.dst_IP}")
                logging.error(f"Error: {e}")

        # Xóa đồ thị cũ trước khi vẽ mới
        ax.clear()
        ax.plot_date(dates, range(len(dates)), linestyle='solid')
        ax.set_title('Alerts over time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Number of alerts')
        ax.xaxis.set_major_locator(mdates.AutoDateLocator()) # Tự động chọn vị trí đặt label
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S')) # Định dạng label thời gian
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right") # Xoay label và canh phải
        
    @staticmethod
    def get_top_attack_ips(alerts, top_n=10):
        """Lấy top N IP tấn công."""
        src_ips = [alert.src_IP for alert in alerts]
        ip_counter = Counter(src_ips)
        top_ips = dict(ip_counter.most_common(top_n))
        return top_ips # Return the top IPs

    @staticmethod
    def plot_top_attack_ips(ax, alerts, top_n=10):
        """Vẽ biểu đồ top N IP tấn công."""
        src_ips = [alert.src_IP for alert in alerts]
        ip_counter = Counter(src_ips)
        top_ips = ip_counter.most_common(top_n)
        
        # Xử lý trường hợp không có IP nào
        if not top_ips:
            ax.text(0.5, 0.5, "No data available", ha='center', va='center')
            return

        ips, counts = zip(*top_ips)

        ax.clear() # Xóa trước khi vẽ

        ax.bar(ips, counts)
        ax.set_xlabel('IP Address')
        ax.set_ylabel('Number of attacks')
        ax.set_title(f'Top {top_n} Attacking IPs')
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


    @staticmethod
    def plot_alert_types(ax, alerts):
        """Vẽ biểu đồ loại tấn công."""
        protocols = [alert.protocol for alert in alerts]
        protocol_counter = Counter(protocols) 

        ax.clear()
        ax.pie(protocol_counter.values(), labels=protocol_counter.keys(), autopct='%1.1f%%', startangle=140)
        ax.set_title('Alerts by Protocol')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    @staticmethod
    def get_top_rules_2(alerts, top_n=10):
        """Lấy top N rules bị kích hoạt nhiều nhất."""
        rules = [(alert.gid, alert.sid) for alert in alerts if alert.gid and alert.sid]
        rule_counter = Counter(rules)
        # top_rules = rule_counter.most_common(top_n)
        top_rules = dict(rule_counter.most_common(top_n))
        return top_rules

    @staticmethod
    def get_top_rules(alerts, top_n=10):
        """Lấy top N rules bị kích hoạt nhiều nhất."""
        rules = [(alert.gid, alert.sid) for alert in alerts if alert.gid and alert.sid]
        rule_counter = Counter(rules)
        top_rules = rule_counter.most_common(top_n)
        return top_rules

    @staticmethod
    def plot_top_rules(ax, alerts, top_n=10):
        """Vẽ biểu đồ top N rules bị kích hoạt nhiều nhất."""
        top_rules = Plotter.get_top_rules(alerts, top_n)

        if not top_rules:
            ax.text(0.5, 0.5, "No data available", ha='center', va='center')
            return

        rules, counts = zip(*top_rules)
        rules_labels = [f"{gid}:{sid}" for gid, sid in rules]

        ax.clear()
        ax.bar(rules_labels, counts)
        ax.set_xlabel('Rule (GID:SID)')
        ax.set_ylabel('Occurrences')
        ax.set_title(f'Top {top_n} Triggered Rules')
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")