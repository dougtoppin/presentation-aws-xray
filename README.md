# presentation-aws-xray
Overview of using the AWS X-Ray service

## Presentation pdf is in the assets dir

## Usage

* create a new aws temporary account that can be deleted afterwards
* install fargate cli (https://github.com/awslabs/fargatecli)
* find the default public subnet in your default vpc
* create a security group that allows access to port 8080 for your default vpc
* create role that allows fargate task to access s3, cloudwatch and use x-ray
* edit Makefile and set role, security group, subnet, path to fargate cli
* make run - this will build the image, push to ECR, create the fargate task
* make info - access the ReST endpoint of the task
* check x-ray console system map to see the fargate task activity
* make stop - stop the running task
* delete temporary aws account

## Files

* Makefile - control build and deploy
* app.py - Python Flask app with a simple ReST endpoint
* Dockerfile - create a container image of the app and x-ray agent
* startup.sh - starts the x-ray agent and app in the container
* cfg.yaml - configuration file for x-ray agent

## Notes

* fargate tasks are not free, do not leave this task running
* fargate task CloudWatch log will be in log group /fargate/task/app