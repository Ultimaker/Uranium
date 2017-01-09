node ('linux && cura') {
    // Step to prepare building
    stage('Prepare') {
        // Ensure we start with a clean build directory.
        step([$class: 'WsCleanup'])

        // Checkout whatever sources are linked to this pipeline.
        checkout scm
    }

    // Perform the actual build and test runs in a "build" subdirectory of the current workspace.
    catchError {
        dir('build') {
            stage('Build') {
                // Ensure CMake is setup. Note that since this is Python code we do not really "build" it.
                sh 'cmake .. -DCMAKE_PREFIX_PATH=/opt/ultimaker/cura-build-environment -DCMAKE_BUILD_TYPE=Release'
            }

            stage('Unit Test') {
                // Try and run the unit tests. If this step fails, we consider the build to be "unstable".
                try {
                    sh 'make test'
                } catch(e) {
                    currentBuild.result = "UNSTABLE"
                }
            }

            stage('Lint') {
                // Perform pylint checks on the source code. If this step fails, we do not consider it an error.
                try {
                    sh 'make check'
                } catch(e) {
                    currentBuild.result = "SUCCESS"
                }
            }
        }
    }

    stage('Finalize') {
        // Publish the test results to Jenkins.
        junit 'build/junit.xml'

        // Publish the pylint results to Jenkins.
        step([
            $class: 'WarningsPublisher',
            parserConfigurations: [[parserName: 'PyLint', pattern: 'pylint.log']],
        ])

        // If the job was not successful, send an email about it
        if(currentBuild.result != "SUCCESS")
        {
            // If our situation changed, send a different mail than if we are simply warning about the build still being broken.
            if(currentBuild.previousBuild.result != currentBuild.result)
            {
                emailext(
                    subject: "[Jenkins] Build ${currentBuild.fullDisplayName} has become ${currentBuild.result}",
                    body: "Jenkins build ${currentBuild.fullDisplayName} changed from ${currentBuild.previousBuild.result} to ${currentBuild.result}.\n\nPlease check the build output at ${env.BUILD_URL} for details.",
                    to: env.CURA_EMAIL_RECIPIENTS
                )
            }
            else
            {
                emailext (
                    subject: "[Jenkins] Build ${currentBuild.fullDisplayName} is ${currentBuild.result}",
                    body: "Jenkins build ${currentBuild.fullDisplayName} is ${currentBuild.result}\n\nPlease check the build output at ${env.BUILD_URL} for details.",
                    to: env.CURA_EMAIL_RECIPIENTS
                )
            }
        }
        else
        {
            // Send an email to indicate build was fixed
            if(currentBuild.previousBuild.result != currentBuild.result)
            {
                emailext(
                    subject: "[Jenkins] Build ${currentBuild.fullDisplayName} was fixed!",
                    body: "Jenkins build ${currentBuild.fullDisplayName} changed from ${currentBuild.previousBuild.result} to ${currentBuild.result}.\n\nPlease check the build output at ${env.BUILD_URL} for details.",
                    to: env.CURA_EMAIL_RECIPIENTS
                )
            }

//             // Otherwise, trigger a build of cura-build
//             build "../../cura-build/master", wait: false
        }
    }
}
