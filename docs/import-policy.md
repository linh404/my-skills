# Import policy

This public repository stores reusable skill source files, not local runtime
state. Do not import virtual environments, caches, generated files, local
translation work directories, credentials, access tokens, or machine-specific
configuration.

The `odoo-wlc` import intentionally excludes `.venv/`, pytest caches,
`__pycache__/`, and local translation work directories.
