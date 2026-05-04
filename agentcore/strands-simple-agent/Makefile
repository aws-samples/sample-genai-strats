bootstrap:
	@echo "Bootstrapping..."
	cd terraform && \
		terraform init && \
		terraform apply --auto-approve --target=module.bootstrap

login-to-ecr:
	@echo "Logging into ECR..."
	$(eval AWS_ACCOUNT_ID := $(shell cat ./tmp/aws_account_id.txt))
	$(eval AWS_REGION := $(shell cat ./tmp/aws_region.txt))
	$(info > AWS_ACCOUNT_ID=$(AWS_ACCOUNT_ID))
	$(info > AWS_REGION=$(AWS_REGION))
	
	docker logout "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
	aws ecr get-login-password | docker login --username AWS --password-stdin "$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com"

build-and-push-agent:
	@echo "> Building agent container image..."
	$(eval ECR_REPO_URL := $(shell cat ./tmp/ecr_repo_url.txt))
	$(info > ECR_REPO_URL=$(ECR_REPO_URL))

	cd src/agent && \
		docker buildx build \
			--platform linux/arm64 \
			--no-cache \
			--load \
			-t "$(ECR_REPO_URL):latest" .

	@echo "> Pushing agent image to ECR..."
	docker push "$(ECR_REPO_URL):latest"

deploy-infra:
	@echo "Deploying cloud resources..."
	cd terraform && \
		terraform init && \
		terraform apply --auto-approve

destroy: 
	@echo "Destroying everything..."
	cd terraform && terraform destroy
	rm -rf ./tmp

test-agent:
	@echo "Testing agent..."
	$(eval AGENT_RUNTIME_ARN := $(shell cat ./tmp/agent_runtime_arn.txt))
	$(info > AGENT_RUNTIME_ARN=$(AGENT_RUNTIME_ARN))

	$(eval PAYLOAD := $(shell printf '{"prompt": "pizza recipe in one sentence"}' | base64))

	aws bedrock-agentcore invoke-agent-runtime \
		--agent-runtime-arn "$(AGENT_RUNTIME_ARN)" \
		--payload "$(PAYLOAD)" \
		--content-type "application/json" \
		--no-cli-pager \
		tmp/invoke_output.txt

	@echo "> Invocation output:"
	@cat tmp/invoke_output.txt | jq .


