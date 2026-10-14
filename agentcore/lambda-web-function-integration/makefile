TF := cd terraform && terraform

deploy:
	$(TF) init
	$(TF) apply -auto-approve

destroy:
	$(TF) destroy

get-demo-secret:
	$(eval DEMO_LOGIN_SECRET_ARN := $(shell cat ./tmp/login_secret_arn.txt))
	aws secretsmanager get-secret-value --secret-id $(DEMO_LOGIN_SECRET_ARN) --query SecretString --output text

run-agent-local:
	cd agent && uv sync && uv run main.py

run-webapp-local:
	$(eval AGENT_RUNTIME_ARN := $(shell cat ./tmp/agent_runtime_arn.txt))
	$(eval DEMO_LOGIN_SECRET_ARN := $(shell cat ./tmp/login_secret_arn.txt))
	$(eval SESSION_SIGNING_KEY_ARN := $(shell cat ./tmp/session_signing_key_arn.txt))
	cd webapp && \
		AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN) \
		DEMO_LOGIN_SECRET_ARN=$(DEMO_LOGIN_SECRET_ARN) \
		SESSION_SIGNING_KEY_ARN=$(SESSION_SIGNING_KEY_ARN) \
		nodemon
