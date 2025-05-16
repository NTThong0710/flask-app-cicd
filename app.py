from flask import Flask, jsonify, render_template, request, redirect, url_for
import datetime
import platform
import psutil

# Khởi tạo ứng dụng
app = Flask(__name__)

# Lưu trữ thông tin truy cập
access_logs = []

# Trang chủ với giao diện HTML đẹp
@app.route('/')
def home():
    # Lưu log truy cập
    log_access(request)
    
    # Thông tin hệ thống
    system_info = {
        "os": platform.system() + " " + platform.release(),
        "python": platform.python_version(),
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "hostname": platform.node()
    }
    
    return render_template('index.html', system_info=system_info)

# API endpoint trả về JSON
@app.route('/api/info')
def api_info():
    return jsonify({
        "message": "Chào mừng đến với Flask CI/CD Pipeline!",
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "online"
    })

# Kiểm tra sức khỏe hệ thống
@app.route('/health')
def health():
    # Lấy thông tin hệ thống
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    health_data = {
        "status": "healthy",
        "uptime": str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())),
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "memory_usage": f"{memory.percent}%",
        "disk_usage": f"{disk.percent}%"
    }
    
    return jsonify(health_data)

# Trang thống kê truy cập
@app.route('/stats')
def stats():
    return render_template('stats.html', logs=access_logs)

# Xóa logs
@app.route('/stats/clear', methods=['POST'])
def clear_stats():
    global access_logs
    access_logs = []
    return redirect(url_for('stats'))

# Hàm ghi log truy cập
def log_access(request):
    global access_logs
    log_entry = {
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "ip": request.remote_addr,
        "path": request.path,
        "user_agent": request.user_agent.string
    }
    access_logs.append(log_entry)
    # Giới hạn số lượng log
    if len(access_logs) > 100:
        access_logs = access_logs[-100:]

if __name__ == '__main__':
    # Chạy ứng dụng
    app.run(host='0.0.0.0', port=5000, debug=False)