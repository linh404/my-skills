# Source-analysis checklist

Use this checklist when a request is not self-explanatory.

## Route and dispatch

- Match HTTP path/model/method from the `.bru` file to the controller route or API dispatcher.
- Record authentication, route type, allowed methods, and response/error handling.
- Check whether the endpoint calls ORM `create`, `write`, `unlink`, a workflow method, or a read/search method.

## Data and constraints

Inspect:

- required fields and default values;
- `Many2one`, `One2many`, and `Many2many` fields;
- selection values and state transitions;
- `@api.constrains`, SQL constraints, unique indexes, and date overlap rules;
- company/user context, record rules, and access groups;
- attachment field/model requirements;
- external services and file paths;
- returned record IDs, codes, and state values.

## Dependency evidence

Classify an edge only after recording its evidence:

| Evidence | Meaning |
|---|---|
| Request payload references an ID returned by another request | direct collection dependency |
| Backend requires a foreign key or searches a prior record | source-verified data dependency |
| Backend rejects a state unless a prior workflow method ran | source-verified state dependency |
| Same domain/name suggests an order but no code proves it | inferred recommendation |
| No endpoint or fixture can provide a required value | blocked/unknown |

## Common flow patterns

These are patterns to verify, not automatic rules:

- `login -> protected request`;
- `create/reference -> create dependent record -> get detail`;
- `create -> upload attachment -> get attachment/profile`;
- `create -> submit -> approve/reject/cancel -> progress/detail`;
- `create/update -> list/search/report`;
- `create fixture -> cleanup` only on an explicitly isolated test database.

When multiple requests can create the same domain record, document which one is canonical and why; do not run duplicate create flows merely because both files exist.
