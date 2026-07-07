pipeline {
    agent any

    stages {
        stage('Trigger Alerts') {
            steps {
                build job: 'alerts-worker-pipeline', wait: true
            }
        }

        stage('Trigger Digest') {
            steps {
                build job: 'digest-worker-pipeline', wait: true
            }
        }

        stage('Trigger Geo') {
            steps {
                build job: 'geo-worker-pipeline', wait: true
            }
        }

        stage('Trigger Greenhouse') {
            steps {
                build job: 'greenhouse-scraper-pipeline', wait: true
            }
        }

        stage('Trigger Job') {
            steps {
                build job: 'job-worker-pipeline', wait: true
            }
        }

        stage('Trigger Jobicy') {
            steps {
                build job: 'jobicy-scraper-pipeline', wait: true
            }
        }

        stage('Trigger Leaderboard') {
            steps {
                build job: 'leaderboard-worker-pipeline', wait: true
            }
        }

        stage('Trigger Personalization') {
            steps {
                build job: 'personalization-worker-pipeline', wait: true
            }
        }

        stage('Trigger Remotive') {
            steps {
                build job: 'remotive-scraper-pipeline', wait: true
            }
        }
    }
}