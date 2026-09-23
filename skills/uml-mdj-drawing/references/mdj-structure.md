# StarUML `.mdj` structure and drawing recipe

The examples below are distilled from `test_redraw.mdj` and `test_redrawn_general.mdj` in the Ttcs workspace.

## 1. Root and semantic layer

```json
{
  "_type": "Project",
  "_id": "project-id",
  "name": "Untitled",
  "ownedElements": [
    {
      "_type": "UMLModel",
      "_id": "model-id",
      "_parent": {"$ref": "project-id"},
      "name": "Model1",
      "ownedElements": []
    }
  ],
  "documentVersion": "..."
}
```

Common semantic elements under `UMLModel.ownedElements`:

- `UMLUseCaseDiagram`: diagram definition; owns `ownedViews`.
- `UMLUseCaseSubject`: system boundary/grouping subject.
- `UMLUseCase`: a use case.
- `UMLActor`: an actor.
- `UMLPackage`: optional organization element.
- `UMLAssociation`: relationship model.
- `UMLAssociationEnd`: one endpoint of an association.

All objects need unique `_id` values. Parentage is represented by `_parent: {$ref: parentId}`. Cross-object links use `{$ref: targetId}`.

For a class/table diagram, `UMLClass` objects are owned by the model, but their attributes use StarUML's native inline shape:

```json
{
  "_type": "UMLClass",
  "_id": "table-model-id",
  "_parent": {"$ref": "model-id"},
  "name": "nhanvien",
  "attributes": [
    {
      "_type": "UMLAttribute",
      "_id": "attribute-model-id",
      "_parent": {"$ref": "table-model-id"},
      "name": "MaNhanVien",
      "type": "VARCHAR"
    }
  ]
}
```

Do not serialize `UMLClass.attributes` as an array of `$ref` objects or keep the attributes only in `UMLClass.ownedElements`. Attribute views may reference the inline attribute IDs, but StarUML uses the inline `attributes` collection to render the fields.

## 2. Node views

A diagram stores view objects in `UMLUseCaseDiagram.ownedViews`:

```json
{
  "_type": "UMLUseCaseView",
  "_id": "view-usecase-1",
  "_parent": {"$ref": "diagram-id"},
  "model": {"$ref": "usecase-model-id"},
  "left": 485,
  "top": 110,
  "width": 330,
  "height": 38,
  "font": "Arial;13;0",
  "parentStyle": false,
  "containerChangeable": true,
  "suppressAttributes": true,
  "suppressOperations": true,
  "nameCompartment": {"$ref": "name-compartment-id"},
  "subViews": []
}
```

In real StarUML files, `subViews` normally contains:

- `UMLNameCompartmentView` with nested `LabelView` objects;
- hidden `UMLAttributeCompartmentView`;
- hidden `UMLOperationCompartmentView`;
- hidden `UMLReceptionCompartmentView`;
- hidden `UMLTemplateParameterCompartmentView`;
- for use cases, hidden `UMLExtensionPointCompartmentView`.

Actors use `UMLActorView`; boundaries use `UMLUseCaseSubjectView`. A subject view has `containedViews` referencing the child node views. A child node view should also set `containerView` to the subject view.

For a visible class field compartment, preserve the standard absolute geometry:

```json
{
  "_type": "UMLAttributeCompartmentView",
  "model": {"$ref": "table-model-id"},
  "left": 100,
  "top": 125,
  "width": 300,
  "height": 70,
  "parentStyle": true,
  "subViews": [
    {
      "_type": "UMLAttributeView",
      "model": {"$ref": "attribute-model-id"},
      "left": 105,
      "top": 130,
      "width": 290,
      "height": 13,
      "parentStyle": true,
      "horizontalAlignment": 0,
      "text": "MaNhanVien: VARCHAR"
    }
  ]
}
```

The compartment and every attribute subview must lie inside the class view. Missing geometry can produce a valid-looking `.mdj` whose table names render but whose fields are blank.

Coordinates are absolute. The label's `text` is in its `LabelView` (usually the bold name label), while the semantic object's `name` remains the source of truth.

`UMLTextView` is optional. Do not create a standalone `UMLTextView` merely to repeat the diagram name or subject title above the canvas. Use it only when the user explicitly requests an additional explanatory heading or annotation.

## 3. Association model and view

An association model has two ends:

```json
{
  "_type": "UMLAssociation",
  "_id": "assoc-model-id",
  "_parent": {"$ref": "source-model-id"},
  "end1": {
    "_type": "UMLAssociationEnd",
    "_id": "assoc-end-1",
    "_parent": {"$ref": "assoc-model-id"},
    "reference": {"$ref": "actor-model-id"}
  },
  "end2": {
    "_type": "UMLAssociationEnd",
    "_id": "assoc-end-2",
    "_parent": {"$ref": "assoc-model-id"},
    "reference": {"$ref": "usecase-model-id"}
  }
}
```

The corresponding diagram view uses **view IDs**, not model IDs:

```json
{
  "_type": "UMLAssociationView",
  "_id": "assoc-view-id",
  "_parent": {"$ref": "diagram-id"},
  "model": {"$ref": "assoc-model-id"},
  "head": {"$ref": "usecase-view-id"},
  "tail": {"$ref": "actor-view-id"},
  "lineStyle": 1,
  "points": "150:290;650:411",
  "subViews": []
}
```

Actual StarUML output usually includes hidden `EdgeLabelView` and `UMLQualifierCompartmentView` children plus refs such as `nameLabel`, `tailRoleNameLabel`, and `headMultiplicityLabel`. Copy the shape from a known-good association view when generating files rather than inventing a reduced shape without testing.

## 4. How the reference diagrams were drawn

`test_redrawn_general.mdj` keeps the original model and adds a general overview diagram:

- one large `UMLUseCaseSubject` boundary;
- 15 overview `UMLUseCase` elements;
- 7 actors outside/around the boundary;
- 20 associations;
- node positions chosen manually on a grid;
- connector points chosen after node placement.

A reliable generation order is therefore:

1. semantic actors/use cases/subject;
2. diagram and node views;
3. subject containment refs;
4. association models and ends;
5. association views and connector points;
6. compartments/labels and validation.

## 5. Validation checklist

Use a small parser/validator before opening StarUML:

- root `_type` is `Project`;
- all `_id` values are unique;
- every `$ref` resolves to an object or an intentionally external parent;
- every association has exactly two ends with valid semantic references;
- every view's `model` points to the expected semantic type;
- every `containerView` has a matching subject `containedViews` entry;
- every association view's `head` and `tail` point to views in the same diagram;
- every `UMLClass.attributes` item is an inline `UMLAttribute` object, every class attribute has a matching `UMLAttributeView`, and field compartment geometry is inside the class bounds;
- each intended semantic association has its own association view; connector views are not merged by visual routing shortcuts;
- all JSON strings are UTF-8 and the file parses cleanly.
