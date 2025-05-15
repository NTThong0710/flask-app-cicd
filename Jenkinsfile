pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'flask-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        EC2_IP = 'your-ec2-instance-ip'
        DOCKER_HUB_CREDS = credentials('docker-hub-credentials')
        DOCKER_HUB_REPO = 'yourusername/flask-app'
        SONARCLOUD_TOKEN = credentials('sonarcloud-token')
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
        
        stage('SonarCloud Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        # Sử dụng SonarScanner 4.5.0.2216 - phiên bản tương thích với Java 11
                        export SONAR_SCANNER_VERSION=4.5.0.2216
                        
                        # Tải SonarScanner
                        wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip
                        
                        # Giải nén
                        unzip -q sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip
                        
                        # Chạy SonarScanner
                        ./sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin/sonar-scanner \
                            -Dsonar.host.url=https://sonarcloud.io \
                            -Dsonar.login=${SONAR_TOKEN} \
                            -Dsonar.projectKey=NTThong0710_flask-app-cicd \
                            -Dsonar.organization=ntthong0710
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                sh '''
                    echo $DOCKER_HUB_CREDS_PSW | docker login -u $DOCKER_HUB_CREDS_USR --password-stdin
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_HUB_REPO}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_HUB_REPO}:latest
                    docker push ${DOCKER_HUB_REPO}:${DOCKER_TAG}
                    docker push ${DOCKER_HUB_REPO}:latest
                '''
            }
        }
        
        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} "
                            echo $DOCKER_HUB_CREDS_PSW | docker login -u $DOCKER_HUB_CREDS_USR --password-stdin
                            docker pull ${DOCKER_HUB_REPO}:latest
                            docker stop flask-container || true
                            docker rm flask-container || true
                            docker run -d -p 5000:5000 --name flask-container ${DOCKER_HUB_REPO}:latest
                            docker system prune -f
                        "
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
