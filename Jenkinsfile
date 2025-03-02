pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/migavel508/NFT_cloud.git'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: "${REPO_URL}"
            }
        }

        stage('Build') {
            steps {
                echo 'Building project...'
                script {
                    if (isUnix()) {
                        sh '''
                        python3 -m venv venv
                        source venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                        python -m venv venv
                        call venv\\Scripts\\activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                script {
                    if (isUnix()) {
                        sh '''
                        source venv/bin/activate
                        pytest --maxfail=3 --disable-warnings
                        '''
                    } else {
                        bat '''
                        call venv\\Scripts\\activate
                        
                        '''
                    }
                }
            }
        }

        stage('Deploy') {
            when {
               expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }


            }
            steps {
                echo 'Deploying...'
                script {
                    if (isUnix()) {
                        sh '''
                        source venv/bin/activate
                        nohup python server.py > server.log 2>&1 &
                        '''
                    } else {
                        bat '''
                        call venv\\Scripts\\activate
                        start /B python server.py
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            deleteDir()
        }
    }
}
