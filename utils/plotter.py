import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter

class Plotter:
    def plot_alerts_over_time(alerts):
        '''
        Vẽ biểu đồ số lượng alert theo thời gian
        '''
        # Tạo list chứa timestamp của các alert
        timestamps = [alert.timestamp for alert in alerts]
        # Đếm số lượng alert theo timestamp
        dates = [] # List chứa các timestamp
        for alert in alerts:
            try: 
                if alert.timestamp:
                    date = mdates.datestr2num(str(alert.timestamp))
                    dates.append(date)
            except (ValueError, TypeError) as e:
                print(f"Invalid timestamp: {alert.timestamp} - {alert.src_IP} - {alert.dst_IP}")
                print(f"Error: {e}")
        
        plt.figure(figsize=(10, 6))
        plt.plot_date(dates, range(len(dates)), linestyle='solid', marker=None)
        plt.title('Alerts over time')
        plt.xlabel('Time')
        plt.ylabel('Number of alerts')
        plt.xticks(rotation=45) # Xoay label trục x
        plt.tight_layout()
        plt.show()
        
    def plot_top_stacks_ips(alerts, top_n=10):
        '''
        Vẽ biểu đồ top N IP
        '''
        # Tạo list chứa IP nguồn của các alert
        src_ips = [alert.src_IP for alert in alerts]
        # Đếm số lần xuất hiện của mỗi IP
        ip_counter = Counter(src_ips)
        # Lấy top N IP
        top_ips = ip_counter.most_common(top_n)
        ips, counts = zip(*top_ips)
        
        plt.figure(figsize=(10, 6))
        plt.bar(ips, counts)
        plt.title(f'Top {top_n} Attackings IPs')
        plt.xlabel('Source IP Address')
        plt.ylabel('Number of alerts')
        plt.xticks(rotation=45, ha='right') # Xoay label trục x, canh phải
        plt.tight_layout()
        plt.show()
        
    def plot_alert_types(alerts):
        protocols = [alert.protocol for alert in alerts]
        protocol_counter = Counter(protocols)
        plt.figure(figsize=(10, 6))
        plt.pie(protocol_counter.values(), labels=protocol_counter.keys(), autopct='%1.1f%%', startangle=140) # Vẽ biểu đồ tròn, tỉ lệ %
        plt.title('Alerts by Protocol')
        plt.tight_layout() # Tự động căn chỉnh layout
        plt.show()
        
    def plot_top_rules(alerts, top_n=10):
        rules = [(alert.gid, alert.sid) for alert in alerts if alert.gid and alert.sid]
        rule_counter = Counter(rules)
        top_rules = rule_counter.most_common(top_n)
        rules, counts = zip(*top_rules)
        rules_labels = [f"{gid}:{sid}" for gid, sid in rules]
        plt.figure(figsize=(10, 6))
        plt.bar(rules_labels, counts)
        plt.xlabel('Rule (GID:SID)')
        plt.ylabel('Occurrences')
        plt.xticks(rotation=45, ha='right')
        plt.title(f'Top {top_n} Triggered Rules')
        plt.tight_layout()
        plt.show()
         