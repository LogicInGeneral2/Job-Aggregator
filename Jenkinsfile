pipeline {
    agent any
    stages {
        stage('Trigger Workers') {
            parallel {
                stage('Alerts') {
                    steps { build job: 'alerts-worker-pipeline', wait: false }
                }
                stage('Digest') {
                    steps { build job: 'digest-worker-pipeline', wait: false }
                }
                stage('Geo') {
                    steps { build job: 'geo-worker-pipeline', wait: false }
                }
                stage('Greenhouse') {
                    steps { build job: 'greenhouse-scraper-pipeline', wait: false }
                }
                stage('Job') {
                    steps { build job: 'job-worker-pipeline', wait: false }
                }
                stage('Jobicy') {
                    steps { build job: 'jobicy-scraper-pipeline', wait: false }
                }
                stage('Leaderboard') {
                    steps { build job: 'leaderboard-worker-pipeline', wait: false }
                }
                stage('Personalization') {
                    steps { build job: 'personalization-worker-pipeline', wait: false }
                }
                stage('Remotive') {
                    steps { build job: 'remotive-scraper-pipeline', wait: false }
                }
            }
        }
    }
}