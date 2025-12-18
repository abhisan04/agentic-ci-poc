pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Meta-Agent') {
            steps {
                // Run meta-agent: it internally calls static & dynamic agents as needed
                sh 'python3 agent/meta_agent.py > agent_result.json'

                script {
                    def result = readJSON file: 'agent_result.json'
                    echo "Agent Result: ${result}"

                    // Pipeline only enforces final decision
                    if (result.final_decision == 'FAIL') {
                        error("Pipeline blocked by agent: ${result.action}")
                    }
                }
            }
        }

        stage('Post-Agent Stage') {
            steps {
                echo "Agent allowed pipeline to continue 🚀"
            }
        }
    }
}
