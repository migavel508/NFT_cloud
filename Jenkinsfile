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
                bat  'pip install -r requirements.txt'  // Install dependencies
                bat  'python server.py'  // Start the server
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                // Add test commands here (e.g., pytest, jest, etc.)
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying...'
                // Add deployment commands here
            }
        }
    }
}
