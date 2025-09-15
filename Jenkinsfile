pipeline{
    agent any

    stages{
        stage("Cloning Github repo to Jenkins"){
            steps{
                echo 'Cloning the Github repo to Jenkins......................'
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/hussainshaayan/ML_OPS_Project1.git']])
            }
        }
    }
}

