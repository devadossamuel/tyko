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
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
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
                        // Bandit version 1.6 exclude the directories doesn't work
                        bat 'pip install "tox<3.10" pytest pytest-bdd mypy flake8 coverage lxml pylint sqlalchemy-stubs "bandit<1.6'
                    }
                }
                stage("Running Tests"){
                    parallel {
                        stage("PyTest"){
                            steps{
                                dir("scm"){
                                    catchError(buildResult: hudson.model.Result.UNSTABLE, message: 'Did not pass all pytest tests', stageResult: hudson.model.Result.UNSTABLE) {
                                        bat(
                                            label: "Run PyTest",
                                            script: "coverage run --parallel-mode --branch --source=avforms,tests,setup.py -m pytest --junitxml=${WORKSPACE}/reports/pytest/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest"
                                        )
                                    }
                                }
                            }
                            post {
                                always{
                                    junit "reports/pytest/junit-*.xml"
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
                            steps{
                                bat "if not exist reports\\mypy\\html mkdir reports\\mypy\\html"
                                dir("scm"){
                                    catchError(buildResult: hudson.model.Result.SUCCESS, message: 'MyPy found issues', stageResult: hudson.model.Result.UNSTABLE) {

                                        bat(returnStatus: true,
                                            script: "mypy -p avforms ${env.scannerHome} --cache-dir=${WORKSPACE}/mypy_cache --html-report ${WORKSPACE}\\reports\\mypy\\html > ${WORKSPACE}\\logs\\mypy.log && type ${WORKSPACE}\\logs\\mypy.log",
                                            label: "Running MyPy"
                                            )
                                    }

                                }
                            }
                            post {
                                always {
                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/mypy/html/", reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                }
                            }
                        }
                        stage("Run Bandit Static Analysis") {
                            steps{
                                bat(
                                    label: "Creating report directories for Bandit reports",
                                    script: """if not exist reports\\bandit\\json mkdir reports\\bandit\\json
if not exist reports\\bandit\\txt mkdir reports\\bandit\\txt"""
                                )
                                dir("scm"){
                                    catchError(buildResult: hudson.model.Result.SUCCESS, message: 'Bandit found issues', stageResult: hudson.model.Result.UNSTABLE) {
                                        bat(
                                            label: "Running bandit",
                                            script: "bandit --format json --output ${WORKSPACE}/reports/bandit/json/bandit-report.json --format txt --output ${WORKSPACE}/reports/bandit/txt/bandit-report.txt --recursive ${WORKSPACE}\\scm --exclude ${WORKSPACE}\\scm\\.eggs",
                                            )
                                    }

                                }
                            }
                            post {
                                always {
                                    archiveArtifacts "reports/bandit/json/bandit-report.json"
                                    archiveArtifacts "reports/bandit/txt/bandit-report.txt"
                                }
                            }
                        }
                        stage("Run Flake8 Static Analysis") {
                            steps{
                                dir("scm"){
                                    catchError(buildResult: hudson.model.Result.SUCCESS, message: 'Flake8 found issues', stageResult: hudson.model.Result.UNSTABLE) {

                                        bat(
                                            script: "flake8 avforms --tee --output-file=${WORKSPACE}\\logs\\flake8.log",
                                            label: "Running Flake8"
                                        )
                                    }
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

                    }
                }
                stage("Run Sonarqube Analysis"){
                    when{
                        equals expected: "master", actual: env.BRANCH_NAME
                    }

                    environment{
                        scannerHome = tool name: 'sonar-scanner-3.3.0', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

                    }
                    steps{
                        withSonarQubeEnv('sonarqube.library.illinois.edu') {
                            withEnv([
                                "PROJECT_HOMEPAGE=${bat(label: 'Getting url metadata', returnStdout: true, script: '@python scm/setup.py --url').trim()}",
                                "PROJECT_DESCRIPTION=${bat(label: 'Getting description metadata', returnStdout: true, script: '@python scm/setup.py --description').trim()}"
                                ]) {

                                bat(
                                    label: "Running Sonar Scanner",
                                    script: "${env.scannerHome}/bin/sonar-scanner \
-Dsonar.projectKey=avdatabase -Dsonar.sources=. \
-Dsonar.projectBaseDir=${WORKSPACE}/scm \
-Dsonar.python.coverage.reportPaths=reports/coverage.xml \
-Dsonar.python.xunit.reportPath=reports/pytest/junit-${env.NODE_NAME}-pytest.xml \
-Dsonar.projectVersion=${PKG_VERSION} \
-Dsonar.python.bandit.reportPaths=${WORKSPACE}/reports/bandit-report.json \
-Dsonar.links.ci=${env.JOB_URL} \
-Dsonar.links.homepage=${env.PROJECT_HOMEPAGE} \
-Dsonar.buildString=${env.BUILD_TAG} \
-Dsonar.analysis.packageName=${env.PKG_NAME} \
-Dsonar.projectDescription=\"%PROJECT_DESCRIPTION%\" \
-X "
                                    )
                                }
                        }

                    }
                }
            }
            post{
                cleanup{
                    cleanWs(patterns:
                        [
                            [pattern: 'reports/coverage.xml', type: 'INCLUDE'],
                            [pattern: 'reports/coverage', type: 'INCLUDE'],
                            [pattern: 'scm/.coverage', type: 'INCLUDE'],
                            [pattern: 'reports/pytest/junit-*.xml', type: 'INCLUDE']
                        ]
                    )

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