TF := cd terraform && terraform

deploy:
	$(TF) init
	$(TF) apply -auto-approve

destroy: 
	$(TF) destroy

run-agent-local:
	cd agent && uv sync && uv run main.py

run-webapp-local:
	$(eval AGENT_RUNTIME_ARN := $(shell cat ./tmp/agent_runtime_arn.txt))
	cd webapp && AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN) nodemon
