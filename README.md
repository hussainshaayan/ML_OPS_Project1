# End-to-End ML Ops Project (MLflow + Docker + Jenkins + GCP)

This repository contains an end-to-end ML Ops workflow that uses
**MLflow, Docker, Jenkins, and Google Cloud Platform (GCP)** to build,
train, deploy, and serve a machine learning model.

------------------------------------------------------------------------

## 🚀 1. Local Development Setup

### Create a virtual environment

``` bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### Push project to GitHub

``` bash
git init
git add .
git commit -m "Initial commit - ML Ops project"
git branch -M main
git remote add origin https://github.com/<user>/ML_OPS_First_Project.git
git push -u origin main
```

------------------------------------------------------------------------

## 📝 2. Core Python Modules

-   **logger.py** → Centralized logging\
-   **custom_exception.py** → Unified error handling\
-   **common_functions.py** → YAML reader & data loader\
-   **data_ingestion.py** → Downloads raw CSV from GCP bucket & splits
    train/test\
-   **data_preprocessing.py** → Cleans data, encodes, balances classes
    (SMOTE), feature selection\
-   **model_training.py** → Trains LightGBM with hyperparameter tuning,
    logs metrics in MLflow\
-   **application.py** → Flask app to serve predictions

Run modules locally:

``` bash
python src/data_ingestion.py
python src/data_preprocessing.py
python src/model_training.py
python application.py
```

------------------------------------------------------------------------

## 🐳 3. Docker Setup

### Install Docker Desktop

Download from [Docker](https://www.docker.com/products/docker-desktop)
and keep it running in background.

### Project Dockerfile

``` dockerfile
FROM python:slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install --no-cache-dir -e .
RUN python src/model_training.py
EXPOSE 5000
CMD ["python", "application.py"]
```

### Build & run

``` bash
docker build -t ml-ops-app .
docker run -p 5000:5000 ml-ops-app
```

------------------------------------------------------------------------

## 🔧 4. Jenkins in Docker (DinD)

### Create custom Jenkins image

Inside `custom_jenkins/Dockerfile`:

``` dockerfile
FROM jenkins/jenkins:lts
USER root
RUN apt-get update -y && apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common &&     curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - &&     echo "deb [arch=amd64] https://download.docker.com/linux/debian bullseye stable" > /etc/apt/sources.list.d/docker.list &&     apt-get update -y && apt-get install -y docker-ce docker-ce-cli containerd.io && apt-get clean
RUN groupadd -f docker && usermod -aG docker jenkins
RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker
USER jenkins
```

### Build & run Jenkins

``` bash
cd custom_jenkins
docker build -t jenkins-dind .
docker run -d --name jenkins-dind ^
  --privileged ^
  -p 8080:8080 -p 50000:50000 ^
  -v //var/run/docker.sock:/var/run/docker.sock ^
  -v jenkins_home:/var/jenkins_home ^
  jenkins-dind
```

### Get Jenkins password

``` bash
docker logs jenkins-dind
```

Go to `http://localhost:8080`, paste password, install suggested
plugins, create admin user.

------------------------------------------------------------------------

## 🐍 5. Configure Jenkins Container

### Install Python

``` bash
docker exec -u root -it jenkins-dind bash
apt update -y
apt install -y python3 python3-pip python3-venv
ln -s /usr/bin/python3 /usr/bin/python
exit
docker restart jenkins-dind
```

### Install Google Cloud CLI

``` bash
docker exec -u root -it jenkins-dind bash
apt-get update
apt-get install -y curl apt-transport-https ca-certificates gnupg
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
apt-get update && apt-get install -y google-cloud-sdk
gcloud --version
exit
```

### Grant Docker permissions

``` bash
docker exec -u root -it jenkins-dind bash
groupadd docker
usermod -aG docker jenkins
usermod -aG root jenkins
exit
docker restart jenkins-dind
```

------------------------------------------------------------------------

## 📦 6. Jenkins Pipeline (CI/CD)

### Jenkinsfile

``` groovy
pipeline {
    agent any
    environment {
        PROJECT_ID = 'my-gcp-project'
        IMAGE = "gcr.io/${PROJECT_ID}/ml-ops-app:${env.BUILD_ID}"
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/<user>/ML_OPS_First_Project.git'
            }
        }
        stage('Setup venv') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                sh '. venv/bin/activate && pytest -q'
            }
        }
        stage('Build Docker') {
            steps {
                sh "docker build -t ${IMAGE} ."
            }
        }
        stage('Push to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa', variable: 'GCLOUD_KEY')]) {
                    sh 'gcloud auth activate-service-account --key-file=$GCLOUD_KEY'
                    sh 'gcloud auth configure-docker --quiet'
                    sh "docker push ${IMAGE}"
                }
            }
        }
    }
}
```

------------------------------------------------------------------------

## ☁️ 7. Deploy to GCP (Cloud Run)

Deploy image to Cloud Run:

``` bash
gcloud run deploy ml-ops-app   --image gcr.io/my-gcp-project/ml-ops-app:latest   --region us-central1   --platform managed   --allow-unauthenticated
```

------------------------------------------------------------------------

## ✅ Final Flow

1.  Local dev → run ingestion, preprocessing, training, Flask app\
2.  Push code to GitHub\
3.  Jenkins (DinD) → build venv, run tests, build Docker, push to GCR\
4.  Deploy to Cloud Run\
5.  MLflow logs experiments and artifacts\
6.  Flask app serves predictions

------------------------------------------------------------------------

This project demonstrates a complete **MLOps pipeline** from raw data
ingestion to cloud deployment with automated CI/CD.
