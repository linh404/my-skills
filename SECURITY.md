# Security policy

This is a public repository. **Never commit credentials or private runtime
configuration.** This includes API keys, access tokens, passwords, private
keys, `.env` files, cloud credentials, and local Codex authentication data.

If a secret is exposed:

1. Revoke or rotate it immediately at the issuing provider.
2. Remove it from the working tree and Git history.
3. Report the incident privately to the repository owner.

The repository's `.gitignore` contains common credential patterns, but every
contributor is responsible for checking changes before pushing them.
