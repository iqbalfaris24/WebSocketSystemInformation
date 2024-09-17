import psutil
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Mengizinkan semua origin untuk akses

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
    }

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