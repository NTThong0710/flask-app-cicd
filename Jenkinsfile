pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'flask-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        EC2_IP = '' 
        DOCKER_HUB_CREDS = credentials('docker-hub-credentials')
        DOCKER_HUB_REPO = 'thong0710/flask-app'  
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Lint & Quick Test') {
            steps {
                sh '''
                    # Kiểm tra syntax Python nhanh
                    python3 -m py_compile app.py
                    echo "Python syntax check passed"
                    
                    # Basic test nếu có
                    if [ -f "test_app.py" ]; then
                        python3 -m pytest test_app.py -v --tb=short
                    fi
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh '''
                    # Build với resource limit để tránh overload
                    docker build --memory=512m --cpus=0.5 -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    
                    # Cleanup ngay sau build
                    docker image prune -f
                '''
            }
        }
        
        stage('Test Docker Image') {
            steps {
                sh '''
                    # Test container có chạy được không
                    docker run --rm -d --name test-container -p 5001:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}
                    sleep 10
                    
                    # Health check
                    curl -f http://localhost:5001/ || exit 1
                    
                    # Stop test container
                    docker stop test-container
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                sh '''
                    # Login Docker Hub
                    echo $DOCKER_HUB_CREDS_PSW | docker login -u $DOCKER_HUB_CREDS_USR --password-stdin
                    
                    # Tag và push
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_HUB_REPO}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_HUB_REPO}:latest
                    
                    docker push ${DOCKER_HUB_REPO}:${DOCKER_TAG}
                    docker push ${DOCKER_HUB_REPO}:latest
                    
                    # Cleanup local images sau khi push
                    docker rmi ${DOCKER_HUB_REPO}:${DOCKER_TAG} ${DOCKER_HUB_REPO}:latest || true
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 ec2-user@${EC2_IP} "
                            # Pull image mới
                            docker pull ${DOCKER_HUB_REPO}:latest
                            
                            # Stop container cũ
                            docker stop flask-app 2>/dev/null || true
                            docker rm flask-app 2>/dev/null || true
                            
                            # Chạy container mới
                            docker run -d -p 5000:5000 --name flask-app --restart unless-stopped ${DOCKER_HUB_REPO}:latest
                            
                            # Cleanup images cũ
                            docker image prune -f
                            
                            # Health check
                            sleep 10
                            curl -f http://localhost:5000/ && echo 'Deployment successful!' || echo 'Deployment failed!'
                        "
                    """
                }
            }
        }
    }
            
    post {
        always {
            // Cleanup workspace và Docker
            sh '''
                docker system prune -f || true
                docker container prune -f || true
            '''
            cleanWs()
        }
        success {
            echo 'Pipeline executed successfully! 🎉'
            echo "Application deployed at: http://${EC2_IP}:5000"
        }
        failure {
            echo 'Pipeline execution failed! ❌'
            // Có thể thêm notification ở đây
        }
    }
}