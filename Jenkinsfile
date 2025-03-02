pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/migavel508/NFT_cloud.git'
            }
        }

        stage('Build') {
            steps {
                echo 'Building project...'
                echo 'Installing dependencies...'
                
                script {
                    if (isUnix()) {
                        sh 'python3 -m venv venv && source venv/bin/activate' // Create virtual env (Linux/macOS)
                        sh 'pip install -r requirements.txt'  // Install dependencies
                    } else {
                        bat 'python -m venv venv && venv\\Scripts\\activate' // Windows virtual env
                        bat 'pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                script {
                    if (isUnix()) {
                        sh 'pytest'
                    } else {
                        bat 'pytest'
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying...'
                script {
                    if (isUnix()) {
                        sh 'nohup python server.py &'
                    } else {
                        bat 'start /B python server.py'
                    }
                }
            }
        }
    }
}
