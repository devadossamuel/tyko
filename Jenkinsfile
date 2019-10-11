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
//         PKG_NAME = pythonPackageName(toolName: "CPython-3.7")
//         PKG_VERSION = pythonPackageVersion(toolName: "CPython-3.7")
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
//        stage('Configure Environment') {
//            environment{
//                PATH = "${tool 'CPython-3.7'};$PATH"
//            }
//            options{
//                timeout(5)
//            }
//            stages{
//                stage("Purge All Existing Data in Workspace"){
//                    when{
//                        anyOf{
//                            equals expected: true, actual: params.FRESH_WORKSPACE
//                            triggeredBy "TimerTriggerCause"
//                        }
//                    }
//                    steps{
//                        deleteDir()
//                        dir("scm"){
//                            checkout scm
//                        }
//                    }
//                }
//            }
//            post{
//                failure {
//                    deleteDir()
//                }
//                success{
//                    echo "Configured ${env.PKG_NAME}, version ${env.PKG_VERSION}, for testing."
//                }
//            }
//        }
        stage("Building"){
            failFast true
            parallel{
                stage("Building Server"){
                    agent {
                      dockerfile {
                        filename 'CI/server_testing/Dockerfile'
                        label "linux && docker"
                        dir 'scm'
                      }
                    }
                    steps{
                        dir("scm"){
                            sh "python setup.py build -b ../build/server dist_info"
                        }
                    }
                    post{
                        success{
                            dir("scm"){
                                stash includes: "deploy/**,database/**", name: 'SERVER_DEPLOY_FILES'
                                stash includes: "tyko.dist-info/**", name: 'DIST-INFO'

                            }

                        }
                        cleanup{
                            cleanWs()
                        }
                    }
                }
                stage("Build Client with Docker Container"){
                    agent{
                        label "Docker && Windows && 1903"
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
                                    script{
                                        if(!fileExists('opengl32.dll')){
                                            node('Windows&&opengl32') {
                                                powershell(
                                                    label: "Searching for opengl32.dll",
                                                    script: '''
$opengl32_libraries = Get-ChildItem -Path c:\\Windows\\System32 -Recurse -Include opengl32.dll
foreach($file in $opengl32_libraries){
    Copy-Item $file.FullName
    break
}'''
                                                )
                                                stash includes: 'opengl32.dll', name: 'OPENGL'
                                            }
                                            unstash 'OPENGL'
                                        }
                                    }

                                    bat("docker build . -f CI/build_VS2019/Dockerfile -m 2GB -t %DOCKER_IMAGE_TAG%")
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
                                    script: "docker run --rm -v \"${WORKSPACE}\\build:c:\\build\" -v \"${WORKSPACE}\\scm:c:\\source:ro\" --workdir=\"c:\\build\" %DOCKER_IMAGE_TAG% cmake -G Ninja -S c:\\source -B c:\\build -DCMAKE_TOOLCHAIN_FILE=conan_paths.cmake -DCMAKE_BUILD_TYPE=Release"
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

            options{
                timeout(10)
            }
            stages{
                stage("Running Tests"){
                    parallel {
                        stage("PyTest"){
                            agent {
                              dockerfile {
                                filename 'CI/server_testing/Dockerfile'
                                label "linux && docker"
                                dir 'scm'
                              }
                            }
                            steps{
                                sh "mkdir -p reports/pytest"
                                dir("scm"){
                                    catchError(buildResult: 'UNSTABLE', message: 'Did not pass all pytest tests', stageResult: 'UNSTABLE') {
                                        sh(
                                            label: "Run PyTest",
                                            script: "coverage run --parallel-mode --branch --source=tyko,tests -m pytest --junitxml=../reports/pytest/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest"
                                        )
                                    }
                                }
                            }
                            post {
                                always{
                                    stash includes: "scm/.coverage.*,reports/pytest/junit-*.xml", name: 'PYTEST_COVERAGE_DATA'
                                    junit "reports/pytest/junit-*.xml"
                                    dir("scm"){
                                        sh "coverage combine"
                                        sh "coverage xml -o ../reports/coverage.xml"
                                    }

                                    publishCoverage(
                                        adapters: [
                                                coberturaAdapter('reports/coverage.xml')
                                                ],
                                        sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                                        )
                                }
                                cleanup{
                                    cleanWs()
                                }
                            }
                        }
                        stage("Tox") {
                            when {
                                equals expected: true, actual: params.TEST_RUN_TOX
                            }
                            agent {
                              dockerfile {
                                filename 'CI/server_testing/Dockerfile'
                                label "linux && docker"
                                dir 'scm'
                              }
                            }
                            steps {
                                sh "mkdir -p logs"
                                dir("scm"){
                                    script{
                                        try{
                                            sh (
                                                label: "Run Tox",
                                                script: "tox --parallel=auto --parallel-live --workdir ../.tox -vv --result-json=../logs/tox_report.json"
                                            )

                                        } catch (exc) {
                                            sh(
                                                label: "Run Tox with new environments",
                                                script: "tox --recreate --parallel=auto --parallel-live --workdir ../.tox -vv --result-json=../logs/tox_report.json"
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
                                    cleanWs()
                                }
                            }
                        }
                        stage("Run MyPy Static Analysis") {
                            agent {
                              dockerfile {
                                filename 'CI/server_testing/Dockerfile'
                                label "linux && docker"
                                dir 'scm'
                              }
                            }
                            steps{
                                sh "mkdir -p reports/mypy/html"
                                sh "mkdir -p logs"
                                tee('logs/mypy.log') {
                                    dir("scm"){
                                        catchError(buildResult: 'SUCCESS', message: 'MyPy found issues', stageResult: 'UNSTABLE') {
                                            sh(
                                                script: "mypy tyko --html-report ../reports/mypy/html",
                                                label: "Running MyPy"
                                                )
                                        }

                                    }
                                }
                            }
                            post {
                                always {
                                    stash includes: "logs/mypy.log", name: 'MYPY_LOGS'
                                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/mypy/html/", reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                        dir("scm"){
                                            unstash "MYPY_LOGS"
                                            recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                        }
                                }
                                cleanup{
                                    cleanWs()
                                }
                            }
                        }
                        stage("Run Bandit Static Analysis") {
                            agent {
                              dockerfile {
                                filename 'CI/server_testing/Dockerfile'
                                label "linux && docker"
                                dir 'scm'
                              }
                            }
                            steps{
                                sh "mkdir -p reports"
                                dir("scm"){
                                    catchError(buildResult: 'SUCCESS', message: 'Bandit found issues', stageResult: 'UNSTABLE') {
                                        sh(
                                            label: "Running bandit",
                                            script: "bandit --format json --output ../reports/bandit-report.json --recursive ../scm/tyko ||  bandit -f html --recursive ../scm/tyko --output ../reports/bandit-report.html"
                                        )
                                    }

                                }
                            }
                            post {
                                always {
                                    archiveArtifacts "reports/bandit-report.json,reports/bandit-report.html"
                                    stash includes: "reports/bandit-report.json", name: 'BANDIT_REPORT'
                                }
                                unstable{
                                    script{
                                        if(fileExists('reports/bandit-report.html')){
                                            parseBanditReport("reports/bandit-report.html")
                                            addWarningBadge text: "Bandit security issues detected", link: "${currentBuild.absoluteUrl}"
                                        }
                                    }
                                }
                                cleanup{
                                    cleanWs()
                                }
                            }
                        }
                        stage("Run Flake8 Static Analysis") {
                            agent {
                              dockerfile {
                                filename 'CI/server_testing/Dockerfile'
                                label "linux && docker"
                                dir 'scm'
                              }
                            }
                            steps{
                                sh "mkdir -p logs"
                                dir("scm"){
                                    catchError(buildResult: 'SUCCESS', message: 'Flake8 found issues', stageResult: 'UNSTABLE') {

                                        sh(
                                            script: "flake8 tyko --tee --output-file=../logs/flake8.log",
                                            label: "Running Flake8"
                                        )
                                    }
                                }
                            }
                            post {
                                always {
                                    stash includes: "logs/flake8.log", name: 'FLAKE8_LOGS'
                                    archiveArtifacts 'logs/flake8.log'
                                    dir('scm') {
                                        unstash "FLAKE8_LOGS"
                                        recordIssues(tools: [flake8(pattern: 'logs/flake8.log')])
                                    }

                                }
                                cleanup{
                                    cleanWs(patterns: [[pattern: 'logs/flake8.log', type: 'INCLUDE']])
                                }
                            }
                        }
                         stage("Run Pylint Static Analysis") {
                            agent {
                              dockerfile {
                                filename 'CI/server_testing/Dockerfile'
                                label "linux && docker"
                                dir 'scm'
                              }
                            }
                            environment{
                                PYLINTHOME="."
                            }
                            steps{
                                sh "mkdir -p reports"
                                dir("scm"){

                                    catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                        sh(
                                            script: 'pylint tyko  -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > ../reports/pylint.txt',
                                            label: "Running pylint"
                                        )
                                    }
                                    sh(
                                        script: 'pylint tyko  -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > ../reports/pylint_issues.txt',
                                        label: "Running pylint for sonarqube",
                                        returnStatus: true
                                    )
                                }
                            }
                            post{
                                always{
                                    stash includes: "reports/pylint_issues.txt", name: 'PYLINT_REPORT'
                                    archiveArtifacts allowEmptyArchive: true, artifacts: "reports/pylint.txt"
                                    dir("scm"){
                                        unstash "PYLINT_REPORT"
                                        recordIssues(tools: [pyLint(pattern: 'reports/pylint_issues.txt')])
                                    }
                                }
                                cleanup{
                                    cleanWs()
                                }
                            }
                        }
                    }
                }
                stage("Run SonarQube Analysis"){
                    agent{
                        dockerfile {
                            filename 'CI/sonarqube/scanner/Dockerfile'
                            label "linux && docker"
                            dir 'scm'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            }
                    }
                    when{
                        equals expected: "master", actual: env.BRANCH_NAME
                    }

                    steps{
                        unstash "DIST-INFO"
                        unstash "PYLINT_REPORT"
                        unstash "BANDIT_REPORT"
                        script{
                                def props = readProperties interpolate: true, file: 'tyko.dist-info/METADATA'
                            withSonarQubeEnv('sonarqube.library.illinois.edu') {
                                sh(
                                    label: "Running Sonar Scanner",
                                    script: "sonar-scanner \
-Dsonar.projectBaseDir=${WORKSPACE}/scm \
-Dsonar.python.coverage.reportPaths=reports/coverage.xml \
-Dsonar.python.xunit.reportPath=reports/pytest/junit-${env.NODE_NAME}-pytest.xml \
-Dsonar.projectVersion=${props.Version} \
-Dsonar.python.bandit.reportPaths=${WORKSPACE}/reports/bandit-report.json \
-Dsonar.links.ci=${env.JOB_URL} \
-Dsonar.buildString=${env.BUILD_TAG} \
-Dsonar.analysis.packageName=${props.Name} \
-Dsonar.analysis.buildNumber=${env.BUILD_NUMBER} \
-Dsonar.analysis.scmRevision=${env.GIT_COMMIT} \
-Dsonar.working.directory=${WORKSPACE}/.scannerwork \
-Dsonar.python.pylint.reportPath=${WORKSPACE}/reports/pylint.txt \
-Dsonar.projectDescription=\"${props.Summary}\" \
-X \
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
                            stash includes: "reports/sonar-report.json", name: 'SONAR_REPORT'
                            archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                            dir("scm"){
                                unstash "SONAR_REPORT"
                                recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
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
                            [pattern: 'scm/**/__pycache__', type: 'INCLUDE'],
                            [pattern: 'reports/pytest/junit-*.xml', type: 'INCLUDE']
                        ]
                    )

                }
            }
        }
        stage("Packaging") {

            options{
                timeout(10)
            }
            failFast true
            parallel{
                stage("Creating Python Packages"){
                    agent {
                      dockerfile {
                        filename 'CI/server_testing/Dockerfile'
                        label "linux && docker"
                        dir 'scm'
                      }
                    }
                    steps{
                        dir("scm"){
                            sh script: "python setup.py sdist -d ../dist --format zip bdist_wheel -d ../dist"
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
                            cleanWs()
                        }
                    }
                }
                stage("Packaging Client in Docker Container"){
                    agent{
                        label "Docker && Windows && 1903"

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
                                script: "docker run --rm -v \"${WORKSPACE}\\build:c:\\build:rw\" -v \"${WORKSPACE}\\dist:c:\\dist\" -v \"${WORKSPACE}\\scm:c:\\source:rw\" -v \"${WORKSPACE}\\scm\\CI\\shared_docker_scripts:c:\\ci_scripts:ro\" --workdir=\"c:\\build\" %DOCKER_IMAGE_TAG% cpack -G NSIS;WIX;ZIP -C Release --verbose"
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
                            archiveArtifacts allowEmptyArchive: true, artifacts: 'build/*.exe,build/*.msi,build/*.zip'
                            stash includes: 'build/*.exe,build/*.msi,build/*.zip,', name: "CLIENT_INSTALLERS"
                        }
                    }
                }
            }

        }
        stage("Deploy"){
            parallel{
                stage("Deploy Server"){
                    agent {
                        label "!aws"
                    }
                    options {
                      skipDefaultCheckout true
                    }
                    when{
                        equals expected: true, actual: params.DEPLOY_SERVER
                        beforeInput true
                    }
                    input {
                      message 'Deploy to server'
                      parameters {
                        string(defaultValue: 'avdatabase.library.illinois.edu', description: 'Location where to install the server application', name: 'SERVER_URL', trim: false)
                        string(defaultValue: 'avdatabase_db_1', description: 'Name of the container with the database', name: 'CONTAINER_NAME_DATABASE', trim: false)
                        credentials credentialType: 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl', defaultValue: 'henryUserName', description: '', name: 'SERVER_CREDS', required: false
                        credentials credentialType: 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl', defaultValue: 'TYKO_DB_CREDS', description: '', name: 'DATABASE_CREDS', required: false
                      }
                    }
                    stages{
                        stage("Backing up database"){
                            steps{
                                script{
                                    def remote = [:]

                                    withCredentials([usernamePassword(credentialsId: SERVER_CREDS, passwordVariable: 'password', usernameVariable: 'username')]) {
                                        remote.name = 'test'
                                        remote.host = SERVER_URL
                                        remote.user = username
                                        remote.password = password
                                        remote.allowAnyHosts = true
                                    }

                                    def backup_file_name = "tyko-${BRANCH_NAME}-${BUILD_NUMBER}-backup.sql"
                                    catchError(buildResult: 'SUCCESS', message: 'Unable to make a backup of database', stageResult: 'UNSTABLE') {
                                        withCredentials([usernamePassword(credentialsId: DATABASE_CREDS, passwordVariable: 'password', usernameVariable: 'username')]) {
                                            sshCommand(
                                                remote: remote,
                                                command: "docker exec ${CONTAINER_NAME_DATABASE} /bin/bash -c \"mysqldump av_preservation --user='${username}' --password='${password}' > /tmp/${backup_file_name}\" && docker cp avdatabase_db_1:/tmp/${backup_file_name} ~/backups/"
                                                )
                                        }
                                    }
                                }

                            }
                        }
                        stage("Deploying New Server"){

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
                                    sshPut remote: remote, from: 'setup.py', into: './package/'
                                    sshPut remote: remote, from: 'setup.cfg', into: './package/'
                                    sshPut remote: remote, from: 'tyko', into: './package/'
                                    sshPut remote: remote, from: 'requirements.txt', into: './package/'
                                    sshPut remote: remote, from: 'dist', into: './package/'
                                    sshPut remote: remote, from: 'deploy', into: './package/'
                                    sshPut remote: remote, from: 'database', into: './package/'
                                    sshCommand remote: remote, command: """cd package &&
        docker-compose -f deploy/docker-compose.yml -p avdatabase build &&
        docker-compose -f deploy/docker-compose.yml -p avdatabase up -d"""
                                }
                                addBadge(icon: 'success.gif', id: '', link: "http://${SERVER_URL}:8000/", text: 'Server Application Deployed')
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
