pipeline {
    agent any

    parameters {
        choice(
            name: 'APP_VERSION',
            choices: ['v1', 'v2', 'v3'],
            description: 'Choose the library application version'
        )

        choice(
            name: 'GIT_BRANCH',
            choices: ['version-v1', 'version-v2', 'version-v3'],
            description: 'Choose the GitHub branch to build'
        )
    }

    environment {
        DOCKERHUB_USER = 'sahanalakshmi18'
        IMAGE_NAME = 'library-system'
        K8S_DEPLOYMENT = "library-${APP_VERSION}"
        K8S_SERVICE = "library-${APP_VERSION}-service"
    }

    stages {

        stage('1. Checkout') {
            steps {
                echo 'Checking out source code from GitHub'

                git branch: "${params.GIT_BRANCH}",
                    url: 'https://github.com/sahana-lakshmi/library-system.git'
            }
        }

        stage('2. Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('3. Run Tests') {
            steps {
                bat 'python -m pytest -v'
            }
        }

        stage('4. Code Quality') {
            steps {
                bat 'python -m flake8 app.py test_app.py --count --statistics'
            }
        }

        stage('5. Build Docker Image') {
            steps {
                bat '''
                    docker build ^
                    -t %DOCKERHUB_USER%/%IMAGE_NAME%:%APP_VERSION% .
                '''
            }
        }

        stage('6. Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_PASSWORD'
                    )
                ]) {
                    bat '''
                        echo %DH_PASSWORD% | docker login -u "%DH_USER%" --password-stdin
                        if errorlevel 1 exit /b 1

                        docker push %DOCKERHUB_USER%/%IMAGE_NAME%:%APP_VERSION%
                        if errorlevel 1 exit /b 1

                        docker logout
                    '''
                }
            }
        }

        stage('7. Deploy to Kubernetes') {
            steps {
                bat '''
                    kubectl config use-context docker-desktop

                    kubectl create deployment %K8S_DEPLOYMENT% ^
                    --image=%DOCKERHUB_USER%/%IMAGE_NAME%:%APP_VERSION% ^
                    --dry-run=client -o yaml | kubectl apply -f -

                    kubectl set env deployment/%K8S_DEPLOYMENT% ^
                    APP_VERSION=%APP_VERSION%

                    kubectl rollout status deployment/%K8S_DEPLOYMENT% ^
                    --timeout=120s

                    kubectl expose deployment %K8S_DEPLOYMENT% ^
                    --name=%K8S_SERVICE% ^
                    --type=NodePort ^
                    --port=5000 ^
                    --target-port=5000 ^
                    --dry-run=client -o yaml | kubectl apply -f -
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Pipeline completed successfully!'
        }

        failure {
            echo 'FAILED: Check the stage logs to identify the error.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}