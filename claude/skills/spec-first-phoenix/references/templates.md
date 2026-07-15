# Templates & conventions for the durable artifacts

Read this when creating any artifact. It gives skeletons and the conventions
that keep them honest. Copy a skeleton, then fill it — do not invent a
different structure per project without a logged decision. Keep the voice
terse and normative: specs are read by implementers who will do exactly what
they say and nothing they don't.

## Conventions that apply to every artifact

- **Status line, always first.** Every durable artifact opens with a status
  line: `Status: DRAFT` or `Status: APPROVED v<N> — see D<k>`. Bump `v<N>` and
  the decision reference at the moment of approval; this is the single most
  forgotten step.
- **Decisions are numbered and quoted.** Every approval, scope change, and
  amendment gets a `D<n>` entry in `docs/design/decision-log.md`, newest last,
  quoting the user's own words for the approval. When notes conflict, the log
  wins.
- **Prohibitions are explained.** Never write a bare "don't." Write
  *"don't X, because Y; instead Z."* Implementation agents ignore bare
  prohibitions and respect explained ones.
- **Judgment is flagged, not disguised.** Any science-/policy-laden default
  (thresholds, radii, priorities, weights) lives in a tunable data file marked
  as drafted judgment for the domain owner to review — never asserted as fact
  in spec prose.
- **Repairs are visible.** Fixing a mistake in a durable artifact gets a note
  and a decision entry. An append-only log that hides its own errors is not
  append-only.

---

## `AXIOMS.md` — the constitution

```markdown
# Axioms
Status: DRAFT

The non-negotiable principles for this project and the rule for changing them.

## A1. <principle, stated positively>
<Why it holds. If it forbids something: don't X, because Y; instead Z.>

## A2. <principle>
...

## Amendment rule
An axiom changes only by a decision-log entry that quotes the maintainer's
approval and states what the change breaks. Superseded axioms are struck
through with the D<n> that retired them, never deleted.
```

Keep axioms few and load-bearing. If a statement is a design preference rather
than a thing that must never be violated, it belongs in a SPEC, not here.

---

## `ARCHITECTURE.md` — components, boundaries, and the treatment table

```markdown
# Architecture
Status: DRAFT

## Components
- **<name>** — <one-line responsibility>. Boundary: <interface it exposes /
  consumes>.

## Cross-component invariants
- <invariant that must hold across boundaries, and who enforces it>

## Treatment table
| Component | Treatment    | Reasoning (argue from the failure modes) |
|-----------|--------------|------------------------------------------|
| <name>    | regenerable  | Pure function; test surface enumerable; no profiling/operational knowledge. |
| <name>    | maintained   | Adapts to a live external API (drift); bugs reproduce only against operational state. |
| <name>.url| regenerable  | Split component: URL construction is pure. |
| <name>.xport | maintained | Split component: transport has live auth + rate limits. |
```

The treatment column is never uniformly "regenerable." Argue each row from
Breunig's failure modes (performance-by-profiling, test surface too large,
bug-reproduction against operational state, continuous external-interface
drift, shared-reference-implementation value). A single component may split —
declare both halves as separate rows.

---

## `specs/<component>/SPEC.md` — the behavioral spec

```markdown
# <Component> — Specification
Status: DRAFT
Treatment: regenerable | maintained

## Purpose
<What this component is responsible for, in one paragraph.>

## Interface
<Functions / endpoints / messages: name, inputs, outputs, types. Reference
declared boundary interfaces; do not restate another component's internals.>

## Behavior
<Normative rules. Numbered so tests and the decision log can cite them.>
1. <rule>
2. <rule; edge cases stated explicitly, not implied>

## Error & warning codes
| Code       | Condition                    | Severity |
|------------|------------------------------|----------|
| E_BADINPUT | <exact trigger>              | error    |
| W_DEGRADED | <exact trigger>              | warning  |
Every code here MUST be exercised by at least one case in tests.yaml.

## Normative data
<Vocabularies, registries, policies this component obeys. Point to the frozen
data file; for maintained components, note which requirements are NOT
contract-testable (transactionality, corrupt-store handling) and require
implementation-level tests instead — so they are recorded, not lost.>
```

---

## `specs/<component>/tests.yaml` — the language-agnostic test contract

```yaml
meta:
  component: <name>
  spec_version: <matches SPEC.md status vN>   # bump at approval
  status: DRAFT
  contract_version: 1

# Fixtures frozen INSIDE the contract, so it can't drift when live config
# evolves. Embed the registries/policies the cases depend on.
fixtures:
  registry:
    - { key: <k>, value: <v> }

cases:
  - id: happy-path-basic
    input: { ... }
    expect:                 # assertions exhaustive and ORDERED; never two
      - output: { ... }     # conflicting expectations in one case
  - id: err-badinput-empty
    input: { ... }
    expect:
      - error: E_BADINPUT   # exercises an error code from the SPEC table
  - id: warn-degraded-…
    input: { ... }
    expect:
      - warning: W_DEGRADED
      - output: { ... }
```

Before implementation, mechanically verify (write a small script — do not
eyeball): the file parses; **every** error/warning code in the SPEC table is
hit by ≥1 case; assertions are ordered and non-conflicting. Where real
corrupted data exists, turn it into a negative fixture — real corruption
beats invented corruption.

---

## `docs/design/decision-log.md` — append-only ledger

```markdown
# Decision log
Append-only. Newest last. When notes conflict, this file wins.

## D1 — <title> — <YYYY-MM-DD>
Decision: <what was decided>.
Approval: "<user's own words>"
Affects: <artifacts / axioms touched>

## D2 — <title> — <YYYY-MM-DD>
...
```

Never edit a past entry to change its meaning; correct it with a new entry
that references the old one.

---

## Provenance `README.md` — one per implementation

Implementations live apart (e.g. `implementations/<component>/`) and each
carries this, so a regenerable implementation is disposable by construction
and says so:

```markdown
# <Component> implementation — <language>
Treatment: regenerable | maintained
Spec version: v<N>            (specs/<component>/SPEC.md)
Contract: tests.yaml v<N> — <M>/<M> cases passing, verified <YYYY-MM-DD>
Generated: <YYYY-MM-DD> by <agent/model>, from SPEC + contract + boundary
           interfaces only (no access to other implementations).

If regenerable: this code may be deleted and regenerated from the spec and
contract above. Do not hand-patch it; fix the spec.
```

---

## Data-project artifacts

When the project handles data, apply the same discipline:

- **Validators** gate ingestion in strict mode with atomic batches — a batch
  is all-or-nothing.
- **Records** are append-only revisions; history is never silently rewritten.
- **Loads are idempotent** and proven so: re-loading identical content must
  report all no-ops.
- **Binary stores are regenerable materialized views** — keep a deterministic,
  sorted, diffable text export in version control and prove the round trip
  (export → rebuild → identical).
