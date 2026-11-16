# Barett reusable UI workflows

Store canonical, verified Odoo UI flows under `<area>/<workflow-slug>.md`.
Use model/menu areas such as `purchase-request`, `purchase-order`,
`sales-plan`, `users`, or `shared`.

Before a browser test, search this catalog by issue ID, model, view, or visible
label. After a test, update a workflow only when the observed flow is new or
changed; the individual run report must still contain its exact action
sequence. See [../test-recording.md](../test-recording.md) for the schema and
query commands.
