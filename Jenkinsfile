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
    FEISHU_WEBHOOK = credentials('lark_webhook')
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
                    export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
                    export PATH="$JAVA_HOME/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    echo "系统 python3:"
                    which python3
                    python3 --version

                    rm -rf .venv

                    python3 -m venv .venv
                    . .venv/bin/activate

                    echo "虚拟环境 Python:"
                    which python
                    python --version

                    python -m pip install -r requirements.txt -i https://pypi.org/simple

                    python -m playwright install chromium firefox webkit
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
                    export PATH="$JAVA_HOME/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                    . .venv/bin/activate

                    echo "运行测试使用的 Python:"
                    which python
                    python --version

                    echo "pytest 来源:"
                    which pytest
                    python -m pytest --version

                    BROWSER_ARGS=""
                    IFS=',' read -ra BROWSER_LIST <<< "${BROWSERS}"

                    for browser in "${BROWSER_LIST[@]}"; do
                        BROWSER_ARGS="$BROWSER_ARGS --browser $browser"
                    done

                    echo "测试环境: ${TEST_ENV}"
                    echo "测试标签: ${TEST_MARK}"
                    echo "浏览器参数: $BROWSER_ARGS"
                    echo "重试次数: ${RERUNS}"

                    python -m pytest \
                      -m "${TEST_MARK}" \
                      --env "${TEST_ENV}" \
                      $BROWSER_ARGS \
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

            script {
                def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'

                withEnv(["BUILD_STATUS=${buildStatus}"]) {
                    sh '''
                        export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
                        export PATH="$JAVA_HOME/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

                        if [ -d ".venv" ]; then
                            . .venv/bin/activate

                            python -m common/lark \
                              --webhook "$FEISHU_WEBHOOK" \
                              --job-name "$JOB_NAME" \
                              --build-number "$BUILD_NUMBER" \
                              --build-status "$BUILD_STATUS" \
                              --test-env "$TEST_ENV" \
                              --test-mark "$TEST_MARK" \
                              --browsers "$BROWSER" \
                              --reruns "$RERUNS" \
                              --build-url "$BUILD_URL" \
                              --allure-url "${BUILD_URL}allure/" \
                              --allure-results-dir "reports/allure-results"
                        else
                            echo ".venv 不存在，跳过飞书通知"
                        fi
                    '''
                }
            }
        }
    }
}