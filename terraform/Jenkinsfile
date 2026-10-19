
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        AWS_REGION     = 'ap-south-1'
        AWS_ACCOUNT_ID = '836568434461'
        ECR_REPOSITORY = 'ecs-cicd-demo-dev-app'
        ECS_CLUSTER    = 'ecs-cicd-demo-dev-cluster'
        ECS_SERVICE    = 'ecs-cicd-demo-dev-service'
        TASK_FAMILY    = 'ecs-cicd-demo-dev-app'
        CONTAINER_NAME = 'app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
                    env.IMAGE_URI = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.ECR_REPOSITORY}:${env.IMAGE_TAG}"
                }
                echo "Building image: ${env.IMAGE_URI}"
            }
        }

        stage('Test Application') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                    .venv/bin/python -m pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build --pull -t "$IMAGE_URI" .
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region "$AWS_REGION" |
                    docker login \
                      --username AWS \
                      --password-stdin \
                      "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
                '''
            }
        }

        stage('Push Image to ECR') {
            steps {
                sh '''
                    docker push "$IMAGE_URI"
                '''
            }
        }

        stage('Register Task Definition') {
            steps {
                sh '''
                    set -eu

                    aws ecs describe-task-definition \
                      --task-definition "$TASK_FAMILY" \
                      --region "$AWS_REGION" \
                      --query 'taskDefinition' \
                      --output json > task-definition.json

                    jq --arg image "$IMAGE_URI" \
                       --arg version "$IMAGE_TAG" \
                       --arg commit "$GIT_COMMIT" \
                       '
                       del(
                         .taskDefinitionArn,
                         .revision,
                         .status,
                         .requiresAttributes,
                         .compatibilities,
                         .registeredAt,
                         .registeredBy
                       )
                       | .containerDefinitions |= map(
                           if .name == "app" then
                             .image = $image
                             | .environment = (
                                 ((.environment // [])
                                   | map(select(
                                       .name != "APP_VERSION"
                                       and .name != "GIT_COMMIT"
                                     )))
                                 + [
                                     {name: "APP_VERSION", value: $version},
                                     {name: "GIT_COMMIT", value: $commit}
                                   ]
                               )
                           else .
                           end
                         )
                       ' task-definition.json > task-definition-new.json

                    jq -e \
                      --arg name "$CONTAINER_NAME" \
                      --arg image "$IMAGE_URI" \
                      '.containerDefinitions | any(
                        .name == $name and .image == $image
                      )' task-definition-new.json

                    aws ecs register-task-definition \
                      --cli-input-json file://task-definition-new.json \
                      --region "$AWS_REGION" \
                      --query 'taskDefinition.taskDefinitionArn' \
                      --output text > new-task-definition-arn

                    cat new-task-definition-arn
                '''
            }
        }

        stage('Deploy to ECS') {
            steps {
                sh '''
                    set -eu

                    TASK_DEFINITION_ARN="$(cat new-task-definition-arn)"

                    aws ecs update-service \
                      --cluster "$ECS_CLUSTER" \
                      --service "$ECS_SERVICE" \
                      --task-definition "$TASK_DEFINITION_ARN" \
                      --region "$AWS_REGION" \
                      --output json

                    aws ecs wait services-stable \
                      --cluster "$ECS_CLUSTER" \
                      --services "$ECS_SERVICE" \
                      --region "$AWS_REGION"
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    aws ecs describe-services \
                      --cluster "$ECS_CLUSTER" \
                      --services "$ECS_SERVICE" \
                      --region "$AWS_REGION" \
                      --query 'services[0].{Status:status,Desired:desiredCount,Running:runningCount,Pending:pendingCount,TaskDefinition:taskDefinition}' \
                      --output table
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review the failed stage and Jenkins console log.'
        }
        always {
            sh 'docker logout "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com" || true'
            deleteDir()
        }
    }
}
