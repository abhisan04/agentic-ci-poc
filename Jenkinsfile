pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Env') {
            steps {
                sh '''
                  python3 -m venv .venv
                  . .venv/bin/activate
                  pip install --upgrade pip
                  pip install -r requirements.txt
                '''
            }
        }

        stage('Agent Self-Validation (NO SELF SCAN)') {
            steps {
                sh '''
                  . .venv/bin/activate

                  echo "Running agent self-validation with strict exclusions"

                  python3 run_scan.py \
                    --target ./src \
                    --exclude agent,agentic,.git,.venv,node_modules,tests
                '''
            }
        }

        stage('Agent Health Check') {
            steps {
                sh '''
                  . .venv/bin/activate
                  python3 -c "import agent; print('Agent loaded successfully')"
                '''
            }
        }
    }

    post {
        always {
            echo "Agentic CI completed (informational only)"
        }
        failure {
            echo "Agent CI failed – investigate agent stability (not target app quality)"
        }
    }
}
