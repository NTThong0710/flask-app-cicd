from flask import Flask, jsonify, render_template, request, redirect, url_for
import datetime
import platform
import psutil
import os

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
    # Tạo thư mục templates nếu chưa tồn tại
    os.makedirs('templates', exist_ok=True)
    
    # Tạo file template index.html
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask CI/CD Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            padding-top: 2rem;
        }
        .card {
            border-radius: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .header-container {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        .system-info {
            background-color: rgba(255,255,255,0.1);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-top: 1rem;
        }
        .btn-primary {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            border: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-container">
            <h1 class="display-4">Flask CI/CD Pipeline Demo</h1>
            <p class="lead">Xây dựng và triển khai tự động với Jenkins</p>
            
            <div class="system-info">
                <div class="row">
                    <div class="col-md-4">
                        <p><strong>Hệ điều hành:</strong> {{ system_info.os }}</p>
                    </div>
                    <div class="col-md-4">
                        <p><strong>Python:</strong> {{ system_info.python }}</p>
                    </div>
                    <div class="col-md-4">
                        <p><strong>Máy chủ:</strong> {{ system_info.hostname }}</p>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Ngày:</strong> {{ system_info.date }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Giờ:</strong> {{ system_info.time }}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">Kiểm tra sức khỏe</h5>
                        <p class="card-text">Xem thông tin về trạng thái hệ thống</p>
                        <a href="/health" class="btn btn-primary">Kiểm tra</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">API</h5>
                        <p class="card-text">Truy cập API để lấy thông tin hệ thống</p>
                        <a href="/api/info" class="btn btn-primary">Truy cập API</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">Thống kê truy cập</h5>
                        <p class="card-text">Xem log truy cập trang web</p>
                        <a href="/stats" class="btn btn-primary">Xem thống kê</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-5">
            <p>Được triển khai tự động với Jenkins CI/CD Pipeline</p>
            <p><small>Thời gian hiện tại: {{ system_info.time }}</small></p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''')
    
    # Tạo file template stats.html
    with open('templates/stats.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thống kê truy cập - Flask CI/CD Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            padding-top: 2rem;
        }
        .header-container {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        .table-container {
            background-color: white;
            border-radius: 1rem;
            padding: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            border: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-container">
            <h1>Thống kê truy cập</h1>
            <p class="lead">Log các truy cập gần đây</p>
        </div>
        
        <div class="mb-3 d-flex justify-content-between">
            <a href="/" class="btn btn-primary">Về trang chủ</a>
            <form action="/stats/clear" method="post">
                <button type="submit" class="btn btn-danger">Xóa logs</button>
            </form>
        </div>
        
        <div class="table-container">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Thời gian</th>
                        <th>Ngày</th>
                        <th>IP</th>
                        <th>Đường dẫn</th>
                        <th>User Agent</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td>{{ log.time }}</td>
                        <td>{{ log.date }}</td>
                        <td>{{ log.ip }}</td>
                        <td>{{ log.path }}</td>
                        <td class="text-truncate" style="max-width: 300px;">{{ log.user_agent }}</td>
                    </tr>
                    {% endfor %}
                    
                    {% if logs|length == 0 %}
                    <tr>
                        <td colspan="5" class="text-center">Không có dữ liệu truy cập</td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
        
        <div class="text-center mt-5">
            <p>Được triển khai tự động với Jenkins CI/CD Pipeline</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        ''')
    
    # Chạy ứng dụng
    app.run(host='0.0.0.0', port=5000, debug=False)