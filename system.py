import psutil
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import re
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variabel global untuk menyimpan hasil perhitungan log
log_access_summary = {}
log_directory = '/var/log/apache2/'  # Tentukan direktori log

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
                if log_data['method'] == 'GET' and log_data['path'] == '/':
                    count += 1
    return count

def process_log_files():
    global log_access_summary
    log_files = [f for f in os.listdir(log_directory) if f.endswith('_access.log')]
    
    for log_file in log_files:
        file_path = os.path.join(log_directory, log_file)
        count = parse_log_file(file_path)
        log_access_summary[log_file] = count

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
            'current': f"{current_freq:.2f}",
            'min': f"{min_freq:.2f}",
            'max': f"{max_freq:.2f}",
            'temperature': cpu_temp,
            'percent': (current_freq / 2.0) * 100
        },
        'memory_percent': memory_usage_percent,
        'memory_total': f"{memory_total:.2f}",
        'memory_used': f"{memory_used:.2f}",
        'storage_percent': storage_usage_percent,
        'storage_total': f"{storage_total:.2f}",
        'storage_used': f"{storage_used:.2f}",
        'log_status':'Hellow'
    }

def send_log_status():
    socketio.emit('log_status_update', log_access_summary)

def background_thread():
    """Mengirim data status sistem ke klien setiap 5 detik"""
    while True:
        status = get_system_status()
        socketio.emit('status_update', status)
        socketio.sleep(3)  # Menunggu selama 3 detik sebelum mengirim data lagi

@socketio.on('connect')
def handle_connect():
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