pipeline {
    agent any
    environment {
        FILE_PATH = "/var/lib/jenkins/jobs/previous_failed_builds.txt"
        EMAIL_RECIPIENTS = "shafeeqahamed1512@gmail.com, rithigasri383@gmail.com, jeevaabishake@gmail.com, yugannkt@gmail.com"
        PYTHON_SCRIPT_PATH = "/var/lib/jenkins/jobs/main.py"
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
        GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        BASE_URL = readFile("./BASE_URL.txt")
    }
    stages {
        stage('Detect Newly Failed Build') {
            steps {
                script {
                    try {
                        echo "BASE URL: ${BASE_URL}"
                        
                        echo "Starting 'Detect Newly Failed Build' stage"
                        // Read the content of the file containing previous failed builds
                        def fileContent = fileExists(env.FILE_PATH) ? readFile(env.FILE_PATH) : ""
                        // Get the names of all active jobs
                        def activeJobs = getActiveJobNames()
                        echo "Active jobs: ${activeJobs}"
                        def newFailedBuilds = []

                        // Iterate over each active job
                        activeJobs.each { jobName ->
                            if (jobName != env.JOB_NAME) {
                                // Get the job object
                                def job = Jenkins.instance.getItem(jobName)
                                // Get all failed builds for the job
                                def failedBuilds = job.getBuilds().findAll { it.result == hudson.model.Result.FAILURE }
                                echo "Failed builds for job ${jobName}: ${failedBuilds}"

                                // Iterate over each failed build
                                failedBuilds.each { failedBuild ->
                                    def failureEntry = "${jobName}:${failedBuild.getNumber()}"
                                    // Check if the failed build is not already recorded
                                    if (!fileContent.contains(failureEntry)) {
                                        // Get the console output of the failed build
                                        def consoleOutput = failedBuild.getLog(Integer.MAX_VALUE).join('\n')
                                        consoleOutput = consoleOutput.replace('\n', '\\n')
                                        // Add the new failed build to the list
                                        newFailedBuilds << "${jobName}:${failedBuild.getNumber()}:${consoleOutput}"
                                    }
                                }
                            }
                        }
                        // Write the new failed builds to a file if any
                        if (newFailedBuilds) {
                            writeFile file: 'failed_builds.txt', text: newFailedBuilds.join("\n")
                        } else {
                            echo "No new failed builds to summarize"
                        }
                    } catch (Exception e) {
                        echo "Error finding new failures: ${e.message}"
                    }
                }
            }
        }
        stage('Summarize Failures & Send Email') {
            steps {
                script {
                    try {
                        echo "Starting 'Summarize Failures' stage"
                        // Read the new failed builds from the file
                        def newFailedBuilds = fileExists('failed_builds.txt') ? readFile('failed_builds.txt').split("\n") : 0
                        if (!newFailedBuilds) {
                            echo "No new failed builds to summarize. Skipping Python and Gemini API call."
                        } else {
                            // Iterate over each new failed build
                            newFailedBuilds.each { failure ->
                                def details = failure.split(":",3)
                                def jobName = details[0]
                                def failID = details[1]
                                def consoleLog = details[2]
                                echo "Processing new failed builds - Job Name: ${jobName}, Build ID: ${failID}"

                                if (consoleLog?.trim()) {
                                    echo "Failed build Logs: ${consoleLog}"
                                    echo "Sending log to Gemini API for summarization..."
                                    
                                    // Properly escape the console log to handle special characters
                                    def escapedConsoleLog = consoleLog.replace("\n", "\\n").replace("\"", "\\\"")

                                    // Read the Python script from main.py
                                    def pythonScript = readFile(env.PYTHON_SCRIPT_PATH)

                                    def result = ""
                                    try {
                                        result = sh(
                                            script: """python3 "${env.PYTHON_SCRIPT_PATH}" --value "${escapedConsoleLog}" --api_key "${env.GEMINI_API_KEY}" --api_url "${env.GEMINI_API_URL}" """,
                                            returnStdout: true
                                        ).trim()
                                    } catch (Exception e) {
                                        echo "Error executing Python script: ${e.message}"
                                        result = "Error executing API summarization."
                                    }

                                    def response = sh(script: """
                                        curl -X 'POST' \
                                        '${BASE_URL}:8000/chatbot/load' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{
                                        "job_name": "${jobName}",
                                        "build_number": "${failID}",
                                        "log": "${escapedConsoleLog}"
                                    }'""", returnStdout: true).trim()
                
                                    // Extract unique_key from the JSON response
                                    def uniqueKey = sh(script: "echo '${response}' | jq -r '.unique_key'", returnStdout: true).trim()

                                    def parsedResult = [:]
                                    try {
                                        parsedResult = readJSON text: result
                                    } catch (Exception e) {
                                        echo "Error parsing API result: ${e.message}"
                                    }
                                    if (parsedResult?.errorType && parsedResult?.summary) {
                                        errorType = parsedResult.errorType
                                        summary = parsedResult.summary
                                    } else {
                                        errorType = "Unknown Error"
                                        summary = "Failed to retrieve summary."
                                    }

                                    echo "Summarization completed"

                                    echo "Error Type: ${errorType}"
                                    echo "Summary: ${summary}"
                                    echo "Unique Key: ${uniqueKey}"
                                    echo "Chat URL: ${BASE_URL}?chat=${uniqueKey}"


                                    // Construct URLs for the job and console
                                    def jobURL = "${Jenkins.instance.getRootUrl()}job/${jobName}/${failID}"
                                    def consoleURL = "${Jenkins.instance.getRootUrl()}job/${jobName}/${failID}/console"
                                    // Construct the email body
                                    def emailBody = """
                                        <p>Dear All,</p>
                                        <p>A new failed build has been detected:</p>
                                        <p><b>Job Name:</b> ${jobName}</p>
                                        <p><b>Build Number:</b> ${failID}</p>
                                        <p><b>Job URL:</b> <a href="${jobURL}">${jobURL}</a></p>
                                        <p><b>Console URL:</b> <a href="${consoleURL}">${consoleURL}</a></p>
                                        <p><b>Error Type:</b> ${errorType}</p>
                                        <p><b>Summary: </b> ${summary}</p>
                                        <p><b>Continue chat:</b>${BASE_URL}?chat=${uniqueKey}</p>
                                        <p>Regards,</p>
                                        <p>Jenkins Admin</p>
                                    """
                                    // Send the email notification
                                    mail to: env.EMAIL_RECIPIENTS,
                                         subject: "New Failed Build on ${jobName} ERROR: ${errorType}",
                                         body: emailBody,
                                         mimeType: 'text/html'

                                } else {
                                    echo "Skipping summarization: Empty or invalid console log."
                                }
                            }
                        }
                    } catch (Exception e) {
                        echo "Error during summarization: ${e.message}"
                    }
                }
            }
        }
        stage('Cleanup') {
            steps {
                script {
                    try {
                        echo "Starting 'Cleanup' stage"
                        // Read the new failed builds from the file
                        def newFailedBuilds = fileExists('failed_builds.txt') ? readFile('failed_builds.txt').split("\n") : []
                        if (newFailedBuilds) {
                            // Read the content of the file containing previous failed builds
                            def fileContent = fileExists(env.FILE_PATH) ? readFile(env.FILE_PATH) : ""
                            // Append the new failed builds to the file
                            writeFile file: env.FILE_PATH, text: fileContent + "\n" + newFailedBuilds.join("\n")
                            echo "File updated with new failed builds."
                            // Remove the temporary file containing new failed builds
                            sh "rm -rf failed_builds.txt"
                        }
                    } catch (Exception e) {
                        echo "Error during cleanup: ${e.message}"
                    }
                }
            }
        }
    }
}

// Helper functions
@NonCPS
def getActiveJobNames() {
    echo "Fetching active job names"
    // Get all active jobs
    def activeJobs = Jenkins.instance.getAllItems(hudson.model.Job.class)
    // Return the names of the active jobs
    return activeJobs.collect { it.name }
}
