# Shared secret the webapp requires on /connect. Generated on first deploy and printed as the
# `demo_login_secret` output; reused on later deploys as long as this state exists.
resource "random_password" "login_secret" {
  length  = 24
  special = false
}

resource "aws_secretsmanager_secret" "login" {
  name = "${local.project_name}-login-secret"
  # Delete immediately on destroy instead of the default 30-day recovery window, so the name
  # can be reused on the next deploy.
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "login" {
  secret_id     = aws_secretsmanager_secret.login.id
  secret_string = random_password.login_secret.result
}

# Key used by the webapp to HMAC-sign session tokens. Generated fresh on each deploy.
resource "random_password" "session_signing_key" {
  length  = 64
  special = false
}

resource "aws_secretsmanager_secret" "session_signing_key" {
  name                    = "${local.project_name}-session-signing-key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "session_signing_key" {
  secret_id     = aws_secretsmanager_secret.session_signing_key.id
  secret_string = random_password.session_signing_key.result
}

# Let `make run-webapp-local` point the local server at the deployed secrets.
resource "local_file" "login_secret_arn" {
  content  = aws_secretsmanager_secret.login.arn
  filename = "${path.root}/../tmp/login_secret_arn.txt"
}

resource "local_file" "session_signing_key_arn" {
  content  = aws_secretsmanager_secret.session_signing_key.arn
  filename = "${path.root}/../tmp/session_signing_key_arn.txt"
}
