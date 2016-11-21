node ('linux && cura') {
    stage('Prepare') {
        step([$class: 'WsCleanup'])

        checkout scm
    }

    stage('Build') {
        sh 'cmake . -DCMAKE_PREFIX_PATH=/opt/ultimaker/cura-build-environment -DCMAKE_BUILD_TYPE=Release'
    }

    stage('Unit Test') {
        sh 'make test'
    }

    stage('Lint') {
        sh 'make check'
    }

    stage('Archive') {
    }
}
