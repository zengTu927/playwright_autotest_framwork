pipeline {
    agent any

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['test', 'prod'],
            description: '选择测试环境'
        )

        string(
            name: 'TEST_MARK',
            defaultValue: 'smoke',
            description: 'pytest marker 表达式，例如：smoke、login、smoke and login'
        )

        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'webkit'],
            description: '选择浏览器'
        )

        string(
            name: 'RERUNS',
            defaultValue: '1',
            description: '失败重试次数'
        )
    }

    environment {
        PYTHONUNBUFFERED = '1'
        ALLURE_RESULTS_DIR = 'reports/allure-results'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate

                    python -m pip install --upgrade pip
                    pip install -r requirements.txt

                    python -m playwright install ${BROWSER}
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . .venv/bin/activate

                    pytest \
                      -m "${TEST_MARK}" \
                      --env "${TEST_ENV}" \
                      --browser "${BROWSER}" \
                      --reruns "${RERUNS}" \
                      --reruns-delay 2
                '''
            }
        }
    }

    post {
        always {
            allure([
                results: [[path: "${ALLURE_RESULTS_DIR}"]]
            ])

            archiveArtifacts(
                artifacts: 'reports/screenshots/**/*, reports/traces/**/*, reports/logs/**/*, reports/playwright-output/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }
    }
}