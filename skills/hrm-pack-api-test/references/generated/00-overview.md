# HRM Pack API execution guide

Generated from 122 executable Bruno requests and the current backend source.

## Important

This is a static build-time guide. The runner must execute one flow at a time, capture IDs/state, and require approval for mutations. Hardcoded IDs are warnings, not reusable fixtures.

## Flow counts

- `attendance_explanation`: 14
- `authentication`: 6
- `employee_context`: 31
- `gps_attendance`: 11
- `helpdesk`: 4
- `leave`: 16
- `overtime`: 5
- `read_only_reports`: 3
- `reference_data`: 7
- `resignation`: 13
- `staff_transfer`: 12

## Files

- `api-execution-order.yaml` — total deterministic order and nodes.
- `api-dependency-graph.yaml` — dependency edges.
- `api-constraints.yaml` — source/collection constraints and risks.
- `api-unknowns.yaml` — unresolved routes/mappings.
- `docs/NNN-*.md` — one document per API in execution order.
