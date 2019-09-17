@Library(["devpi", "PythonHelpers"]) _
def parseBanditReport(htmlReport){
    script {
        try{
            def summary = createSummary icon: 'warning.gif', text: "Bandit Security Issues Detected"
            summary.appendText(readFile("${htmlReport}"))

        } catch (Exception e){
            echo "Failed to reading ${htmlReport}"
        }
    }
}

def get_sonarqube_unresolved_issues(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'
        def response = httpRequest url : props['serverUrl'] + "/api/issues/search?componentKeys=" + props['projectKey'] + "&resolved=no"
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

def get_sonarqube_scan_data(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'

        def ceTaskUrl= props['ceTaskUrl']
        def response = httpRequest ceTaskUrl
        def ceTask = readJSON text: response.content

        def response2 = httpRequest url : props['serverUrl'] + "/api/qualitygates/project_status?analysisId=" + ceTask["task"]["analysisId"]
        def qualitygate =  readJSON text: response2.content
        return qualitygate
    }
}

def get_sonarqube_project_analysis(report_task_file, buildString){
    def props = readProperties  file: '.scannerwork/report-task.txt'
    def response = httpRequest url : props['serverUrl'] + "/api/project_analyses/search?project=" + props['projectKey']
    def project_analyses = readJSON text: response.content

    for( analysis in project_analyses['analyses']){
        if(!analysis.containsKey("buildString")){
            continue
        }
        def build_string = analysis["buildString"]
        if(build_string != buildString){
            continue
        }
        return analysis
    }
}

pipeline {
    agent {
        label 'Windows && Python3'
    }
    triggers {
        cron('@daily')
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(180)  // Timeout after 180 minutes. This shouldn't take this long
        checkoutToSubdirectory("scm")
        buildDiscarder logRotator(artifactDaysToKeepStr: '30', artifactNumToKeepStr: '30', daysToKeepStr: '100', numToKeepStr: '100')
    }
    environment{
        PKG_NAME = pythonPackageName(toolName: "CPython-3.7")
        PKG_VERSION = pythonPackageVersion(toolName: "CPython-3.7")
        DOC_ZIP_FILENAME = "${env.PKG_NAME}-${env.PKG_VERSION}.doc.zip"
        DEVPI = credentials("DS_devpi")
        DOCKER_IMAGE_TAG="tyko/${env.BRANCH_NAME.toLowerCase()}"
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        booleanParam(name: "BUILD_CLIENT", defaultValue: true, description: "Build Client program")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
        booleanParam(name: "DEPLOY_SERVER", defaultValue: false, description: "Deploy server software to server")
    }
    stages {
        stage('Configure Environment') {
            environment{
                PATH = "${tool 'CPython-3.7'};$PATH"
            }
            options{
                timeout(5)
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
                        bat "venv\\37\\Scripts\\pip.exe install -U setuptools wheel sqlalchemy  -r scm/requirements.txt --upgrade-strategy only-if-needed"
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
            failFast true
            parallel{
                stage("Building Server"){
                    environment{
                        PATH = "${WORKSPACE}\\venv\\37\\Scripts;$PATH"
                    }
                    steps{
                        dir("scm"){
                            bat "python setup.py build -b ${WORKSPACE}/build/server"
                        }
                    }
                    post{
                        success{
                            dir("scm"){
                                stash includes: "deploy/**,database/**", name: 'SERVER_DEPLOY_FILES'
                            }
                        }
                    }
                }
                stage("Build Client with Docker Container"){
                    agent{
                        label "Docker"
                    }
                    when {
                        equals expected: true, actual: params.BUILD_CLIENT
                    }
                    environment{
                        DOCKER_PATH = tool name: 'Docker', type: 'org.jenkinsci.plugins.docker.commons.tools.DockerTool'
                        PATH = "${DOCKER_PATH};$PATH"
                    }
                    options{
                        timestamps()
                    }

                    stages{
                        stage("Build Docker Container"){
                            steps{

                                dir("scm"){
                                     powershell(
                                        label: "Searching for opengl32.dll",
                                        script: '''
$opengl32_libraries = Get-ChildItem -Path c:\\Windows -Recurse -Include opengl32.dll
foreach($file in $opengl32_libraries){
    Copy-Item $file.FullName
    break
}'''
                                )
                                    bat("docker build . -f CI/build_VS2019/Dockerfile -m 10GB -t %DOCKER_IMAGE_TAG%")
                                }
                            }
                        }
                        stage("Install Dependencies"){
                            steps{
                                bat "if not exist build mkdir build"
                                bat(
                                    label: "Using conan to install dependencies to build directory.",
                                    script: "docker run -v \"${WORKSPACE}\\build:c:\\build\" -v \"${WORKSPACE}\\scm:c:\\source:ro\" --workdir=\"c:\\build\" --rm %DOCKER_IMAGE_TAG% conan install c:\\source"
                                    )
                            }
                        }
                        stage("Configure and Build Client"){
                            steps{
                                bat(
                                    label: "Configuring CMake",
                                    script: "docker run --rm -v \"${WORKSPACE}\\build:c:\\build\" -v \"${WORKSPACE}\\scm:c:\\source:ro\" --workdir=\"c:\\build\" %DOCKER_IMAGE_TAG% cmake -S c:\\source -B c:\\build -DCMAKE_TOOLCHAIN_FILE=conan_paths.cmake -DCMAKE_GENERATOR_PLATFORM=x64"
                                )
                                bat(
                                    label: "Running build command from CMake",
                                    script: "docker run --rm -v \"${WORKSPACE}\\build:c:\\build\" -v \"${WORKSPACE}\\scm:c:\\source:ro\" --workdir=\"c:\\build\" %DOCKER_IMAGE_TAG% cmake --build c:\\build --config Release"
                                )

                            }
                        }
                    }
                    post{
                        success{
                            stash includes: "build/**", name: 'CLIENT_BUILD_DOCKER'
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'build', type: 'INCLUDE'],
                                    ]
                            )
                        }

                    }
                }
            }
        }
        stage('Testing') {
            environment{
                PATH = "${WORKSPACE}\\venv\\37\\Scripts;$PATH"
            }
            options{
                timeout(10)
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
                                    catchError(buildResult: 'UNSTABLE', message: 'Did not pass all pytest tests', stageResult: 'UNSTABLE') {
                                        bat(
                                            label: "Run PyTest",
                                            script: "coverage run --parallel-mode --branch --source=tyko,tests -m pytest --junitxml=${WORKSPACE}/reports/pytest/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest"
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
                                    catchError(buildResult: 'SUCCESS', message: 'MyPy found issues', stageResult: 'UNSTABLE') {

                                        bat(
                                            script: "mypy -p tyko --cache-dir=${WORKSPACE}/mypy_cache --html-report ${WORKSPACE}\\reports\\mypy\\html > ${WORKSPACE}\\logs\\mypy.log && type ${WORKSPACE}\\logs\\mypy.log",
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
                                dir("scm"){
                                    catchError(buildResult: 'SUCCESS', message: 'Bandit found issues', stageResult: 'UNSTABLE') {
                                        bat(
                                            label: "Running bandit",
                                            script: "bandit --format json --output ${WORKSPACE}/reports/bandit-report.json --recursive ${WORKSPACE}\\scm\\tyko || bandit -f html --recursive ${WORKSPACE}\\scm\\tyko --output ${WORKSPACE}/reports/bandit-report.html"
                                            )
                                    }

                                }
                            }
                            post {
                                always {
                                    archiveArtifacts "reports/bandit-report.json,reports/bandit-report.html"
                                }
                                unstable{
                                    script{
                                        if(fileExists('reports/bandit-report.html')){
                                            parseBanditReport("reports/bandit-report.html")
                                            addWarningBadge text: "Bandit security issues detected", link: "${currentBuild.absoluteUrl}"
                                        }
                                    }
                                }
                            }
                        }
                        stage("Run Flake8 Static Analysis") {
                            steps{
                                dir("scm"){
                                    catchError(buildResult: 'SUCCESS', message: 'Flake8 found issues', stageResult: 'UNSTABLE') {

                                        bat(
                                            script: "flake8 tyko --tee --output-file=${WORKSPACE}\\logs\\flake8.log",
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
                         stage("Run Pylint Static Analysis") {
                            steps{
                                dir("scm"){
                                    catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                        bat(
                                            script: 'pylint tyko  -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > %WORKSPACE%\\reports\\pylint.txt & pylint tyko  -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > %WORKSPACE%\\reports\\pylint_issues.txt',
                                            label: "Running pylint"
                                        )
                                    }
                                }
                            }
                            post{
                                always{
                                    archiveArtifacts allowEmptyArchive: true, artifacts: "reports/pylint.txt"
                                    recordIssues(tools: [pyLint(pattern: 'reports/pylint_issues.txt')])
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
                stage("Run SonarQube Analysis"){
                    when{
                        equals expected: "master", actual: env.BRANCH_NAME
                    }

                    environment{
                        scannerHome = tool name: 'sonar-scanner-3.3.0', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

                    }
                    steps{
                        withSonarQubeEnv('sonarqube.library.illinois.edu') {
                            withEnv([
                                "PROJECT_DESCRIPTION=${bat(label: 'Getting description metadata', returnStdout: true, script: '@python scm/setup.py --description').trim()}"
                                ]) {

                                bat(
                                    label: "Running Sonar Scanner",
                                    script: "${env.scannerHome}/bin/sonar-scanner \
-Dsonar.projectBaseDir=${WORKSPACE}/scm \
-Dsonar.python.coverage.reportPaths=reports/coverage.xml \
-Dsonar.python.xunit.reportPath=reports/pytest/junit-${env.NODE_NAME}-pytest.xml \
-Dsonar.projectVersion=${PKG_VERSION} \
-Dsonar.python.bandit.reportPaths=${WORKSPACE}/reports/bandit-report.json \
-Dsonar.links.ci=${env.JOB_URL} \
-Dsonar.buildString=${env.BUILD_TAG} \
-Dsonar.analysis.packageName=${env.PKG_NAME} \
-Dsonar.analysis.buildNumber=${env.BUILD_NUMBER} \
-Dsonar.analysis.scmRevision=${env.GIT_COMMIT} \
-Dsonar.working.directory=${WORKSPACE}\\.scannerwork \
-Dsonar.python.pylint.reportPath=${WORKSPACE}\\reports\\pylint.txt \
-Dsonar.projectDescription=\"%PROJECT_DESCRIPTION%\" \
"
                                    )
                                }
                        }
                        script{

                            def sonarqube_result = waitForQualityGate abortPipeline: false
                            if(sonarqube_result.status != "OK"){
                                unstable("SonarQube quality gate: ${sonarqube_result}")
                            }
                            def sonarqube_data = get_sonarqube_scan_data(".scannerwork/report-task.txt")
                            echo sonarqube_data.toString()

                            echo get_sonarqube_project_analysis(".scannerwork/report-task.txt", BUILD_TAG).toString()
                            def outstandingIssues = get_sonarqube_unresolved_issues(".scannerwork/report-task.txt")
                            writeJSON file: 'reports/sonar-report.json', json: outstandingIssues
                        }
                    }
                    post{
                        always{
                            archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                            recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
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
                            [pattern: 'scm/**/__pycache__', type: 'INCLUDE'],
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
            options{
                timeout(10)
            }
            failFast true
            parallel{
                stage("Creating Python Packages"){

                    steps{
                        dir("scm"){
                            bat script: "python setup.py build -b ${WORKSPACE}/build/server sdist -d ${WORKSPACE}/dist --format zip bdist_wheel -d ${WORKSPACE}/dist"
                        }
                    }
                }
                stage("Packaging Client in Docker Container"){
                    agent{
                        label "Docker"

                    }
                    when {
                        equals expected: true, actual: params.BUILD_CLIENT
                    }
                    environment{
                        DOCKER_PATH = tool name: 'Docker', type: 'org.jenkinsci.plugins.docker.commons.tools.DockerTool'
                        PATH = "${DOCKER_PATH};$PATH"
                    }
                    steps{
                            unstash "CLIENT_BUILD_DOCKER"
                            bat "if not exist dist mkdir dist"
                            bat(
                                label: "Running build command from CMake on node ${NODE_NAME}",
                                script: "docker run --rm -v \"${WORKSPACE}\\build:c:\\build:rw\" -v \"${WORKSPACE}\\dist:c:\\dist\" -v \"${WORKSPACE}\\scm:c:\\source:ro\" -v \"${WORKSPACE}\\scm\\CI\\shared_docker_scripts:c:\\ci_scripts:ro\" --workdir=\"c:\\TEMP\" %DOCKER_IMAGE_TAG% C:\\ci_scripts\\package.bat"
                            )
                    }
                    post{
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'build', type: 'INCLUDE'],
                                    [pattern: 'dist', type: 'INCLUDE'],
                                    ]
                            )
                        }
                        failure{
                            archiveArtifacts allowEmptyArchive: true, artifacts: 'build/**/*.log'
                        }
                        success{
                            archiveArtifacts allowEmptyArchive: true, artifacts: 'dist/*.exe,dist/*.msi,dist/*.zip'
                            stash includes: 'dist/*.exe,dist/*.msi,dist/*.zip,', name: "CLIENT_INSTALLERS"
                        }
                    }
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: "dist/*.whl,dist/*.zip", fingerprint: true
                    stash includes: "dist/*.whl,dist/*.zip", name: 'PYTHON_PACKAGES'
                }
                unstable {
                    archiveArtifacts artifacts: "dist/*.whl,dist/*.zip", fingerprint: true
                    stash includes: "dist/*.whl,dist/*.zip", name: 'PYTHON_PACKAGES'
                }

                cleanup{
                    cleanWs deleteDirs: true, patterns: [[pattern: 'dist/*.whl,dist/*.tar.gz,dist/*.zip', type: 'INCLUDE']]
                }
            }
        }
        stage("Deploy"){
            parallel{
                stage("Deploy Server"){
                    agent any
                    options {
                      skipDefaultCheckout true
                    }
                    when{
                        equals expected: true, actual: params.DEPLOY_SERVER
                    }
                    stages{
                        stage("Deploy"){

                            input {
                              message 'Deploy to server'
                              parameters {
                                string(defaultValue: 'avdatabase.library.illinois.edu', description: 'Location where to install the server application', name: 'SERVER_URL', trim: false)
                                credentials credentialType: 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl', defaultValue: 'henryUserName', description: '', name: 'SERVER_CREDS', required: false
                              }
                            }

                            steps{
                                unstash "PYTHON_PACKAGES"
                                unstash "SERVER_DEPLOY_FILES"
                                script{
                                    def remote = [:]

                                    withCredentials([usernamePassword(credentialsId: SERVER_CREDS, passwordVariable: 'password', usernameVariable: 'username')]) {
                                        remote.name = 'test'
                                        remote.host = SERVER_URL
                                        remote.user = username
                                        remote.password = password
                                        remote.allowAnyHosts = true
                                    }
                                    sshRemove remote: remote, path: "package", failOnError: false
                                    sshCommand remote: remote, command: "mkdir package"
                                    sshPut remote: remote, from: 'dist', into: './package/'
                                    sshPut remote: remote, from: 'deploy', into: './package/'
                                    sshPut remote: remote, from: 'database', into: './package/'
                                    sshCommand remote: remote, command: """cd package &&
docker-compose -f deploy/docker-compose.yml -p avdatabase build &&
docker-compose -f deploy/docker-compose.yml -p avdatabase up -d"""
                                }
                                addBadge(icon: 'success.gif', id: '', link: 'http://avdatabase.library.illinois.edu:8000/', text: 'Server Application Deployed')
                            }
                        }
                    }
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
