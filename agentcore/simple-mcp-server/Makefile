deploy:
	cd terraform && terraform init && terraform apply --auto-approve

destroy:
	cd terraform && terraform destroy --auto-approve
	rm -rf ./tmp

test-local:
	cd src && uv sync && uv run server.py

get-cognito-token:
	cd scripts && uv sync && uv run get-cognito-token.py

test-remote-mcp:
	cd scripts && uv sync && uv run test-remote-mcp.py


build-package:
	mkdir -p ./tmp
	cd src && \
		uv pip install \
			--python-platform aarch64-manylinux2014 \
			--python-version 3.13 \
			--target=./../tmp/mcp_server_package/dependencies \
			--only-binary=:all: \
			-r pyproject.toml
	cd tmp/mcp_server_package/dependencies && zip -r ../mcp_server.zip .
	cd src && zip ./../tmp/mcp_server_package/mcp_server.zip *.py
