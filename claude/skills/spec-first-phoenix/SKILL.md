---
name: spec-first-phoenix
description: Apply the Phoenix/spec-first development methodology — durable specifications, language-agnostic test contracts, and regenerable implementations — to software and data projects. Use this skill whenever the user mentions spec-first or spec-driven development, the Phoenix architecture or Phoenix principle, the deletion test, regenerable vs maintained code, AXIOMS/SPEC/test-contract artifacts, wanting specs that outlive code, structuring a project for AI-assisted development, or asks how to start or restructure a project so implementations can be safely deleted and regenerated — even if they never name the methodology explicitly.
---

# Spec-first ("Phoenix") development

The premise: with AI generation, code is cheap and confidence is expensive.
Durability moves out of implementations and into four things — behavioral
specifications, executable test contracts, interface boundaries, and
provenance. A well-run project passes the **deletion test**: if the
implementation of a component were deleted, a competent implementer given
only its SPEC and test contract would regenerate an equivalent passing one.
If the honest answer is "we'd need the old code," the spec is incomplete —
fix the spec, not the code.

Read `references/sources.md` before summarizing or defending the
methodology to the user — it distills the three source texts (Fowler,
Breunig, Bergel) with their key claims and the tooling landscape, so you
do not need to research them. Read `references/templates.md` when creating
any of the artifacts below — it has skeletons and conventions.

## The durable artifact set

- `AXIOMS.md` — the constitution: non-negotiable principles and how they
  change. Phrase prohibitions as "don't X, because Y; instead Z" —
  implementation agents reliably ignore bare prohibitions but respect
  explained ones.
- `ARCHITECTURE.md` — components, boundaries, cross-component invariants,
  and a **treatment table** declaring each component regenerable or
  maintained, with the reasoning.
- `specs/<component>/SPEC.md` + `tests.yaml` — one behavioral spec and one
  language-agnostic test contract per component, plus any normative data
  files (vocabularies, registries, policies) the contract references.
- `docs/design/decision-log.md` — an append-only ledger of numbered
  decisions (D1, D2, …), newest last. Every approval, scope change, and
  amendment lands here; when notes conflict, the log wins.

Implementations live apart (e.g. `implementations/<component>/`) and each
carries a provenance README: spec version, contract pass count, generation
date, declared treatment. Regenerable implementations are disposable by
construction; the README says so.

## The treatment decision — never uniform

Do not apply the regenerable treatment to everything because it is the
project's philosophy; argue each component from Breunig's failure modes.
A component should be **maintained** (durable code, spec'd anyway) when any
of these hold: performance knowledge is discoverable only by profiling or
field use; the test surface is too large to enumerate; bugs must be
reproduced against specific operational states; it adapts continuously to
changing external interfaces (providers, APIs, formats); or its value
depends on a shared reference implementation. Everything else — pure data
contracts, validators, parsers, planners, format mappers — is a
**regenerable** candidate.

The split can occur *inside* one component: a URL-construction layer can
be regenerable (pure function, enumerable tests) while the transport layer
that fetches those URLs is maintained (live auth, rate limits, provider
drift). Declare both halves explicitly.

Maintained code still gets a contract: pin its enumerable core (state
machines, invariants) with the same language-agnostic tests, framed as a
regression net rather than a complete definition of correctness. Document
explicitly which requirements are NOT contract-testable (transactionality,
corrupt-store handling) and require implementation-level tests for them,
so those requirements are recorded rather than lost.

## The working loop

1. **Read the existing project first.** Survey prior art before proposing
   anything; generalize established vocabulary and conventions rather than
   replacing them. Deviations require a logged decision.
2. **Interview in small batches.** Ask 3–4 focused questions at a time,
   record each answer as a numbered decision immediately. Do not move to
   artifacts until scope, consumers, and operational model are decided.
3. **Constitution first, then one component at a time.** Draft AXIOMS.md,
   get explicit approval, and record it. Then, for the component the user
   picks: clarify batch → SPEC + contract draft → **written approval
   before any implementation** (the gate applies to regenerable and
   maintained components alike). Mark every artifact's status line
   (DRAFT/APPROVED vN + decision reference) and bump contract meta headers
   at approval — they are easy to forget.
4. **Make contracts airtight before implementation.** Mechanically verify:
   the contract parses; every error and warning code in the SPEC is
   exercised by at least one case (write a small script; do not eyeball);
   assertions are exhaustive and ordered — never two conflicting
   expectations in one case; fixtures are frozen *inside* the contract
   (embedded test registries/policies) so the contract cannot drift when
   live configuration evolves. Where real corrupted data exists, turn it
   into negative fixtures — real corruption beats invented corruption.
5. **Implement deletion-test style.** Give a fresh agent (or fresh
   session) ONLY the SPEC, the contract, and declared boundary interfaces
   — no access to other implementations. Iterate until the contract is
   fully green. Require the implementer to REPORT spec ambiguities with
   its chosen reading, and forbid it from editing specs or tests: if a
   test seems wrong, that is a finding for the maintainer, not a thing to
   fix silently.
6. **Verify independently.** Re-run every contract yourself after
   delivery; never take the implementer's word. When two components were
   built independently against a shared contract (e.g., a validator and a
   producer of records), run one against the other's output — agreement
   through the spec alone is the strongest evidence the methodology is
   working.
7. **Treat data with the same discipline.** Validators gate ingestion
   (strict mode, atomic batches); records are append-only revisions so
   history is never silently rewritten; loads are idempotent and proven so
   (re-load of identical content must report all no-ops); binary stores
   are regenerable materialized views — keep deterministic, sorted,
   diffable text exports in version control and prove the round trip.

## Governance habits that keep it honest

Changes to any approved spec or normative data file require a decision-log
entry. Approvals quote the user's words. When you make a mistake in a
durable artifact, repair it visibly with a note, and record it — an
append-only log that hides its own errors is not append-only. Science- or
policy-laden defaults (thresholds, radii, priorities) belong in tunable
data files reviewed explicitly by the domain owner, not buried in spec
prose: flag them as drafted judgment, never as established fact.

## Pitfalls observed in the field

A vague spec produces implementations that are wrong in unpredictable
ways; specificity is the entire cost of admission. Trendy spec-frameworks
(per-feature branches, specs-as-change-artifacts) fit feature-driven app
teams, not long-lived single-maintainer systems — hand-rolled artifacts
that compound into system documentation usually serve better; see
`references/sources.md` for the tooling comparison. Expect implementation
agents to surface genuine spec gaps (code collisions between error types,
ordering of validation stages); treat each reported ambiguity as a future
spec amendment, and record it. And keep the human's approval cadence
light: one gate per component, small question batches, everything else
proceeding without ceremony.