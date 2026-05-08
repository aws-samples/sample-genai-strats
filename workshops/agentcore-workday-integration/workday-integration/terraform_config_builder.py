import os
from pathlib import Path
import dotenv

config_path = Path(__file__).parent.parent / "workday.configuration"
dotenv.load_dotenv(dotenv_path=config_path)

MAPPING = {
    "wd_agent_client_id": "AGENT_CLIENT_ID",
    "wd_agent_client_secret": "AGENT_CLIENT_SECRET",
    "wd_agent_client_issuer": "AGENT_CLIENT_ISSUER",
    "wd_agent_client_authz_endpoint": "AGENT_CLIENT_AUTHZ_ENDPOINT",
    "wd_agent_client_token_endpoint": "AGENT_CLIENT_TOKEN_ENDPOINT",
}

output_path = Path(__file__).parent.parent / "tmp" / "terraform.tfvars"
output_path.parent.mkdir(parents=True, exist_ok=True)

lines = []
for tf_var, env_var in MAPPING.items():
    value = os.environ[env_var]
    lines.append(f'{tf_var} = "{value}"')

output_path.write_text("\n".join(lines) + "\n")
print(f"Written to {output_path}")
