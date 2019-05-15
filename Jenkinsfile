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
    stages {
        stage('Configure Environment') {
            environment{
                PATH = "${tool 'CPython-3.7'}\\Scripts"
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
                    [pattern: '*tmp', type: 'INCLUDE'],
                    [pattern: "scm", type: 'INCLUDE'],
                    ]
                )
        }
      }

}