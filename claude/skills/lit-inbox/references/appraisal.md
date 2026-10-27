# appraisal.md: Tier 2 frameworks (load only for Tier 2 and upgrades to Tier 2)

Contents: §1 critical appraisal · §2 reproducibility · §3 idea quality bar.

Ground every statement in text you actually read. Say "no major concerns" or "not stated in
the paper" when that is the honest result; never invent a weakness to fill a section, and
never soften a real one. Respect the config's appraisal depth.

---

## 1. Critical-appraisal framework

Adapted from `scientific-critical-thinking`. Skim these lenses and surface only the flags that
genuinely apply. Output: 2 to 5 flags, or "No major concerns — sound within its scope."
Name each issue precisely, for example "causal claim from correlational field data".

- **Design and validity.** Does the design support the causal claims made? Are confounders
  controlled? For geophysical field data: coverage, sensor coupling, noise, and whether the
  inversion is constrained enough for the interpretation drawn.
- **Statistics.** Sample size and power; correlation used as causation; uncorrected multiple
  comparisons; effect sizes and uncertainty reported (error bars, confidence intervals) or
  only p-values; whether stated uncertainties propagate to the headline numbers.
- **Bias.** Selection or sampling bias; p-hacking or post-hoc hypotheses presented as
  planned; cherry-picked evidence; contradictory findings ignored.
- **Claim versus data.** Do the conclusions follow from what was shown, or do they overreach
  (overgeneralized, extrapolated beyond the data, mechanism claimed without mechanistic
  evidence)?

Record page anchors for flags where practical, for example `(p. 8)`.

---

## 2. Reproducibility framework (reuse-focused, not an accept/reject verdict)

Adapted from `peer-review`.

- **Data:** deposited and available (repository, DOI, accession numbers), available on
  request, or absent?
- **Code:** shared (GitHub, Zenodo, supplement)? Are software, versions and parameters
  stated?
- **Methods:** detailed enough to re-run or adapt the workflow?
- **Reuse verdict:** one line stating whether Dylan could reuse the data, code or method in
  his work, and how.

---

## 3. Idea quality bar (for research-idea notes)

Adapted from `hypothesis-generation`. An idea earns a note only if it is:

- **Mechanistic:** proposes how or why, not just "someone should study X".
- **Testable and falsifiable:** carries a concrete prediction that could come out either way.
- **Distinguishable:** adds a new angle, scale, method or application (ideally tied to the
  geophysics and NGI context), and is not the paper's own future-work section restated.
- **Grounded:** traces back to something specific the paper showed.

If fewer ideas than the config's count meet the bar, seed fewer. Zero is acceptable.
