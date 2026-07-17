# Technical Note: Safe Configuration-as-Code Workflow for CCMS XML via WebDAV

## Purpose

This note captures a practical approach for managing CCMS configuration in a safer, repeatable, version-controlled way. It is intended to support team discussion, provide a basis for a pilot, and frame the controls required before broader automation.

The core idea is to treat customer-managed CCMS configuration as code:

- Store a canonical source model in Git
- Generate target XML artifacts from that source
- Validate before deployment
- Deploy only to approved WebDAV paths
- Tag releases so specific milestones can be reloaded if rollback is required

This is best described as `configuration as code` with a `GitOps-style deployment model` for the subset of CCMS configuration we own.

## Context

We manage CCMS configuration that is ultimately stored as XML and loaded through a WebDAV endpoint. New configuration work often follows recurring patterns, such as:

- workflow configuration
- user configuration
- related supporting XML structures

At the same time, the target WebDAV instance also contains files that are changed by the SaaS platform itself. Those SaaS-managed files are isolated in separate directories and generally do not need to be modified by us.

That separation is important. It means a safe automation model is possible if we strictly limit our process to customer-managed paths and treat SaaS-managed paths as out of scope and read-only.

## Problem Statement

The current manual or semi-manual model creates predictable issues:

- repeated hand editing of similar XML structures
- inconsistent implementation between configurations
- limited auditability of what changed and why
- difficult rollback to a known-good configuration milestone
- higher chance of mistakes in pathing, naming, and dependent objects
- weak reuse when new configurations follow an existing pattern

These are all strong indicators that the work is suitable for automation.

## Proposed Operating Model

The proposed workflow is:

1. Capture configuration intent in a small structured source file, likely YAML.
2. Validate the YAML using JSON Schema and domain-specific rules.
3. Use templates and a build step to generate the full XML configuration set.
4. Validate the generated XML before deployment.
5. Deploy only the generated files that belong in customer-managed WebDAV directories.
6. Record the deployment as a versioned release tied to a Git commit or tag.
7. Roll back by redeploying a previous known-good release if needed.

This would allow both the source definition and the generated target artifacts to be versioned. Each release point would be recoverable from the Git repository.

## Scope Boundary

The key design principle is a hard boundary between two classes of target content:

- `customer-managed`: declarative, generated, version-controlled, deployable by our process
- `saas-managed`: mutable by the platform, excluded from generation, excluded from deployment, excluded from rollback

This boundary should be enforced in code, not treated as a convention.

The deployment tool should:

- use an allowlist of approved target directories
- refuse to write outside those directories
- refuse to delete or overwrite content in SaaS-managed locations
- keep an explicit source-to-target mapping for every deployed file

## Why This Is Worth Pursuing

If most configuration work follows repeatable patterns, then automation should provide clear gains:

- faster delivery of new configurations
- more consistent output
- lower manual error rate
- better reviewability through Git-based diffs
- reproducible deployments
- recoverable milestones
- a path to upstream automation from form-based inputs

This also creates a natural integration point for future intake automation. If business or implementation forms can produce validated YAML, the remainder of the pipeline can stay consistent.

## Recommended Architecture

### 1. Source Model

Use YAML as the human-authored source format for common configuration types. Examples:

- workflow definitions
- user definitions
- role or permission mappings
- routing or metadata configuration

The YAML should describe intent, not raw XML structure where possible.

### 2. Validation Layer

Validation should happen in two stages:

- structural validation using JSON Schema
- semantic validation using custom rules

JSON Schema is useful for checking:

- required fields
- allowed value types
- enums
- shape of nested objects

Custom validation is still needed for:

- naming conventions
- uniqueness rules
- referential integrity between related configuration items
- environment-specific constraints
- cross-file dependency checks

### 3. Template and Build Layer

Templates should be organized by configuration type. A builder should take validated YAML and generate deterministic XML output.

Important properties:

- same input always produces the same XML
- file naming and target paths are predictable
- ordering of generated XML is stable
- formatting is normalized so diffs are meaningful

### 4. Deployment Layer

Deployment should be manifest-driven. A manifest should define:

- source YAML file
- generated XML files
- approved WebDAV target paths
- deployment ordering
- release identifier

This avoids ad hoc copying and makes each release explicit and reviewable.

### 5. Verification Layer

After deployment, the process should verify:

- each expected file was uploaded
- each file landed in the expected path
- checksums or content match expectations where practical
- no out-of-scope path was touched

## Suggested Repository Shape

```text
/config/
  workflows/
  users/
  roles/

/schemas/
  workflow.schema.json
  user.schema.json
  role.schema.json

/templates/
  workflows/
  users/
  roles/

/generated/
  workflows/
  users/
  roles/

/manifests/
  releases/

/tools/
  validate
  build
  deploy
  verify
```

Depending on team preference, generated XML can either be committed to the repository or produced as a build artifact. There are tradeoffs.

Commit generated XML if the goal is:

- easy review of exact deployed artifacts
- immutable release snapshots inside Git
- simpler operational rollback without regeneration risk

Do not commit generated XML if the goal is:

- smaller and cleaner change history
- fewer merge conflicts
- strict separation between source and build output

If generated XML is committed, it should be treated as release output, not hand-edited content.

## Safety Controls

This approach is viable only if the safety controls are explicit.

### Path Safety

- maintain an allowlist of customer-managed WebDAV directories
- fail the deployment if any output resolves outside the allowlist
- never perform recursive delete outside explicitly managed locations

### Ownership Safety

- treat SaaS-managed directories as read-only and excluded
- avoid any rollback strategy that touches SaaS-owned paths

### Validation Safety

- require successful YAML validation before build
- require successful XML validation before deploy
- fail fast on unresolved references or missing dependencies

### Deployment Safety

- deploy in a deterministic order
- use dry-run mode by default for early testing
- produce a deployment report for each release

### Rollback Safety

- rollback by redeploying a previously tagged release
- use the same deployment manifest and path restrictions during rollback
- avoid any rollback that assumes the entire WebDAV tree is under our control

## Risks and Constraints

The approach is strong, but several risks remain:

### Drift within customer-managed scope

If people continue to edit deployed XML directly, Git stops being the source of truth. This must be addressed through team practice and deployment policy.

### Hidden configuration logic

If parts of the CCMS behavior depend on undocumented XML interactions, the builder may initially miss important rules. A pilot should expect discovery work here.

### Partial deployment states

If a set of XML files must be updated together, deployment ordering and failure handling matter. The tooling needs to account for incomplete uploads or mid-run errors.

### Environment differences

If dev, test, and production differ in naming, paths, or allowable values, the model needs explicit environment overlays rather than ad hoc edits.

### Over-generalization too early

Trying to solve every configuration type with a single abstract model will likely slow adoption. It is better to automate a narrow, high-volume configuration family first.

## Recommended Pilot

The safest way to test the idea is a constrained pilot.

Start with one configuration family that is:

- common
- repetitive
- well understood
- fully contained in customer-managed paths

Pilot phases:

1. Define one YAML model for that configuration family.
2. Write JSON Schema for structural validation.
3. Implement XML generation for one or two representative examples.
4. Compare generated output to current manually produced XML.
5. Add a dry-run deployment to a non-production environment.
6. Add manifest-driven deployment and verification.
7. Review whether the model is robust enough to expand to adjacent configuration types.

## Upstream Automation Opportunity

This model creates a clear path for future automation:

- implementation forms or intake workflows generate YAML
- YAML is validated automatically
- pull requests are created for review
- approved changes flow through build, validation, and deployment

That would move the team from manual XML editing toward a controlled, auditable delivery pipeline.

## Recommended Team Decisions

Before implementation, the team should align on a few points:

1. What exact WebDAV directories are customer-managed and therefore in scope?
2. Which configuration family is the best pilot candidate?
3. Should generated XML be committed to Git or built in CI?
4. What rollback procedure is acceptable operationally?
5. What environment model is required: dev, test, prod, or more?
6. Who owns the schemas, templates, and deployment tooling?

## Conclusion

This appears to be a strong candidate for automation.

The important constraint is not whether XML can be generated from YAML; that part is straightforward. The success of the approach depends on whether we enforce clear ownership boundaries, validate aggressively, and deploy only to approved customer-managed paths.

With those controls in place, a large share of the configuration project should be automatable. The best next step is a narrowly scoped pilot that proves the model on one configuration family, with explicit path controls, validation, deployment manifests, and release-based rollback.
