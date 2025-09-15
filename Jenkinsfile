pipeline{
    agent any

    environment{
        VENV_DIR='venv'
    }

    stages{
        stage("Cloning Github repo to Jenkins"){
            steps{
                echo 'Cloning the Github repo to Jenkins......................'
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/hussainshaayan/ML_OPS_Project1.git']])
            }
        }

        stage("Setting up our Virtual Environment and Installing dependencies"){
            steps{
                echo 'Setting up our Environment......................'
                sh '''
                python -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -e .
                '''
            }
        }
    }
}

 