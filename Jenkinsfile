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
            sh 'make test'

            junit 'build/junit.xml'
        }

        stage('Lint') {
            sh 'make check'
        }
    }
}
