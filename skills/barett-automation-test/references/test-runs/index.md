# Barett test-run archive

This directory is append-only. Create one Markdown file for every browser
test execution that reaches an Odoo view, including `FAIL`, `BLOCKED`, and
`NOT TESTED` outcomes.

Path format:

```text
YYYY/MM/YYYY-MM-DD--HHmmss--<scope>.md
```

The file's frontmatter is the searchable run index. See
[../test-recording.md](../test-recording.md) for the required fields and body
schema. Never overwrite an earlier run or place secrets in a report.
