@Library(["devpi", "PythonHelpers"]) _

pipeline {
    agent {
        label 'Windows && Python3'
    }
    triggers {
        cron('@daily')
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        checkoutToSubdirectory("scm")
    }
    environment{
        PKG_NAME = pythonPackageName(toolName: "CPython-3.7")
        PKG_VERSION = pythonPackageVersion(toolName: "CPython-3.7")
        DOC_ZIP_FILENAME = "${env.PKG_NAME}-${env.PKG_VERSION}.doc.zip"
        DEVPI = credentials("DS_devpi")
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        booleanParam(name: "TEST_RUN_PYTEST", defaultValue: true, description: "Run unit tests with PyTest")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
        booleanParam(name: "TEST_RUN_MYPY", defaultValue: true, description: "Run MyPy Tests")
        booleanParam(name: "TEST_RUN_FLAKE8", defaultValue: true, description: "Run Flake8 Tests")
    }
    stages {
        stage('Configure Environment') {
            environment{
                PATH = "${tool 'CPython-3.7'};$PATH"
            }
            stages{
                stage("Purge All Existing Data in Workspace"){
                    when{
                        anyOf{
                            equals expected: true, actual: params.FRESH_WORKSPACE
                            triggeredBy "TimerTriggerCause"
                        }
                    }
                    steps{
                        deleteDir()
                        dir("scm"){
                            checkout scm
                        }
                    }
                }
                stage("Creating Python Virtualenv for Building"){
                    steps{
                        bat "if not exist venv\\37 mkdir venv\\37 && python -m venv venv\\37"
                        script {
                            try {
                                bat "venv\\37\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "python -m venv venv\\37"
                                bat "venv\\37\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }
                        }
                        bat "venv\\37\\Scripts\\pip.exe install -U setuptools wheel sqlalchemy mysqlclient"
//                        bat "venv36\\Scripts\\pip.exe install pytest-cov lxml flake8 mypy -r source\\requirements.txt --upgrade-strategy only-if-needed"
                    }
                post{
                    success{
                        bat "if not exist logs mkdir logs"
                        bat "venv\\37\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
                        archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
                    }
                }
            }
            }
            post{
                failure {
                    deleteDir()
                }
                success{
                    echo "Configured ${env.PKG_NAME}, version ${env.PKG_VERSION}, for testing."
                }
            }
        }
        stage("Building"){
            environment{
                PATH = "${WORKSPACE}\\venv\\37\\Scripts;$PATH"
            }
            steps{
                dir("scm"){
                    bat "python setup.py build -b ${WORKSPACE}\\build"
                }
            }
        }
        stage('Testing') {
            environment{
                PATH = "${WORKSPACE}\\venv\\37\\Scripts;$PATH"
            }
            stages{
                stage("Installing Python Testing Packages"){
                    steps{
                        bat 'pip install "tox<3.10" pytest mypy flake8 coverage lxml'
                    }
                }
                stage("Running Tests"){
                    parallel {
                        stage("PyTest"){
                            when {
                                equals expected: true, actual: params.TEST_RUN_PYTEST
                            }
                            steps{
                                dir("scm"){
                                    bat(
                                        label: "Run PyTest",
                                        script: "coverage run --parallel-mode --source=avforms -m pytest --junitxml=${WORKSPACE}/reports/pytest/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest"
                                    )
                                }
                            }
                            post {
                                always{
                                    junit "reports/pytest/junit-*.xml"
                                }
                                cleanup{
                                    cleanWs(patterns: [[pattern: 'reports/pytest/junit-*.xml', type: 'INCLUDE']])
                                }
                            }
                        }
                        stage("Tox") {
                            when {
                                equals expected: true, actual: params.TEST_RUN_TOX
                            }
                            environment {
                                PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                            }
                            steps {
                                dir("scm"){
                                    script{
                                        try{
                                            bat (
                                                label: "Run Tox",
                                                script: "tox --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox -vv --result-json=${WORKSPACE}\\logs\\tox_report.json"
                                            )

                                        } catch (exc) {
                                            bat(
                                                label: "Run Tox with new environments",
                                                script: "tox --recreate --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox -vv --result-json=${WORKSPACE}\\logs\\tox_report.json"
                                            )
                                        }
                                    }
                                }
                            }
                            post {
                                always {
                                    archiveArtifacts allowEmptyArchive: true, artifacts: '.tox/py*/log/*.log,.tox/log/*.log,logs/tox_report.json'
                                    recordIssues(tools: [pep8(id: 'tox', name: 'Tox', pattern: '.tox/py*/log/*.log,.tox/log/*.log')])
                                }
                                cleanup{
                                    cleanWs(
                                        patterns: [
                                            [pattern: '.tox/py*/log/*.log', type: 'INCLUDE'],
                                            [pattern: '.tox/log/*.log', type: 'INCLUDE'],
                                            [pattern: 'logs/rox_report.json', type: 'INCLUDE']
                                        ]
                                    )
                                }
                            }
                        }
                        stage("Run MyPy Static Analysis") {
                            when {
                                equals expected: true, actual: params.TEST_RUN_MYPY
                            }
                            stages{
                                stage("Generate Stubs") {
                                    steps{
                                        dir("scm"){
                                          bat "stubgen -p avforms -o ${WORKSPACE}\\mypy_stubs"
                                        }
                                    }

                                }
                                stage("Running MyPy"){
                                    environment{
                                        MYPYPATH = "${WORKSPACE}\\mypy_stubs"
                                    }
                                    steps{
                                        bat "if not exist reports\\mypy\\html mkdir reports\\mypy\\html"
                                        dir("scm"){
                                            bat(returnStatus: true,
                                                script: "mypy -p avforms --html-report ${WORKSPACE}\\reports\\mypy\\html > ${WORKSPACE}\\logs\\mypy.log",
                                                label: "Running MyPy"
                                                )

                                        }
                                    }
                                    post {
                                        always {
                                            recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/mypy/html/", reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                        }
                                    }
                                }
                            }
                        }
                        stage("Run Flake8 Static Analysis") {
                            when {
                                equals expected: true, actual: params.TEST_RUN_FLAKE8
                            }
                            steps{
                                dir("scm"){
                                    bat(returnStatus: true,
                                        script: "flake8 avforms --tee --output-file=${WORKSPACE}\\logs\\flake8.log",
                                        label: "Running Flake8"
                                        )
                                }
                            }
                            post {
                                always {
                                    archiveArtifacts 'logs/flake8.log'
                                    recordIssues(tools: [flake8(pattern: 'logs/flake8.log')])
                                }
                                cleanup{
                                    cleanWs(patterns: [[pattern: 'logs/flake8.log', type: 'INCLUDE']])
                                }
                            }
                        }
                    }
                    post{
                        always{
                            script{
                                try{
                                    dir("scm"){
                                        bat "${WORKSPACE}\\venv\\37\\Scripts\\coverage.exe combine"
                                        bat "${WORKSPACE}\\venv\\37\\Scripts\\coverage.exe xml -o ${WORKSPACE}\\reports\\coverage.xml"
                                        bat "${WORKSPACE}\\venv\\37\\Scripts\\coverage.exe html -d ${WORKSPACE}\\reports\\coverage"
                                    }
                                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/coverage", reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                                    publishCoverage adapters: [
                                                    coberturaAdapter('reports/coverage.xml')
                                                    ],
                                                sourceFileResolver: sourceFiles('STORE_ALL_BUILD')

                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                                } catch(exec){
                                    echo "No Coverage data collected"
                                }
                            }
                        }
                        cleanup{
                            cleanWs(patterns:
                                [
                                    [pattern: 'reports/coverage.xml', type: 'INCLUDE'],
                                    [pattern: 'reports/coverage', type: 'INCLUDE'],
                                    [pattern: 'scm/.coverage', type: 'INCLUDE']
                                ]
                            )

                        }
                    }
                }
            }
        }
        stage("Packaging") {
            environment{
                PATH = "${WORKSPACE}\\venv\\37\\Scripts;$PATH"
            }
            failFast true
            steps{
                dir("scm"){
                    bat script: "python setup.py build -b ${WORKSPACE}/build sdist -d ${WORKSPACE}/dist --format zip bdist_wheel -d ${WORKSPACE}/dist"
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: "dist/*.whl,dist/*.zip", fingerprint: true
                    stash includes: "dist/*.whl,dist/*.zip", name: 'PYTHON_PACKAGES'
                }
                cleanup{
                    cleanWs deleteDirs: true, patterns: [[pattern: 'dist/*.whl,dist/*.tar.gz,dist/*.zip', type: 'INCLUDE']]
                }
            }
        }
     }
     post {
        cleanup {
          cleanWs(
                deleteDirs: true,
                patterns: [
                    [pattern: 'dist', type: 'INCLUDE'],
                    [pattern: 'reports', type: 'INCLUDE'],
                    [pattern: 'logs', type: 'INCLUDE'],
                    [pattern: 'certs', type: 'INCLUDE'],
                    [pattern: 'mypy_stubs', type: 'INCLUDE'],
                    [pattern: '*tmp', type: 'INCLUDE'],
                    [pattern: "scm", type: 'INCLUDE'],
                    ]
                )
        }
      }

}