---
name: uml-mdj-drawing
description: Create, edit, redraw, or validate StarUML .mdj UML/use-case diagrams by preserving the semantic model, references, views, layout coordinates, and connector geometry.
---

# StarUML `.mdj` drawing

Use this skill when the task asks to draw or redraw a UML diagram in StarUML JSON (`.mdj`), add actors/use cases/subjects/relationships, repair a diagram that does not open correctly, or generate a reusable diagram from a textual requirement.

Do **not** treat `.mdj` as a flat image or edit only labels. A valid file has two coupled layers:

1. **Semantic model** — actors, use cases, subjects, packages, associations, association ends.
2. **Diagram views** — visible nodes, compartments, labels, containers, and connector geometry.

Read [references/mdj-structure.md](references/mdj-structure.md) when creating or repairing a file programmatically.

## Workflow

1. **Gate 1 — present the drawing plan before editing.** Before creating or changing any `.mdj`, stop and show the user a concise overview of what will be drawn. The overview must name the target diagram, boundary/subjects, actors, use-case groups, important relationships, and intended layout. Use [references/gate-1-overview.md](references/gate-1-overview.md). Do not write the diagram file until the user approves the plan or explicitly tells you to proceed.
2. **Inspect the existing file first.** Preserve the root project/model/diagram structure, existing IDs, names, and unrelated diagrams. Never regenerate the whole file when a scoped edit is enough.
3. **Design semantics before layout.** List actors, use cases, system boundaries/subjects, and each relationship. Decide containment (which use case belongs to which subject) before assigning coordinates.
4. **Create unique IDs.** Every model object and every view/compartment needs a unique `_id`. For generated content use a stable prefix such as `GEN-`; do not reuse an ID from another object.
5. **Add semantic objects to `UMLModel.ownedElements`.** A diagram alone is not enough: the model objects must exist and associations must have two `UMLAssociationEnd` objects whose `reference` points to the endpoint model IDs.
   For class diagrams, follow StarUML's native class schema: keep each `UMLAttribute` object inline in its owning `UMLClass.attributes` array (with its own `_id` and `_parent`). Do not replace that array with `$ref` entries or store the attributes only in `ownedElements`; `UMLAttributeView` can then reference those attribute IDs while StarUML still renders the fields.
6. **Create views in the target diagram's `ownedViews`.** Each node view points to its semantic object with `model: {$ref: ...}` and has `_parent: {$ref: diagramId}`. Add `containerView` and the subject's `containedViews` when a use case is inside a subject boundary.
7. **Use StarUML's normal subview shape.** Node views contain a `UMLNameCompartmentView`; use-case/actor views also contain hidden attribute/operation/reception/template compartments. Keep these standard compartments unless there is a strong reason to simplify. Do not render the same name twice: if the target StarUML version renders the semantic object's `name` through the name compartment, leave that compartment's `subViews` empty and do not add a duplicate `LabelView` with the same text. When editing an existing file, preserve its established name-rendering pattern rather than mixing both patterns.
8. **Lay out on a grid.** Place the system boundary first, then use cases in columns/rows, then actors outside the boundary. Set `left`, `top`, `width`, and `height`; make widths large enough for the label. Avoid overlaps and keep whitespace for connectors.
9. **Create association views last.** Point `model` to the association, set `head`/`tail` to the endpoint *view IDs*, and use a `points` string such as `"x1:y1;x2:y2"`. Route lines along clear paths and avoid crossing node interiors. Preserve the standard hidden `EdgeLabelView`/qualifier subviews for compatibility. Keep one editable connector view per semantic association; never merge several actor/use-case associations into one line or collapse their endpoints merely to reduce visible rays unless the user explicitly asks for that redesign.
10. **Validate before finishing.** Parse JSON, verify every `$ref` resolves, verify every association has two valid ends, verify every visible model has the expected view, and check that container references are reciprocal. For class diagrams, also verify that every `UMLClass.attributes` entry is an inline `UMLAttribute`, every attribute view has usable absolute geometry, and each attribute compartment fits inside its class view. Then inspect a diff and, if possible, close/reopen the file in StarUML to verify the actual render; JSON validation alone is not a visual verification.

## Editing rules

- Prefer minimal, deterministic edits over broad reformatting; `.mdj` files are large and ID-heavy.
- Keep semantic IDs and view IDs distinct even when they represent the same concept.
- A relationship's model endpoints use semantic IDs; a relationship view's `head`/`tail` use view IDs. Do not mix these namespaces.
- Coordinates are absolute diagram coordinates. Recompute connector points after moving nodes.
- For visible class fields, use the normal StarUML geometry: the `UMLAttributeCompartmentView` needs absolute `left`, `top`, `width`, and `height`, and every `UMLAttributeView` needs absolute `left`, `top`, `width`, `height`, `parentStyle`, and `horizontalAlignment`. Increase the class view height when needed so the compartment is not clipped. Copy this shape from a known-good StarUML class diagram instead of relying on default bounds.
- Do not delete hidden compartments merely because they are not visible; StarUML commonly expects them in generated node views.
- Do not add guessed `lineColor`/`fillColor` properties as a substitute for missing fields. Repair semantic class attributes and compartment geometry first; only copy explicit style properties from a known-good file or a user-specified visual style.
- Do not add a `LabelView` that duplicates a semantic model name. Before finishing, scan actor, use-case, subject, package, component, and note views for repeated labels and verify that each visible name has one rendering source.
- Do not add a standalone title text above the diagram (for example a `UMLTextView` reading “Use Case tổng quát — ...”) unless the user explicitly asks for one. The diagram name and the subject/boundary label are sufficient; avoid duplicating them on the canvas.
- Preserve the user's current scope: do not re-add an actor, use case, relationship, or diagram element that the user removed, and do not silently redraw connector routing after a requested rollback.
- Do not invent UML relationships from prose without confirming direction/meaning. For ordinary use-case participation, an association is usually sufficient; use include/extend/generalization only when explicitly required.
- Preserve Vietnamese labels and Unicode; write UTF-8 JSON.
- Never claim the drawing is correct from JSON parsing alone: unresolved refs, stale container lists, bad connector endpoints, or an invalid StarUML view can still make the diagram render incorrectly.

## Output expectations

When completing a drawing task, report:

- files changed;
- semantic elements added/changed;
- diagrams/views added/changed;
- validation performed and any remaining uncertainty.
