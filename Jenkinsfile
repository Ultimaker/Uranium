node ('linux && cura') {
    // Prepare building
    stage('Prepare') {
        // Ensure we start with a clean build directory.
        step([$class: 'WsCleanup'])

        // Checkout whatever sources are linked to this pipeline.
        checkout scm
    }

    // If any error occurs during building, we want to catch it and continue with the "finale" stage.
    catchError {
        // Building and testing should happen in a subdirectory.
        dir('build') {
            // Perform the "build". Since Uranium is Python code, this basically only ensures CMake is setup.
            stage('Build') {
                // Ensure CMake is setup. Note that since this is Python code we do not really "build" it.
                sh 'cmake .. -DCMAKE_PREFIX_PATH=/opt/ultimaker/cura-build-environment -DCMAKE_BUILD_TYPE=Release'
            }

            // Try and run the unit tests. If this stage fails, we consider the build to be "unstable".
            stage('Unit Test') {
                try {
                    sh 'make test'
                } catch(e) {
                    currentBuild.result = "UNSTABLE"
                }
            }

            // Perform pylint checks on the source code. If this step fails, we do not consider it an error.
            stage('Lint') {
                try {
                    sh 'make check'
                } catch(e) {
                    currentBuild.result = "SUCCESS"
                }
            }
        }
    }

    // Perform any post-build actions like notification and publishing of unit tests.
    stage('Finalize') {
        // Publish the test results to Jenkins.
        junit 'build/junit*.xml'

        // Publish the pylint results to Jenkins.
        step([
            $class: 'WarningsPublisher',
            parserConfigurations: [[parserName: 'PyLint', pattern: 'build/pylint.log']],
        ])

        // If the job was not successful, send an email about it
        if(currentBuild.result && currentBuild.result != "SUCCESS")
        {
            // If our situation changed, send a different mail than if we are simply warning about the build still being broken.
            if(currentBuild.previousBuild && currentBuild.previousBuild.result != currentBuild.result)
            {
                emailext(
                    subject: "[Jenkins] Build ${currentBuild.fullDisplayName} has become ${currentBuild.result}",
                    body: "Jenkins build ${currentBuild.fullDisplayName} changed from ${currentBuild.previousBuild.result} to ${currentBuild.result}.\n\nPlease check the build output at ${env.BUILD_URL} for details.",
                    to: env.CURA_EMAIL_RECIPIENTS // Note: Using an environment variable for security reasons.
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
            if(currentBuild.previousBuild && currentBuild.previousBuild.result != currentBuild.result)
            {
                emailext(
                    subject: "[Jenkins] Build ${currentBuild.fullDisplayName} was fixed!",
                    body: "Jenkins build ${currentBuild.fullDisplayName} was ${currentBuild.previousBuild.result} but is now stable again.\n\nPlease check the build output at ${env.BUILD_URL} for details.",
                    to: env.CURA_EMAIL_RECIPIENTS
                )
            }

//             // Otherwise, trigger a build of cura-build
//             build "../../cura-build/master", wait: false
        }
    }
}
