# Sources — the three texts and the tooling landscape

Read this before summarizing or defending the methodology. It distills the
three source texts behind the skill so you can answer from them without
re-researching, and situates the approach against the spec-driven tooling
that shipped in 2026. Cite the primary essays, not this digest, if the user
wants to read further.

The through-line: **when AI makes code cheap, durability has to move out of
the implementation.** The three authors put it in different places — Fowler
in oracles, Breunig in a spec+tests artifact with honest limits, Bergel in a
full artifact set — and the skill is the union of all three, disciplined by
Breunig's failure modes.

---

## 1. Chad Fowler — *The Phoenix Architecture* / *The Deletion Test* (Jan 2026)

Primary: <https://aicoding.leaflet.pub/3md5ftetaes2e> — "Durability through
disposability. When code is cheap, durability comes from regeneration, not
preservation."

Key claims:

- The bottleneck moved from **production to validation**. Generating code is
  cheap; confidence is expensive. Code is a *disposable cache of
  understanding*, not an irreplaceable asset.
- The **deletion test is a diagnostic, not a recommendation.** The question
  is: *"If I deleted this codebase and regenerated it from scratch, what would
  I rely on to decide whether the result was correct?"* If the honest answer
  is "the old code," that code has become an inappropriate single source of
  truth — a design smell, not a fact of life.
- What must survive deletion is not code but the **oracle**: property-based
  tests, contracts, invariants, and operational signals — a mechanical way to
  tell correct from incorrect without consulting implementation history.
- On telemetry: *"Production telemetry can tell you that something changed. It
  rarely tells you whether it should have."* Signals detect drift; they do not
  define correctness.

Memorable lines: *"Code becomes precious when it is the only place knowledge
lives."* / *"When deleting code is boring, regenerating it is safe."*

This is the origin of the skill's **deletion test** and the insistence that a
failed deletion test is a spec bug, not a code virtue. (Distinct from Martin
Fowler's older *PhoenixServer*/immutable-infrastructure pattern, which is the
ancestor idea applied to servers — worth naming if the user conflates them.)

---

## 2. Drew Breunig — *A Software Library with No Code* (Jan 8 2026) + *…SDD Triangle* (Mar 4 2026)

Primary: <https://www.dbreunig.com/2026/01/08/a-software-library-with-no-code.html>
and the follow-up <https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html>.
Simon Willison's writeup is a good secondary: <https://simonwillison.net/2026/Jan/10/a-software-library-with-no-code/>.

The demonstration: **`whenwords`**, a relative-time formatting library
shipped as *no code at all* — a ~500-line `SPEC.md`, a `tests.yaml` of 125
language-agnostic input/output cases, and a 9-line `INSTALL.md` prompt. Five
functions (`timeago`, `duration`, `parse_duration`, `human_date`,
`date_range`); the consumer names a language and the agent regenerates it on
demand. *"There wasn't a single language where Claude couldn't implement
`whenwords` in one shot."* This is the concrete model for the skill's
`SPEC.md` + `tests.yaml` per-component artifact.

**Breunig's five failure modes** — the skill's treatment-decision test for
when code should be **maintained**, not regenerated:

1. **Performance matters** — optimization is hard-won knowledge found by
   profiling and tuning, codified across versions; a spec can't carry it.
2. **Testing complexity explodes** — spec changes cascade unpredictably across
   languages and models. SQLite's ~51,445 tests vs `whenwords`' 125 is the
   scaling problem in one number.
3. **Support & bug replication** — *"Replicating bugs is nearly impossible. If
   the customer gets stuck on an issue with their own generated codebase, how
   do we have a hope of finding the problem?"* Divergent per-user
   implementations defeat debugging.
4. **Continuous updates required** — security patches, new integrations,
   platform drift demand active maintenance (his examples: LiteLLM, Postgres).
5. **Community crystallization** — *"The code we rely on is not just an
   instantiation of a spec … but the product of people and culture that
   crystallize around a goal."*

The follow-up's honest correction, which the skill's "Pitfalls" section
inherits: **"no-code libraries are toys."** Larger projects stalled — *"every
time they fixed a new bug, it broke something else."* His fixes: spec, tests,
and code form a **triangle / feedback loop**, not a pipeline — *"implementing
the code helps us improve our spec"* — kept in sync by capturing decisions at
commit time (his tool, **Plumb**). Constraint: the process must stay
lightweight or it *"just moves the problem somewhere else."* This is exactly
why the skill keeps approval to one gate per component and records decisions
in an append-only log rather than adopting a heavier framework.

---

## 3. Bergel — *The Phoenix Principle: A Manifesto for Programmers in the AI Age*

Primary: <https://medium.com/@bergel/the-phoenix-principle-a-manifesto-for-programmers-in-the-ai-age-ca63317c5ebc>.
Explicitly synthesizes Fowler and Breunig into an artifact set.

Key claims:

- *"Code is ephemeral. Specification is eternal. Tests are truth."* /
  *"Code is now the compilation artifact; specification is the source."* The
  shift is *"from programming IN languages to programming WITH language."*
- The **Symbiont model**: the human owns specification and architectural
  vision; the AI owns implementation and cross-language translation.
- Regenerability is **not uniform** — it names the same limits as Breunig
  (performance, SQLite-scale test surfaces, security patches, community
  investment) as reasons to maintain instead of regenerate.
- Classical framing: axioms → theorems → proofs, the scientific method,
  clinical-trial protocols — domains where the specification outlives every
  implementation.
- Prescribes the artifact set the skill uses: **AXIOMS.md, SPEC.md,
  tests.yaml, ARCHITECTURE.md**, plus regeneration instructions.

Caveat when citing: the manifesto is grand and self-consciously
demonstrative (it notes it was co-written with an AI and could itself be
deleted because "the principle survives"). Treat it as the naming and
framing source; lean on Fowler for the diagnostic and Breunig for the
empirical limits.

---

## Tooling landscape — and why this skill hand-rolls artifacts

Spec-driven development tooling that shipped around 2026 splits into two
camps:

- **Feature-workflow frameworks** — *GitHub Spec Kit* and *AWS Kiro* generate
  per-feature spec/design/task files as **change artifacts** inside an app
  team's branch-and-ship loop. Specs are scaffolding for a feature and are
  consumed by it.
- **Regenerative / spec-as-source platforms** — *Codeplain* ("code should be
  regenerated, not maintained"), Breunig's own *Plumb* (keeps the spec/tests/
  code triangle in sync by extracting and approving decisions at commit
  time), and other commercial spec-centric entrants (e.g. Tessl). These treat
  the spec as the durable source.

The skill's stance: those frameworks fit **feature-driven app teams**, not
**long-lived single-maintainer systems**. For the latter, hand-rolled
artifacts that compound into durable system documentation serve better than
per-feature specs that are born and discarded with a branch — you want the
spec to *outlive* features, not track them. Recommend a tool only if the user
is on a team already living in that tool's loop; otherwise the `AXIOMS.md /
SPEC.md / tests.yaml / decision-log.md` set in `templates.md` is the
lighter-weight, more durable choice. Whatever the tool, Breunig's lightweight
constraint holds: if the process costs more than it saves, it has just moved
the problem.
