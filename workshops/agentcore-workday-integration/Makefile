# --- Get Agent Card via Workday Integration Client ----
get-agent-card:
	cd workday-integration && \
		uv sync && \
		uv run get-agent-card.py
	
	cp ./tmp/agent_card.json ./agent/agent_card.json

# --- Build agent package
build-agent-package:
	rm -rf ./tmp/agent_package
	mkdir -p ./tmp
	cd agent && \
		uv pip install \
			--python-platform aarch64-manylinux2014 \
			--python-version 3.13 \
			--target=./../tmp/agent_package/dependencies \
			--only-binary=:all: \
			-r pyproject.toml
	cd tmp/agent_package/dependencies && zip -r ../agent.zip .
	cd agent && zip ./../tmp/agent_package/agent.zip *.py
	cd agent && zip ./../tmp/agent_package/agent.zip agent_card.json

# --- Deploy AgentCore Resources ----
build-terraform-config:
	cd workday-integration && \
		uv sync && \
		uv run terraform_config_builder.py
	
	cp ./tmp/terraform.tfvars ./terraform/terraform.tfvars
	rm ./tmp/terraform.tfvars

deploy-infra:
	@echo "> Deploying infrastructure..."
	cd terraform && \
		terraform init && \
		terraform apply --auto-approve

deploy-agent-to-agentcore: build-agent-package build-terraform-config deploy-infra

destroy:
	@echo "> Cleaning up..."
	cd terraform && terraform destroy
	rm -rf ./agent/agent_card.json
	rm -rf ./terraform/terraform.tfvars
	rm -rf ./tmp

# --- Workshop Tasks ----
run-chat-local:
	cd agent-chat && uv sync && uv run chat.py

run-chat-remote:
	cd agent-chat && uv sync && uv run chat.py remote

run-agent-locally:
	$(eval WORKLOAD_IDENTITY_NAME := $(shell cat ./tmp/workload_identity_name.txt))
	$(eval CREDENTIAL_PROVIDER_NAME := $(shell cat ./tmp/agent_client_credential_provider_name.txt))
	
	cd agent && \
		WORKLOAD_IDENTITY_NAME="$(WORKLOAD_IDENTITY_NAME)" \
		CREDENTIAL_PROVIDER_NAME="$(CREDENTIAL_PROVIDER_NAME)" \
		uv run agent.py

start-dashboard:
	@echo "> Start Dashboard..."
	$(eval AGENT_RUNTIME_ARN := $(shell cat ./tmp/agent_runtime_arn.txt))
	$(info > AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN))

	@rm -f ./dashboard/.env
	@echo "AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN)" >> ./dashboard/.env
	@echo "> ./dashboard/.env updated"

	cd dashboard && uv sync
	cd dashboard && uv run dashboard.py

