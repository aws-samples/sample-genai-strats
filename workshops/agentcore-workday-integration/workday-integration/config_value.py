# Prints one value from workday.configuration, with TENANT_ALIAS replaced by WORKDAY_TENANT_ALIAS.
# Used by the Makefile, e.g.: uv run config_value.py AGENT_MCP_ENDPOINT
import sys
from pathlib import Path
import dotenv

config = dotenv.dotenv_values(Path(__file__).parent.parent / "workday.configuration")
value = config.get(sys.argv[1]) or ""
print(value.replace("TENANT_ALIAS", config.get("WORKDAY_TENANT_ALIAS") or ""))
