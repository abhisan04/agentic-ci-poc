pipeline {
    agent any

    environment {
        AGENT_SIGNAL = "${params.SIGNAL}"
    }

    parameters {
        choice(name: 'SIGNAL', choices: ['pass', 'fail'], description: 'Agent input')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Agent Decision') {
            steps {
                sh '''
                  python3 agent/decision_agent.py
                '''
            }
        }

        stage('Post-Agent Stage') {
            steps {
                echo "Agent allowed pipeline to continue 🚀"
            }
        }
    }
}