
# set this to the role that allows your task to do stuff,
# this app needs s3, CloudWatch and Xray accesses
ROLE="arn:aws:iam::xxx:role/yyy"

# set this to the security group that allows access to at least your port
SECGROUP="sg-xxx"

# set this to the public subnet where you can get to your task port
SUBNET="subnet-yyy"

# set this to the path to the fargate cli binary
CLI="fargate"

run:
	${CLI} task run app  --security-group-id ${SECGROUP}  --task-role ${ROLE}

stop:
	${CLI} task stop app

info:
	$(eval IP:= $(shell ${CLI} task info app --no-color --no-emoji|grep IP|sed -n 's/^.*: //p'))
	@echo ${IP}

	@curl http://${IP}:8080
	@echo

run-local:
	python3 app.py

info-local:
	@curl localhost:8080
	@echo
