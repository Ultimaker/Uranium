node ('linux && cura') {
    stage('Prepare') {
        step([$class: 'WsCleanup'])

        checkout scm
    }

    dir('build') {
        stage('Build') {
            sh 'cmake .. -DCMAKE_PREFIX_PATH=/opt/ultimaker/cura-build-environment -DCMAKE_BUILD_TYPE=Release'
        }

        stage('Unit Test') {
            try {
                sh 'make test'
            } catch(e) {
                currentBuild.result = "UNSTABLE"
            }

            junit 'junit.xml'
        }

        stage('Lint') {
            try {
                sh 'make check'
            } catch(e) {
                currentBuild.result = "UNSTABLE"
            }

            step([
                $class: 'WarningsPublisher',
                canComputeNew: false,
                canResolveRelativePaths: false,
                defaultEncoding: '',
                excludePattern: '',
                healthy: '',
                includePattern: '',
                messagesPattern: '',
                parserConfigurations: [[parserName: 'PyLint', pattern: 'pylint.log']],
                unHealthy: ''
            ])
        }
    }
}
