enable-cloudwatch-transactional-search:
	-aws xray update-indexing-rule --name Default --rule '{"Probabilistic":{"DesiredSamplingPercentage":100}}'

	-aws logs put-resource-policy \
  		--policy-name xray-cloudwatch-logs-policy \
  		--policy-document file://xray-cloudwatch-logs-policy.json

	-aws xray update-trace-segment-destination --destination CloudWatchLogs

deploy-infra:
	@echo "Running terraform apply..."
	cd terraform && \
		terraform init && \
		terraform apply --auto-approve

redeploy-gateway:
	@echo "Destroying log deliveries (must precede gateway deletion)..."
	cd terraform && terraform apply --auto-approve \
		-destroy \
		-target=aws_cloudwatch_log_delivery.gateway_logs \
		-target=aws_cloudwatch_log_delivery.gateway_traces
	
	@echo "Replacing AgentCore Gateway..."
	cd terraform && terraform apply --auto-approve \
		-replace=awscc_bedrockagentcore_gateway.pizza_shop \
		-replace=awscc_bedrockagentcore_policy_engine.pizza_shop

destroy:
	@echo "Destroying everything..."
	cd terraform && terraform destroy --auto-approve
	rm -rf tmp

# ── Module 2/3: basic gateway tests ──────────────────────────────────────────
list-tools:
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	$(eval ACCESS_TOKEN := $(shell cat ./tmp/access_token.txt 2>/dev/null || echo ""))
	curl -s -X POST $(GATEWAY_URL) \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq .

get-menu:
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	$(eval ACCESS_TOKEN := $(shell cat ./tmp/access_token.txt 2>/dev/null || echo ""))
	curl -s -X POST $(GATEWAY_URL) \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get-menu___get-menu","arguments":{}}}' | jq .

create-order:
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	$(eval ACCESS_TOKEN := $(shell cat ./tmp/access_token.txt 2>/dev/null || echo ""))
	$(eval PIZZA_ID := $(if $(pizzaId),$(pizzaId),1))
	curl -s -X POST $(GATEWAY_URL) \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"create-order___create-order\",\"arguments\":{\"pizzaId\":$(PIZZA_ID)}}}" | jq .

# ── Module 3: Cognito JWT ─────────────────────────────────────────────────────
get-token:
	@echo "Fetching Cognito access token..."
	$(eval COGNITO_TOKEN_ENDPOINT := $(shell cat ./tmp/cognito_token_endpoint.txt))
	$(eval COGNITO_CLIENT_ID := $(shell cat ./tmp/cognito_client_id.txt))
	$(eval COGNITO_CLIENT_SECRET := $(shell cat ./tmp/cognito_client_secret.txt))
	$(eval COGNITO_SCOPE := $(shell cat ./tmp/cognito_scope.txt))

	$(info > COGNITO_TOKEN_ENDPOINT=$(COGNITO_TOKEN_ENDPOINT))
	$(info > COGNITO_CLIENT_ID=$(COGNITO_CLIENT_ID))
	$(info > COGNITO_SCOPE=$(COGNITO_SCOPE))

	$(eval ACCESS_TOKEN := $(shell curl -s -X POST $(COGNITO_TOKEN_ENDPOINT) \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "grant_type=client_credentials&client_id=$(COGNITO_CLIENT_ID)&client_secret=$(COGNITO_CLIENT_SECRET)&scope=$(COGNITO_SCOPE)" \
		| jq -r '.access_token'))
	@echo ""
	@echo "Retrieved access token: $(ACCESS_TOKEN)"
	@echo $(ACCESS_TOKEN) > ./tmp/access_token.txt
	@echo "Token saved to ./tmp/access_token.txt"


# ── Module 5: Policy testing ──────────────────────────────────────────────────
get-client1-token:
	@echo "Fetching token for client1 (get_menu scope only)..."
	$(eval COGNITO_TOKEN_ENDPOINT := $(shell cat ./tmp/cognito_token_endpoint.txt))
	$(eval CLIENT_ID := $(shell cat ./tmp/cognito_client1_id.txt))
	$(eval CLIENT_SECRET := $(shell cat ./tmp/cognito_client1_secret.txt))
	$(eval ACCESS_TOKEN := $(shell curl -s -X POST $(COGNITO_TOKEN_ENDPOINT) \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "grant_type=client_credentials&client_id=$(CLIENT_ID)&client_secret=$(CLIENT_SECRET)&scope=gateway/get_menu" \
		| jq -r '.access_token'))
	@echo $(ACCESS_TOKEN) > ./tmp/access_token.txt
	@echo "client1 token saved to ./tmp/access_token.txt"

get-client2-token:
	@echo "Fetching token for client2 (get_menu + create_order scopes)..."
	$(eval COGNITO_TOKEN_ENDPOINT := $(shell cat ./tmp/cognito_token_endpoint.txt))
	$(eval CLIENT_ID := $(shell cat ./tmp/cognito_client2_id.txt))
	$(eval CLIENT_SECRET := $(shell cat ./tmp/cognito_client2_secret.txt))
	$(eval ACCESS_TOKEN := $(shell curl -s -X POST $(COGNITO_TOKEN_ENDPOINT) \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "grant_type=client_credentials&client_id=$(CLIENT_ID)&client_secret=$(CLIENT_SECRET)&scope=gateway/get_menu gateway/create_order" \
		| jq -r '.access_token'))
	@echo $(ACCESS_TOKEN) > ./tmp/access_token.txt
	@echo "client2 token saved to ./tmp/access_token.txt"

# ── Module 6: Outbound identity ──────────────────────────────────────────────
get-promotions:
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	$(eval ACCESS_TOKEN := $(shell cat ./tmp/access_token.txt 2>/dev/null || echo ""))
	curl -s -X POST $(GATEWAY_URL) \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"promotions___get-promotions","arguments":{}}}' | jq .

# ── Module 8: Python agent ────────────────────────────────────────────────────
run-agent-client1:
	@echo "Starting pizza ordering agent as client1 (get_menu + promotions only)..."
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	$(eval COGNITO_TOKEN_ENDPOINT := $(shell cat ./tmp/cognito_token_endpoint.txt 2>/dev/null || echo ""))
	$(eval CLIENT_ID := $(shell cat ./tmp/cognito_client1_id.txt 2>/dev/null || echo ""))
	$(eval CLIENT_SECRET := $(shell cat ./tmp/cognito_client1_secret.txt 2>/dev/null || echo ""))
	cd src/agent && \
		GATEWAY_URL=$(GATEWAY_URL) \
		COGNITO_CLIENT_ID=$(CLIENT_ID) \
		COGNITO_CLIENT_SECRET=$(CLIENT_SECRET) \
		COGNITO_TOKEN_ENDPOINT=$(COGNITO_TOKEN_ENDPOINT) \
		COGNITO_SCOPE="gateway/get_menu" \
		uv run agent.py

run-agent-client2:
	@echo "Starting pizza ordering agent as client2 (get_menu + create_order + promotions)..."
	$(eval GATEWAY_URL := $(shell cat ./tmp/gateway_url.txt))
	$(eval COGNITO_TOKEN_ENDPOINT := $(shell cat ./tmp/cognito_token_endpoint.txt 2>/dev/null || echo ""))
	$(eval CLIENT_ID := $(shell cat ./tmp/cognito_client2_id.txt 2>/dev/null || echo ""))
	$(eval CLIENT_SECRET := $(shell cat ./tmp/cognito_client2_secret.txt 2>/dev/null || echo ""))
	cd src/agent && \
		GATEWAY_URL=$(GATEWAY_URL) \
		COGNITO_CLIENT_ID=$(CLIENT_ID) \
		COGNITO_CLIENT_SECRET=$(CLIENT_SECRET) \
		COGNITO_TOKEN_ENDPOINT=$(COGNITO_TOKEN_ENDPOINT) \
		COGNITO_SCOPE="gateway/get_menu gateway/create_order" \
		uv run agent.py
