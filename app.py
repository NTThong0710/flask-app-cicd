from flask import Flask, render_template_string, jsonify, request
import platform
import datetime

app = Flask(__name__)

# HTML template với CSS đẹp mắt
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flameo App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .header {
            background: linear-gradient(135deg, #FF5722, #FFC107);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .info-card {
            background-color: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .info-card:hover {
            transform: translateY(-5px);
        }
        .card-title {
            font-size: 1.5rem;
            color: #FF5722;
            margin-bottom: 1rem;
            border-bottom: 2px solid #f5f5f5;
            padding-bottom: 0.5rem;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #FF5722, #FFC107);
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            margin-top: 1rem;
        }
        .btn:hover {
            opacity: 0.9;
            transform: scale(1.05);
        }
        .footer {
            text-align: center;
            margin-top: 3rem;
            color: #666;
        }
        .emoji {
            font-size: 2rem;
            margin-right: 0.5rem;
            vertical-align: middle;
        }
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            .container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">🔥</span> Welcome to Flameo!</h1>
            <p>Successfully deployed with Jenkins CI/CD Pipeline</p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h2 class="card-title">System Info</h2>
                <p><strong>Operating System:</strong> {{ system_info.os }}</p>
                <p><strong>Python Version:</strong> {{ system_info.python }}</p>
                <p><strong>Hostname:</strong> {{ system_info.hostname }}</p>
                <p><strong>Current Time:</strong> {{ system_info.time }}</p>
                <p><strong>Date:</strong> {{ system_info.date }}</p>
                <a href="/health" class="btn">Check Health</a>
            </div>
            
            <div class="info-card">
                <h2 class="card-title">About This App</h2>
                <p>This is a simple Flask application deployed using a CI/CD pipeline with Jenkins, Docker, and AWS EC2.</p>
                <p>The pipeline automatically builds, tests, and deploys the application whenever changes are pushed to the repository.</p>
                <p><strong>GitHub Repository:</strong>
                    <a href="https://github.com/NTThong0710/flask-app-cicd">flask-app-cicd</a>
                </p>
                <a href="https://github.com/NTThong0710/flask-app-cicd"
                    target="_blank" class="btn">View Source</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Flameo Hotman! 🔥 © 2025</p>
            <p>Made with ❤️ by Flameo Team</p>
        </div>
    </div>
</body>
</html>
'''

# Trang health với giao diện đẹp
HEALTH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flameo Health Check</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container {
            width: 90%;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }
        .header {
            background: linear-gradient(135deg, #4CAF50, #8BC34A);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .status-card {
            background-color: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 2rem;
        }
        .status-indicator {
            font-size: 5rem;
            margin-bottom: 1rem;
        }
        .status-text {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 1rem;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #FF5722, #FFC107);
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            opacity: 0.9;
            transform: scale(1.05);
        }
        .footer {
            text-align: center;
            margin-top: 3rem;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>System Health Check</h1>
            <p>Current status of the Flameo application</p>
        </div>
        
        <div class="status-card">
            <div class="status-indicator">✅</div>
            <div class="status-text">{{ status }}</div>
            <p>The system is running smoothly and all services are operational.</p>
        </div>
        
        <div style="text-align: center;">
            <a href="/" class="btn">Back to Home</a>
        </div>
        
        <div class="footer">
            <p>Flameo Hotman! 🔥 © 2025</p>
            <p>Made with ❤️ by Flameo Team</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    # Vẫn trả về JSON cho các yêu cầu API
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify({"message": "Hello from Flask in Jenkins CI/CD Pipeline!"})
    
    # Thông tin hệ thống
    system_info = {
        "os": platform.system() + " " + platform.release(),
        "python": platform.python_version(),
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "hostname": platform.node()
    }
    
    # Trả về HTML với template
    return render_template_string(HOME_TEMPLATE, system_info=system_info)

@app.route('/health')
def health():
    # Vẫn trả về JSON cho các yêu cầu API
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify({"status": "healthy"})
    
    # Trả về HTML với template
    return render_template_string(HEALTH_TEMPLATE, status="Healthy")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
