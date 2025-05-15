pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'flask-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        EC2_IP = '3.0.59.46'  // Thay bằng IP EC2 thực tế của bạn
        DOCKER_HUB_CREDS = credentials('docker-hub-credentials')
        DOCKER_HUB_REPO = 'thong0710/flask-app'  // Thay thế bằng username Docker Hub thực tế
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Lint') {
            steps {
                sh '''
                    . venv/bin/activate
                    flake8 --ignore=E302,E305,W292 --max-line-length=120
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest --cov=. --cov-report=xml --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        // SonarCloud stage được giữ nguyên nhưng đang bị comment out
        
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                sh '''
                    # Đăng nhập vào Docker Hub
                    echo $DOCKER_HUB_CREDS_PSW | docker login -u $DOCKER_HUB_CREDS_USR --password-stdin
                    
                    # In ra các biến để kiểm tra
                    echo "Docker Image: ${DOCKER_IMAGE}"
                    echo "Docker Tag: ${DOCKER_TAG}"
                    echo "Docker Hub Repo: ${DOCKER_HUB_REPO}"
                    echo "Docker Hub User: ${DOCKER_HUB_CREDS_USR}"
                    
                    # Tạo tên repo từ tên người dùng Docker Hub thực tế nếu DOCKER_HUB_REPO không được cấu hình
                    ACTUAL_REPO=${DOCKER_HUB_REPO:-${DOCKER_HUB_CREDS_USR}/flask-app}
                    
                    # Tag với tên repo chính xác
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${ACTUAL_REPO}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${ACTUAL_REPO}:latest
                    
                    # Push lên Docker Hub
                    docker push ${ACTUAL_REPO}:${DOCKER_TAG}
                    docker push ${ACTUAL_REPO}:latest
                '''
            }
        }
        
        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh '''
                        # Kiểm tra SSH agent
                        ssh-add -l
                        
                        # Thực hiện deploy bằng scp/ssh tới EC2 server
                        # Bỏ qua kiểm tra host key để tránh lỗi
                        ssh -o StrictHostKeyChecking=no ec2-user@your-ec2-instance-ip '
                            # Pull image từ Docker Hub
                            docker pull thong0710/flask-app:latest
                            
                            # Dừng container cũ nếu đang chạy
                            docker stop flask-app || true
                            docker rm flask-app || true
                            
                            # Chạy container mới
                            docker run -d -p 5000:5000 --name flask-app thong0710/flask-app:latest
                        '
                    '''
                }
            }
        }
    }
    
    post {
        always {
            sh 'docker system prune -f'
            cleanWs()
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline execution failed!'
        }
    }
}
