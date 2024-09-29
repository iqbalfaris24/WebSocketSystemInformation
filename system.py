import psutil
import threading
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import re
import os
import time
import cpuinfo

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variabel global untuk menyimpan hasil perhitungan log
log_access_summary = {}
log_directory = '/var/log/apache2/'  # Tentukan direktori log
systemInfo = {}

def parse_log_file(file_path):
    count = 0
    log_pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s'
        r'(?P<identd>\S+)\s'
        r'(?P<user>\S+)\s'
        r'\[(?P<time>[^\]]+)\]\s'
        r'"(?P<method>\S+)\s(?P<path>\S+)\s(?P<proto>\S+)"\s'
        r'(?P<status>\d+)\s'
        r'(?P<size>\d+|-)\s'
        r'"(?P<referer>[^"]*)"\s'
        r'"(?P<user_agent>[^"]*)"'
    )
    
    with open(file_path, 'r') as file:
        for line in file:
            match = log_pattern.match(line)
            if match:
                log_data = match.groupdict()
                # log_data['size'] = int(log_data['size']) if log_data['size'] != '-' else 0

                if log_data['method'] == 'GET' and log_data['path'] == '/':
                    count += 1
    return count

def process_log_files():
    global log_access_summary
    log_files = [f for f in os.listdir(log_directory) if f.endswith('_access.log')]
    
    for log_file in log_files:
        file_path = os.path.join(log_directory, log_file)
        count = parse_log_file(file_path)
        # Menghapus '_access.log' dari nama file sebelum menambahkannya ke summary
        log_access_summary[log_file.replace('_access.log', '')] = count
    return log_access_summary

def get_uptime():
    global systemInfo
    # Data Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    # Menghitung hari, jam, dan menit uptime
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    # CPU Info
    cpuInfo = cpuinfo.get_cpu_info()
    brandCpu = cpuInfo['brand_raw']
    # OS Info
    # Memperbaiki struktur untuk dictionary
    systemInfo = {
        'uptime' : {
            'days': days,
            'hours': hours,
            'minutes': minutes
        },
        'processor': brandCpu,
        'os': os.uname().sysname,
        'os_version': os.uname().version
    }
    return systemInfo

def get_system_status():
    # CPU usage
    cpu_freq = psutil.cpu_freq()
    # Mengambil frekuensi untuk single CPU
    current_freq = cpu_freq.current / 1000  # Mengonversi MHz ke GHz
    min_freq = cpu_freq.min / 1000          # Mengonversi MHz ke GHz
    max_freq = cpu_freq.max / 1000          # Mengonversi MHz ke GHz

    # Memory usage
    memory_info = psutil.virtual_memory()
    memory_usage_percent = memory_info.percent
    memory_total = memory_info.total / (1024**3)
    memory_used = memory_info.used / (1024**3)

    # Disk usage
    disk_info = psutil.disk_usage('/')
    storage_usage_percent = disk_info.percent
    storage_total = disk_info.total / (1024**3)
    storage_used = disk_info.used / (1024**3)
    # CPU temperature (note: may not work on all systems)
    try:
        temp_info = psutil.sensors_temperatures()
        cpu_temp = temp_info['coretemp'][0].current  # adjust as needed based on your system
    except KeyError:
        cpu_temp = "Temperature sensor not found"

    return {
        'cpu': {
            'processor': systemInfo['processor'],
            'current': f"{current_freq:.2f}",
            'min': f"{min_freq:.2f}",
            'max': f"{max_freq:.2f}",
            'temperature': cpu_temp,
            'percent': (current_freq / 2.0) * 100
        },
        'memory':{
            'percent': memory_usage_percent,
            'total': f"{memory_total:.2f}",
            'used': f"{memory_used:.2f}",
        },
        'storage':{
            'percent': storage_usage_percent,
            'total': f"{storage_total:.2f}",
            'used': f"{storage_used:.2f}",
        },
        'log_status': log_access_summary,
        'system_info': {
            'uptime': systemInfo['uptime'],
            'os': systemInfo['os'],
            'os_version': systemInfo['os_version'],
        }
    }

def background_thread():
    """Mengirim data status sistem ke klien setiap 5 detik"""
    while True:
        status = get_system_status()
        socketio.emit('status_update', status)
        socketio.sleep(3)  # Menunggu selama 3 detik sebelum mengirim data lagi

@socketio.on('connect')
def handle_connect():
    process_log_files()
    get_uptime()
    print("Client connected")
    global thread
    # Menggunakan lock untuk memastikan hanya ada satu thread yang berjalan
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Variabel global harus berada di luar blok __name__
thread = None
thread_lock = threading.Lock()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)