pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'flask-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        EC2_IP = '47.129.246.224' 
        DOCKER_HUB_CREDS = credentials('docker-hub-credentials')
        DOCKER_HUB_REPO = 'thong0710/flask-app'  
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
	// stage('SonarCloud Analysis') {
	//     steps {
	//         withCredentials([string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')]) {
	//             sh '''
	//                 apt-get update && apt-get install -y wget unzip
	
	//                 export SONAR_SCANNER_VERSION=4.6.2.2472
	//                 wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip
	//                 unzip -q sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip
	
	//                 # Thiết lập JAVA_HOME theo đúng bản Java 17
	//                 export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
	//                 export PATH=$JAVA_HOME/bin:$(pwd)/sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin:$PATH
	
	//                 echo "Using Java:"
	//                 java -version
	
	//                 sonar-scanner -Dsonar.login=${SONAR_TOKEN} -X
	//             '''
	//         }
	//     }
	// }


        
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
	            sh """
	                ssh -o StrictHostKeyChecking=no -t ec2-user@${EC2_IP} "
	                    docker pull thong0710/flask-app:latest
	                    docker stop flask-app || true
	                    docker rm flask-app || true
	                    docker run -d -p 5000:5000 --name flask-app thong0710/flask-app:latest
	                    docker system prune -f
	                "
	            """
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
