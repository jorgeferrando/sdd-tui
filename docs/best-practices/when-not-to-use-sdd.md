# When Not to Use SDD

SDD adds value when a change is complex enough to benefit from a documented proposal, spec, and design. For small, routine changes, the ceremony adds friction without payoff.

---

## Cases where SDD is overkill

### Hotfixes

A production bug that needs to be fixed in the next 30 minutes is not the time for a proposal and spec review.

**Do instead:** Fix it, commit with a clear message, merge. If the fix reveals a systemic issue, open an SDD change for the root cause.

---

### Config-only changes

Updating environment variables, CI workflow tweaks, dependency version bumps, or `.gitignore` additions don't need a spec.

**Do instead:** Commit directly with a descriptive message. If the config change is part of a larger feature, include it in that feature's `tasks.md`.

---

### Obvious < 3 file patches

If the change is "add one field to a form and its test" and the design is unambiguous, the overhead of proposal + spec + design + tasks > the value of the documentation.

**Rule of thumb:** If you can explain the change in one sentence and it touches ≤ 2 files, skip SDD.

---

### Exploratory / throwaway work

Prototypes, spikes, and experiments aren't candidates for SDD — they may be discarded entirely. Run the experiment first, and if it proves the approach, *then* open a proper change to implement it cleanly.

---

### Pure refactors with no behavior change

Renaming variables, extracting a method, reorganizing imports — these don't change behavior and don't benefit from a spec. They may benefit from `tasks.md` if the scope is large, but the full ceremony is unnecessary.

---

## The real question

Ask: *"Would I want to find this decision in the archive six months from now?"*

- New feature → yes → use SDD
- Bug fix with architectural implications → yes → use SDD
- Typo in a comment → no → commit directly
- Dependency bump → no → commit directly
- New integration with a third-party service → yes → use SDD

---

## When in doubt, start with a proposal

If you're not sure whether a change warrants SDD, write a `proposal.md` in 5 minutes. If the proposal is trivial ("update X to Y, no alternatives, no decisions"), that's a signal to skip the rest. If it surfaces real decisions, the ceremony is worth it.
