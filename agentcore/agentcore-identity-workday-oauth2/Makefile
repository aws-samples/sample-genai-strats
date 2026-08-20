deploy:
	@echo "Running terraform apply"
	cd terraform && terraform init && terraform apply --auto-approve
	

destroy:
	@echo "Destroying everything..."
	cd terraform && terraform destroy
	rm -rf tmp

test:
	cd scripts && uv run test.py
