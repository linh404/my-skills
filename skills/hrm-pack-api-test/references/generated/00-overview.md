# HRM Pack API execution guide

Generated from 146 executable Bruno requests and the current backend source.

## Important

This is a static build-time guide. The runner must execute one flow at a time, capture IDs/state, and require approval for mutations. Hardcoded IDs are warnings, not reusable fixtures.

## Flow counts

- `attendance_explanation`: 18
- `authentication`: 6
- `employee_context`: 34
- `external_services`: 3
- `gps_attendance`: 13
- `helpdesk`: 5
- `leave`: 22
- `overtime`: 6
- `read_only_reports`: 5
- `reference_data`: 8
- `resignation`: 13
- `staff_transfer`: 13

## Files

- `api-execution-order.yaml` — total deterministic order and nodes.
- `api-dependency-graph.yaml` — dependency edges.
- `api-constraints.yaml` — source/collection constraints and risks.
- `api-unknowns.yaml` — unresolved routes/mappings.
- `docs/NNN-*.md` — one document per API in execution order.
