enable-cloudwatch-transactional-search:
	-aws xray update-indexing-rule --name Default --rule '{"Probabilistic":{"DesiredSamplingPercentage":100}}'
	
	-aws logs put-resource-policy \
  		--policy-name xray-cloudwatch-logs-policy \
  		--policy-document file://xray-cloudwatch-logs-policy.json

	-aws xray update-trace-segment-destination --destination CloudWatchLogs

deploy-infra:
	@echo "Running terraform apply"
	cd terraform && \
	terraform init && \
	terraform apply --auto-approve

destroy:
	@echo "Destroying everything..."
	cd terraform && terraform destroy
	rm -rf tmp

run-agent-locally:
	@echo "Run agent locally..."
	$(eval TECH_SUPPORT_KB_ID := $(shell cat ./tmp/tech_support_kb_id.txt))
	$(eval MEMORY_ID := $(shell cat ./tmp/memory_id.txt))
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	$(eval COGNITO_CLIENT_ID := $(shell cat ./tmp/cognito_client_id.txt))
	$(eval COGNITO_CLIENT_SECRET := $(shell cat ./tmp/cognito_client_secret.txt))
	$(eval COGNITO_TOKEN_ENDPOINT := $(shell cat ./tmp/cognito_token_endpoint.txt))
	$(eval COGNITO_SCOPE := $(shell cat ./tmp/cognito_scope.txt))
	$(eval WORKLOAD_ID_NAME := $(shell cat ./tmp/workload_identity_name.txt))
	$(eval CREDENTIAL_PROVIDER_NAME := $(shell cat ./tmp/credential_provider_name.txt))
	
	cd src/agent && \
		TECH_SUPPORT_KB_ID=$(TECH_SUPPORT_KB_ID) \
		MEMORY_ID=$(MEMORY_ID) \
		GATEWAY_URL=$(GATEWAY_URL) \
		COGNITO_CLIENT_ID=$(COGNITO_CLIENT_ID) \
		COGNITO_CLIENT_SECRET=$(COGNITO_CLIENT_SECRET) \
		COGNITO_TOKEN_ENDPOINT=$(COGNITO_TOKEN_ENDPOINT) \
		COGNITO_SCOPE=$(COGNITO_SCOPE) \
		WORKLOAD_ID_NAME=$(WORKLOAD_ID_NAME) \
		CREDENTIAL_PROVIDER_NAME=$(CREDENTIAL_PROVIDER_NAME) \
		uv run agent.py

get-cognito-access-token:
	@echo "Getting a new access token..."
	$(eval COGNITO_TOKEN_ENDPOINT := $(shell cat ./tmp/cognito_token_endpoint.txt))
	$(eval COGNITO_SCOPE := $(shell cat ./tmp/cognito_scope.txt))
	$(eval COGNITO_CLIENT_ID := $(shell cat ./tmp/cognito_client_id.txt))
	$(eval COGNITO_CLIENT_SECRET := $(shell cat ./tmp/cognito_client_secret.txt))

	$(info > COGNITO_TOKEN_ENDPOINT=$(COGNITO_TOKEN_ENDPOINT))
	$(info > COGNITO_CLIENT_ID=$(COGNITO_CLIENT_ID))
	$(info > COGNITO_CLIENT_SECRET=$(shell echo $(COGNITO_CLIENT_SECRET) | cut -c1-2)...REDACTED...)
	$(info > COGNITO_SCOPE=$(COGNITO_SCOPE))

	$(eval ACCESS_TOKEN := $(shell curl -s -X POST $(COGNITO_TOKEN_ENDPOINT) \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "grant_type=client_credentials&client_id=$(COGNITO_CLIENT_ID)&client_secret=$(COGNITO_CLIENT_SECRET)&scope=$(COGNITO_SCOPE)" \
		| jq -r '.access_token'))
	@echo ""
	@echo "Retrieved access token: $(ACCESS_TOKEN)"
	@echo $(ACCESS_TOKEN) > ./tmp/access_token.txt
	@echo ""
	@echo "Token saved to ./tmp/access_token.txt"

test-gateway:
	@echo "Getting a list of tools from the gateway..."
	$(eval ACCESS_TOKEN := $(shell cat ./tmp/access_token.txt))
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	
	$(info > ACCESS_TOKEN=$(shell echo $(ACCESS_TOKEN) | cut -c1-10).....)
	$(info > GATEWAY_URL=$(GATEWAY_URL))

	curl -s -X POST $(GATEWAY_URL) \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' \
		| jq .

build-agent-package:
# 	rm -rf ./tmp/agent_package
# 	rm -rf ./tmp/agent_package/agent.zip
	mkdir -p ./tmp
	cd src/agent && \
		uv pip install \
			--python-platform aarch64-manylinux2014 \
			--python-version 3.13 \
			--target=./../../tmp/agent_package/dependencies \
			--only-binary=:all: \
			-r pyproject.toml
	cd tmp/agent_package/dependencies && zip -r ../agent.zip .
	cd src/agent && zip ./../../tmp/agent_package/agent.zip *.py tools/*.py

invoke-agent:
	@echo "Invoking agent...."
	$(eval AGENT_RUNTIME_ARN := $(shell cat ./tmp/agent_runtime_arn.txt))
	$(info > AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN))

	$(eval PROMPT := My headphones are broken, whats the return policy?)
	$(eval PAYLOAD := $(shell echo '{"prompt":"$(PROMPT)"}' | base64))

	@echo ""
	@echo "Testing with prompt: $(PROMPT)"
	@printf "Press ENTER to start..."; read _
	
	aws bedrock-agentcore invoke-agent-runtime \
  		--agent-runtime-arn "$(AGENT_RUNTIME_ARN)" \
		--payload "$(PAYLOAD)" \
		--content-type "application/json" \
		tmp/invoke_output.txt \
		--no-cli-pager

test-remote-agent:
	@echo "Testing remote agent..."
	cd src/agent && uv run remote_agent_invoker.py



